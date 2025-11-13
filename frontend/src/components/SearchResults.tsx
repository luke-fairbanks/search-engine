import React from 'react';
import { Card, CardBody, Link, Chip, Skeleton } from '@nextui-org/react';
import { SearchResponse } from '../types/SearchTypes';

interface SearchResultsProps {
  results: SearchResponse;
  loading?: boolean;
  query: string;
}

const SearchResults: React.FC<SearchResultsProps> = ({ results, loading = false, query }) => {
  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <Card key={i} className="bg-slate-800/50 border border-slate-700/50 backdrop-blur-sm">
            <CardBody className="space-y-3">
              <Skeleton className="w-3/5 rounded-lg">
                <div className="h-6 rounded-lg bg-slate-700"></div>
              </Skeleton>
              <Skeleton className="w-2/5 rounded-lg">
                <div className="h-4 rounded-lg bg-slate-700"></div>
              </Skeleton>
              <Skeleton className="w-full rounded-lg">
                <div className="h-4 rounded-lg bg-slate-700"></div>
              </Skeleton>
              <Skeleton className="w-4/5 rounded-lg">
                <div className="h-4 rounded-lg bg-slate-700"></div>
              </Skeleton>
            </CardBody>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div>
      {/* Results list */}
      <div className="space-y-4">
        {results.results.map((result, index) => (
          <Card
            key={index}
            className="bg-slate-800/60 border border-slate-700/40 backdrop-blur-xl hover:bg-slate-800/80 hover:border-slate-600/60 hover:shadow-2xl hover:shadow-blue-500/10 transition-all duration-300 group"
          >
            <CardBody className="p-6">
              {/* Result Title */}
              <Link
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-start gap-2 group/link mb-2"
              >
                <h3 className="text-xl font-semibold text-blue-400 group-hover/link:text-blue-300 transition-colors flex-1">
                  {result.title}
                </h3>
                <svg className="w-4 h-4 text-slate-500 group-hover/link:text-blue-400 mt-1 flex-shrink-0 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </Link>

              {/* URL */}
              <p className="text-emerald-400 text-sm mb-3 truncate font-mono">
                {result.url}
              </p>

              {/* Snippet */}
              <p className="text-slate-300 text-sm leading-relaxed mb-4">
                {result.snippet}...
              </p>

              {/* Metadata - Elevated micro-layer */}
              <div className="flex items-center gap-2 flex-wrap">
                <Chip
                  size="sm"
                  variant="flat"
                  className="bg-blue-500/20 text-blue-300 border border-blue-500/30 shadow-lg shadow-blue-500/10"
                >
                  Relevance: {result.score.toFixed(2)}
                </Chip>
                <Chip
                  size="sm"
                  variant="flat"
                  className="bg-slate-700/50 text-slate-300 border border-slate-600/50"
                >
                  {result.length} words
                </Chip>
              </div>
            </CardBody>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default SearchResults;
