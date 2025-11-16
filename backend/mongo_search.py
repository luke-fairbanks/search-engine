#!/usr/bin/env python3
"""
MongoDB-based search engine
Provides BM25 + PageRank hybrid ranking using MongoDB as the data source
"""

import math
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import Counter
from pymongo import MongoClient

TOKEN_RE = re.compile(r"[A-Za-z0-9]+")

def tokenize(s: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric tokens"""
    return [t.lower() for t in TOKEN_RE.findall(s)]

@dataclass
class Document:
    url: str
    title: str
    length: int
    snippet: str

class MongoSearchEngine:
    """Search engine using MongoDB as the data source"""

    def __init__(self, mongo_uri: str = 'mongodb://localhost:27017/', db_name: str = 'crawler_db'):
        """Initialize MongoDB connection and build index cache"""
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db.crawled_pages

        # Cache for search index
        self.index_cache = None
        self.last_doc_count = 0

    def _build_index(self, force_rebuild: bool = False):
        """Build or rebuild the search index from MongoDB"""
        current_count = self.collection.count_documents({})

        # Use cache if available and doc count hasn't changed
        if not force_rebuild and self.index_cache and self.last_doc_count == current_count:
            return self.index_cache

        print(f"Building search index from {current_count} documents...")

        # Fetch all documents
        docs = list(self.collection.find({}, {
            'url': 1,
            'title': 1,
            'text': 1,
            'snippet': 1,
            'links': 1,
            '_id': 0
        }))

        if not docs:
            return None

        # Build document list
        doc_list = []
        doc_tokens = []
        doc_lengths = {}
        url_to_idx = {}

        for i, doc in enumerate(docs):
            url = doc.get('url', '')
            title = doc.get('title', 'Untitled')
            text = doc.get('text', '')
            snippet = doc.get('snippet', '')[:200]

            # Use full text if available, otherwise fall back to snippet
            content = text if text else snippet

            # Tokenize title and full text content (or snippet as fallback)
            tokens = tokenize(f"{title} {content}")

            # Generate snippet from text if not provided
            if not snippet and text:
                snippet = text[:200]

            doc_list.append(Document(
                url=url,
                title=title,
                length=len(tokens),
                snippet=snippet
            ))
            doc_tokens.append(tokens)
            doc_lengths[i] = len(tokens)
            url_to_idx[url] = i

        # Calculate average document length
        avgdl = sum(doc_lengths.values()) / len(doc_lengths) if doc_lengths else 0

        # Build inverted index and calculate IDF
        inverted_index = {}
        for doc_idx, tokens in enumerate(doc_tokens):
            token_counts = Counter(tokens)
            for token, count in token_counts.items():
                if token not in inverted_index:
                    inverted_index[token] = []
                inverted_index[token].append((doc_idx, count))

        # Calculate IDF scores
        N = len(doc_list)
        idf = {}
        for term, postings in inverted_index.items():
            df = len(postings)
            idf[term] = math.log((N - df + 0.5) / (df + 0.5) + 1.0)

        # Build simple PageRank (based on link structure)
        pagerank = self._calculate_pagerank(docs, url_to_idx)

        self.index_cache = {
            'docs': doc_list,
            'doclen': doc_lengths,
            'avgdl': avgdl,
            'idf': idf,
            'inverted_index': inverted_index,
            'pagerank': pagerank
        }
        self.last_doc_count = current_count

        print(f"✓ Index built: {N} docs, {len(idf)} unique terms, avgdl={avgdl:.1f}")
        return self.index_cache

    def _calculate_pagerank(self, docs: List[dict], url_to_idx: Dict[str, int], iterations: int = 20, damping: float = 0.85) -> Dict[int, float]:
        """Calculate PageRank scores"""
        N = len(docs)
        if N == 0:
            return {}

        # Build adjacency list
        outlinks = {i: [] for i in range(N)}
        for i, doc in enumerate(docs):
            links = doc.get('links', [])
            for link in links:
                if link in url_to_idx:
                    target_idx = url_to_idx[link]
                    if target_idx != i:  # No self-links
                        outlinks[i].append(target_idx)

        # Initialize PageRank
        pr = {i: 1.0 / N for i in range(N)}

        # Power iteration
        for _ in range(iterations):
            new_pr = {}
            for i in range(N):
                rank_sum = sum(pr[j] / len(outlinks[j]) for j in range(N) if i in outlinks[j] and len(outlinks[j]) > 0)
                new_pr[i] = (1 - damping) / N + damping * rank_sum
            pr = new_pr

        return pr

    def search(self, query: str, alpha: float = 0.2, beta: float = 0.8, k: int = 10, title_boost: float = 0.5) -> List[Tuple[Document, float]]:
        """
        Hybrid search using BM25 and PageRank

        Args:
            query: Search query string
            alpha: Floor weight (default 0.2)
            beta: PageRank weight (default 0.8)
            k: Number of results to return (default 10)
            title_boost: Bonus multiplier for title/URL matches (default 0.5)

        Returns:
            List of (Document, score) tuples
        """
        # Build/refresh index
        idx = self._build_index()
        if not idx:
            return []

        # Tokenize query
        qterms = tokenize(query)
        if not qterms:
            return []

        # BM25 parameters
        k1 = 1.5
        b = 0.75

        # Calculate BM25 scores
        bm25_scores = {}
        for doc_idx in range(len(idx['docs'])):
            score = 0.0
            for term in qterms:
                if term not in idx['inverted_index']:
                    continue

                # Find term frequency in this document
                tf = 0
                for posting_doc_idx, posting_tf in idx['inverted_index'][term]:
                    if posting_doc_idx == doc_idx:
                        tf = posting_tf
                        break

                if tf == 0:
                    continue

                # BM25 formula
                idf_score = idx['idf'].get(term, 0)
                doc_len = idx['doclen'][doc_idx]
                avgdl = idx['avgdl']

                numerator = tf * (k1 + 1)
                denominator = tf + k1 * (1 - b + b * (doc_len / avgdl))
                score += idf_score * (numerator / denominator)

            if score > 0:
                bm25_scores[doc_idx] = score

        if not bm25_scores:
            return []

        # Normalize PageRank
        pr_values = list(idx['pagerank'].values())
        pr_min = min(pr_values) if pr_values else 0.0
        pr_max = max(pr_values) if pr_values else 1.0
        pr_range = pr_max - pr_min

        def pr_norm(doc_idx):
            if pr_range < 1e-12:
                return 0.0
            return (idx['pagerank'].get(doc_idx, 0.0) - pr_min) / pr_range

        # Calculate title match bonus
        def title_match_score(doc_idx):
            doc = idx['docs'][doc_idx]
            title_lower = doc.title.lower()
            url_lower = doc.url.lower()
            title_tokens = set(tokenize(title_lower))

            matches = 0
            for qt in qterms:
                if qt in title_tokens:
                    matches += 1
                elif any(qt in token for token in title_tokens):
                    matches += 0.8
                elif qt in url_lower:
                    matches += 0.6

            if matches == 0:
                return 0.0
            return title_boost * (matches / len(qterms))

        # Combine scores
        final_scores = {}
        for doc_idx, bm_score in bm25_scores.items():
            pr_score = pr_norm(doc_idx)
            title_score = title_match_score(doc_idx)
            final_scores[doc_idx] = bm_score * (alpha + beta * pr_score + title_score)

        # Sort and return top k
        top_results = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:k]
        return [(idx['docs'][doc_idx], score) for doc_idx, score in top_results]

    def get_stats(self) -> dict:
        """Get statistics about the search index"""
        idx = self._build_index()
        if not idx:
            return {
                'total_docs': 0,
                'avg_doc_length': 0,
                'vocab_size': 0
            }

        return {
            'total_docs': len(idx['docs']),
            'avg_doc_length': idx['avgdl'],
            'vocab_size': len(idx['idf'])
        }

    def get_suggestions(self, prefix: str, limit: int = 8) -> List[str]:
        """Get search suggestions based on query prefix with fuzzy matching"""
        idx = self._build_index()
        if not idx:
            return []

        prefix_lower = prefix.lower()
        # Remove spaces and special chars for fuzzy matching
        prefix_normalized = ''.join(c for c in prefix_lower if c.isalnum())

        # Find matching terms in vocabulary
        matching_terms = []
        for term in idx['idf'].keys():
            # Exact prefix match
            if term.startswith(prefix_lower):
                matching_terms.append((term, 0))  # Priority 0 (highest)
            # Match without spaces (e.g., "for loops" -> "forloops")
            elif len(prefix_normalized) >= 3 and term.startswith(prefix_normalized):
                matching_terms.append((term, 1))  # Priority 1
            # Contains the prefix
            elif prefix_lower in term and len(prefix_lower) >= 3:
                matching_terms.append((term, 2))  # Priority 2
            # Fuzzy match - all characters present in order
            elif len(prefix_normalized) >= 3 and self._fuzzy_match(prefix_normalized, term):
                matching_terms.append((term, 3))  # Priority 3

        # Sort by priority, then by IDF score (lower IDF = more common = better)
        matching_terms.sort(key=lambda x: (x[1], idx['idf'].get(x[0], float('inf'))))
        term_suggestions = [term for term, _ in matching_terms[:limit * 2]]

        # Also get matching document titles with fuzzy matching
        title_suggestions = []
        for doc in idx['docs']:
            title_lower = doc.title.lower()
            title_normalized = ''.join(c for c in title_lower if c.isalnum())

            # Check if prefix matches title (with or without spaces)
            if (prefix_lower in title_lower or
                (len(prefix_normalized) >= 3 and prefix_normalized in title_normalized)):
                if title_lower not in title_suggestions:
                    title_suggestions.append(title_lower)
                    if len(title_suggestions) >= limit // 2:
                        break

        # Combine term suggestions and title suggestions
        all_suggestions = []
        seen = set()

        # Add title-based suggestions first (more specific)
        for title in title_suggestions:
            if title not in seen:
                all_suggestions.append(title)
                seen.add(title)

        # Add term-based suggestions
        for term in term_suggestions:
            if term not in seen and len(all_suggestions) < limit:
                all_suggestions.append(term)
                seen.add(term)

        return all_suggestions[:limit]

    def _fuzzy_match(self, pattern: str, text: str) -> bool:
        """Check if all characters in pattern appear in text in order"""
        pattern_idx = 0
        for char in text:
            if pattern_idx < len(pattern) and char == pattern[pattern_idx]:
                pattern_idx += 1
        return pattern_idx == len(pattern)

    def close(self):
        """Close MongoDB connection"""
        self.client.close()
