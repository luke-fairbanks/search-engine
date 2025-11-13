export interface SearchResult {
  url: string;
  title: string;
  snippet: string;
  score: number;
  length: number;
}

export interface SearchResponse {
  query: string;
  total: number;
  results: SearchResult[];
}

export interface IndexStats {
  total_docs: number;
  avg_doc_length: number;
  vocab_size: number;
}
