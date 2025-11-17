#!/usr/bin/env python3
"""
Polling-based crawler for Vercel serverless functions
Stores job state in MongoDB for persistence across function invocations
"""

import asyncio
import time
import uuid
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from collections import deque
from bs4 import BeautifulSoup
import aiohttp

class CrawlerJobManager:
    """Manages crawler jobs using MongoDB for state persistence"""
    
    def __init__(self, mongo_client, db_name='crawler_db'):
        self.db = mongo_client[db_name]
        self.jobs_collection = self.db.crawler_jobs
        self.pages_collection = self.db.crawled_pages
    
    async def create_job(self, start_url, max_depth=2, max_pages=50):
        """Create a new crawler job"""
        job_id = str(uuid.uuid4())
        job = {
            'job_id': job_id,
            'start_url': start_url,
            'max_depth': max_depth,
            'max_pages': max_pages,
            'status': 'pending',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'stats': {
                'total_pages': 0,
                'completed_pages': 0,
                'queue_size': 1,
                'duration': 0
            },
            'queue': [{'url': start_url, 'depth': 0, 'parent': None}],
            'visited': [],
            'nodes': []
        }
        await self.jobs_collection.insert_one(job)
        return job_id
    
    async def get_job(self, job_id):
        """Get job status"""
        return await self.jobs_collection.find_one({'job_id': job_id})
    
    async def process_job_batch(self, job_id, batch_size=5, timeout=8):
        """Process a batch of URLs from the job queue (time-limited for serverless)"""
        job = await self.get_job(job_id)
        if not job:
            return {'error': 'Job not found'}
        
        if job['status'] == 'completed':
            return job
        
        # Mark as running
        await self.jobs_collection.update_one(
            {'job_id': job_id},
            {'$set': {'status': 'running', 'updated_at': datetime.utcnow()}}
        )
        
        start_time = time.time()
        processed = 0
        
        async with aiohttp.ClientSession() as session:
            while job['queue'] and processed < batch_size:
                # Check timeout (leave 2s buffer for cleanup)
                if time.time() - start_time > timeout:
                    break
                
                # Stop if max pages reached
                if len(job['visited']) >= job['max_pages']:
                    break
                
                # Get next URL from queue
                current = job['queue'].pop(0)
                url = current['url']
                depth = current['depth']
                parent = current['parent']
                
                # Skip if already visited
                if url in job['visited']:
                    continue
                
                job['visited'].append(url)
                
                # Add node as crawling
                node = {
                    'url': url,
                    'depth': depth,
                    'status': 'crawling',
                    'parent': parent
                }
                job['nodes'].append(node)
                
                # Crawl the page
                try:
                    page_data, links = await self._crawl_page(url, depth, session, job['start_url'])
                    
                    if page_data:
                        # Update node status
                        job['nodes'][-1].update({
                            'status': 'completed',
                            'title': page_data['title'],
                            'linkCount': len(links)
                        })
                        
                        # Save to pages collection
                        await self._save_page(url, page_data, depth, parent, job['start_url'])
                        
                        # Add new links to queue
                        if depth < job['max_depth']:
                            for link in links[:10]:  # Limit links per page
                                if link not in job['visited'] and len(job['queue']) < 100:
                                    job['queue'].append({
                                        'url': link,
                                        'depth': depth + 1,
                                        'parent': url
                                    })
                    else:
                        job['nodes'][-1]['status'] = 'error'
                        
                except Exception as e:
                    job['nodes'][-1]['status'] = 'error'
                    print(f"Error crawling {url}: {e}")
                
                processed += 1
        
        # Update stats
        duration = time.time() - start_time
        job['stats'].update({
            'total_pages': len(job['visited']),
            'completed_pages': len([n for n in job['nodes'] if n['status'] == 'completed']),
            'queue_size': len(job['queue']),
            'duration': job['stats']['duration'] + duration
        })
        
        # Check if job is complete
        if not job['queue'] or len(job['visited']) >= job['max_pages']:
            job['status'] = 'completed'
        else:
            job['status'] = 'pending'
        
        # Save job state
        await self.jobs_collection.update_one(
            {'job_id': job_id},
            {
                '$set': {
                    'status': job['status'],
                    'updated_at': datetime.utcnow(),
                    'stats': job['stats'],
                    'queue': job['queue'],
                    'visited': job['visited'],
                    'nodes': job['nodes']
                }
            }
        )
        
        return job
    
    async def _crawl_page(self, url, depth, session, base_url):
        """Crawl a single page"""
        try:
            async with session.get(url, timeout=5) as response:
                if response.status != 200:
                    return None, []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract title
                title = soup.find('title')
                title_text = title.string.strip() if title else url
                
                # Remove script and style elements
                for script in soup(['script', 'style', 'noscript']):
                    script.decompose()
                
                # Get limited text content
                text = soup.get_text()[:5000]
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                full_text = ' '.join(chunk for chunk in chunks if chunk)[:5000]
                
                # Extract snippet
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                snippet = meta_desc.get('content', '')[:200] if meta_desc else full_text[:200]
                
                # Extract links (limit to 20)
                links = []
                for link in soup.find_all('a', href=True)[:20]:
                    absolute_url = urljoin(url, link['href'])
                    if self._is_valid_url(absolute_url, base_url):
                        links.append(absolute_url)
                
                return {
                    'title': title_text,
                    'text': full_text,
                    'snippet': snippet
                }, links
                
        except Exception as e:
            print(f"Error crawling {url}: {e}")
            return None, []
    
    def _is_valid_url(self, url, base_url):
        """Check if URL is valid and belongs to same domain"""
        try:
            parsed = urlparse(url)
            base_parsed = urlparse(base_url)
            return (
                parsed.scheme in ('http', 'https') and
                parsed.netloc == base_parsed.netloc
            )
        except:
            return False
    
    async def _save_page(self, url, page_data, depth, parent, start_url):
        """Save page to MongoDB"""
        try:
            existing = await self.pages_collection.find_one({'url': url})
            if not existing:
                await self.pages_collection.insert_one({
                    'url': url,
                    'title': page_data['title'],
                    'text': page_data['text'],
                    'snippet': page_data['snippet'],
                    'depth': depth,
                    'parent_url': parent,
                    'crawled_at': datetime.utcnow(),
                    'start_url': start_url
                })
        except Exception as e:
            print(f"Error saving page {url}: {e}")
    
    async def cleanup_old_jobs(self, days=7):
        """Clean up old completed jobs"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        await self.jobs_collection.delete_many({
            'status': 'completed',
            'updated_at': {'$lt': cutoff}
        })
