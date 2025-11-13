import React, { useState, useEffect } from 'react';
import { Chip, Pagination } from '@nextui-org/react';
import { motion } from 'framer-motion';
import SearchBox from './SearchBox';
import SearchResults from './SearchResults';
import { searchApi } from '../services/api';
import { SearchResponse, IndexStats } from '../types/SearchTypes';

const RESULTS_PER_PAGE = 10;

const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<IndexStats | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [searchTime, setSearchTime] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState(1);

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      return;
    }

    setLoading(true);
    setError(null);
    setQuery(searchQuery);
    setHasSearched(true);
    setCurrentPage(1);

    const startTime = performance.now();

    try {
      const response = await searchApi.search(searchQuery, 500); // Fetch 500 results for pagination
      const endTime = performance.now();
      setSearchTime((endTime - startTime) / 1000);
      setResults(response);
    } catch (err: any) {
      setError(err.response?.data?.error || 'An error occurred while searching');
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  // Read initial state from URL on mount
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const urlQuery = urlParams.get('q');
    const urlPage = urlParams.get('page');

    if (urlQuery) {
      if (urlPage) {
        setCurrentPage(parseInt(urlPage, 10) || 1);
      }
      // Trigger search with URL query
      handleSearch(urlQuery);
    }

    // Load index stats on mount
    searchApi.getStats()
      .then(setStats)
      .catch(err => console.error('Failed to load stats:', err));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Update URL when query or page changes
  useEffect(() => {
    if (hasSearched && query) {
      const params = new URLSearchParams();
      params.set('q', query);
      if (currentPage > 1) {
        params.set('page', currentPage.toString());
      }
      const newUrl = `${window.location.pathname}?${params.toString()}`;
      window.history.pushState({}, '', newUrl);
    }
  }, [query, currentPage, hasSearched]);

  // Get paginated results
  const paginatedResults = results ? {
    ...results,
    results: results.results.slice(
      (currentPage - 1) * RESULTS_PER_PAGE,
      currentPage * RESULTS_PER_PAGE
    )
  } : null;

    const totalPages = results ? Math.ceil(results.results.length / RESULTS_PER_PAGE) : 0;

  return (
    <div className={`bg-gradient-to-br from-gray-900 via-slate-900 to-gray-950 flex flex-col ${hasSearched ? 'min-h-screen' : 'h-[calc(100vh-4rem)]'}`}>
      {/* Search Box - Animated Container */}
      <motion.div
        className={`w-full ${hasSearched ? 'sticky top-16 z-10 bg-slate-900/20 backdrop-blur-xl border-b border-slate-700/50 shadow-2xl' : 'z-10'}`}
        initial={false}
        animate={{
          marginTop: hasSearched ? '0rem' : '30vh',
          paddingTop: hasSearched ? '1rem' : '0rem',
          paddingBottom: hasSearched ? '1rem' : '0rem',
        }}
        transition={{
          type: "spring",
          stiffness: 120,
          damping: 25,
          mass: 0.8
        }}
      >
        <div className="max-w-screen-lg w-full mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div className="w-full">
            <motion.div
              className="text-center overflow-hidden"
              initial={{ opacity: 1, maxHeight: '300px' }}
              animate={{
                opacity: hasSearched ? 0 : 1,
                maxHeight: hasSearched ? '0px' : '300px',
                marginBottom: hasSearched ? '0px' : '3rem'
              }}
              transition={{
                duration: 0.4,
                ease: "easeInOut"
              }}
            >
              <h2 className="text-6xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4 drop-shadow-2xl">
                Search the Web
              </h2>
              <p className="text-lg text-slate-400">
                Powered by BM25 ranking and PageRank algorithm
              </p>
            </motion.div>
            <SearchBox onSearch={handleSearch} loading={loading} initialQuery={query} hasSearched={hasSearched} />
          </motion.div>
        </div>
      </motion.div>

      <div className="max-w-screen-lg w-full mx-auto px-4 sm:px-6 lg:px-8 flex-1">
        {/* Stats Bar - Show after search */}
        {!hasSearched && stats && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.2 }}
            className="mt-4 mb-6 flex gap-2 justify-center"
          >
            <Chip
              size="sm"
              variant="flat"
              className="bg-blue-500/20 text-blue-300 border border-blue-500/30"
            >
              {stats.total_docs.toLocaleString()} docs
            </Chip>
            <Chip
              size="sm"
              variant="flat"
              className="bg-purple-500/20 text-purple-300 border border-purple-500/30"
            >
              {stats.vocab_size.toLocaleString()} terms
            </Chip>
          </motion.div>
        )}

        {/* Error Message - Layer 2 */}
        {error && (
          <div className="mt-6 p-4 bg-red-900/30 border border-red-500/50 rounded-xl backdrop-blur-sm shadow-xl shadow-red-900/20">
            <p className="text-red-300">{error}</p>
          </div>
        )}

        {/* Search Results */}
        {paginatedResults && (
          <div className="mt-8 mb-12">
            {/* Search Info - Subtle Layer */}
            <div className="mb-6 flex items-center justify-between px-2">
              <p className="text-slate-400 text-sm">
                About <strong className="text-slate-200">{results?.results.length.toLocaleString()}</strong> results
                <span className="text-slate-500"> ({searchTime.toFixed(2)} seconds)</span>
              </p>
              {totalPages > 1 && (
                <p className="text-slate-500 text-sm">
                  Page <span className="text-slate-300">{currentPage}</span> of {totalPages}
                </p>
              )}
            </div>

            <SearchResults results={paginatedResults} loading={loading} query={query} />

            {/* Pagination - Elevated Layer */}
            {totalPages > 1 && (
              <div className="mt-8 flex justify-center">
                <Pagination
                  total={totalPages}
                  page={currentPage}
                  onChange={setCurrentPage}
                  showControls
                  color="primary"
                  size="lg"
                  classNames={{
                    wrapper: "gap-2",
                    item: "bg-slate-800/50 border border-slate-700/50 text-slate-300 hover:bg-slate-700/50 backdrop-blur-sm shadow-lg",
                    cursor: "bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg shadow-blue-500/30 text-white font-semibold"
                  }}
                />
              </div>
            )}
          </div>
        )}

        {/* No Results */}
        {hasSearched && !loading && results && results.results.length === 0 && (
          <div className="mt-12 text-center p-8 bg-slate-800/50 rounded-2xl border border-slate-700/50 backdrop-blur-sm shadow-xl">
            <h3 className="text-xl font-semibold text-slate-300">
              No results found for "{query}"
            </h3>
            <p className="text-slate-500 mt-2">
              Try different keywords or check your spelling
            </p>
          </div>
        )}
      </div>

      {/* Footer - Base Layer */}
      <div className={`py-6 bg-slate-900/50 border-t border-slate-800/50 backdrop-blur-sm ${hasSearched ? 'mt-12' : 'mt-auto'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-slate-500 text-sm">
            Mini Search Engine • Built with Python, React, TypeScript, and NextUI
          </p>
        </div>
      </div>
    </div>
  );
};

export default SearchPage;
