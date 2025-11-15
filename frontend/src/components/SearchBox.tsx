import React, { useState, useEffect, useRef } from 'react';
import { Input, Button, Spinner, Card, CardBody } from '@nextui-org/react';
import { motion } from 'framer-motion';
import { searchApi } from '../services/api';

interface SearchBoxProps {
  onSearch: (query: string) => void;
  loading?: boolean;
  initialQuery?: string;
  hasSearched?: boolean;
  onMobileFocus?: (isFocused: boolean) => void;
}

const SearchBox: React.FC<SearchBoxProps> = ({ onSearch, loading = false, initialQuery = '', hasSearched = false, onMobileFocus }) => {
  const [query, setQuery] = useState(initialQuery);
  const [isFocused, setIsFocused] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const inputRef = useRef<HTMLDivElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  // Detect if device is mobile
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 640); // sm breakpoint
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    setQuery(initialQuery);
  }, [initialQuery]);

  // Fetch suggestions when query changes
  useEffect(() => {
    const fetchSuggestions = async () => {
      if (query.length < 2) {
        setSuggestions([]);
        setShowSuggestions(false);
        return;
      }

      setLoadingSuggestions(true);
      try {
        const results = await searchApi.getSuggestions(query, 8);
        setSuggestions(results);
        setShowSuggestions(results.length > 0 && isFocused);
      } catch (error) {
        console.error('Failed to fetch suggestions:', error);
        setSuggestions([]);
      } finally {
        setLoadingSuggestions(false);
      }
    };

    const debounceTimer = setTimeout(fetchSuggestions, 200);
    return () => clearTimeout(debounceTimer);
  }, [query, isFocused]);

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        inputRef.current &&
        !inputRef.current.contains(event.target as Node) &&
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    onSearch(suggestion);
    setShowSuggestions(false);
    setIsFocused(false);
    if (onMobileFocus && isMobile) {
      onMobileFocus(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions || suggestions.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => (prev < suggestions.length - 1 ? prev + 1 : prev));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => (prev > 0 ? prev - 1 : -1));
    } else if (e.key === 'Enter' && selectedIndex >= 0) {
      e.preventDefault();
      handleSuggestionClick(suggestions[selectedIndex]);
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
      setSelectedIndex(-1);
    }
  };

  const handleFocus = () => {
    setIsFocused(true);
    setShowSuggestions(suggestions.length > 0);
    if (onMobileFocus && isMobile) {
      onMobileFocus(true);
    }
  };

  const handleBlur = () => {
    setIsFocused(false);
    if (onMobileFocus && isMobile) {
      onMobileFocus(false);
    }
  };

  // On mobile when focused, hide the button. On desktop, show it when focused or not searched yet
  const showButton = isMobile ? (!isFocused && !hasSearched) : (!hasSearched || isFocused);

  return (
    <form onSubmit={handleSubmit} className="relative w-full flex max-w-3xl mx-auto px-2 sm:px-0">
      <div className="flex flex-1 gap-2 sm:gap-3 justify-center items-center">
        <motion.div
          className="w-full relative"
          ref={inputRef}
          animate={{
            maxWidth: showButton ? '600px' : '800px'
          }}
          transition={{
            type: "spring",
            stiffness: 150,
            damping: 20
          }}
        >
          <Input
            type="text"
            placeholder="Search the web..."
            value={query}
            onValueChange={setQuery}
            onFocus={handleFocus}
            onBlur={handleBlur}
            onKeyDown={handleKeyDown}
            disabled={loading}
            autoFocus={!hasSearched}
            size="lg"
            radius="full"
            classNames={{
              input: "text-base sm:text-lg text-white placeholder:text-slate-500",
              inputWrapper: "h-11 sm:h-12 bg-slate-800/80 backdrop-blur-xl border-2 border-slate-700/50 hover:border-blue-500/50 shadow-2xl hover:shadow-blue-500/20 transition-all duration-300 data-[hover=true]:bg-slate-800/90",
            }}
            startContent={
              <svg className="w-4 h-4 sm:w-5 sm:h-5 text-slate-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            }
          />

          {/* Autocomplete Suggestions */}
          {showSuggestions && suggestions.length > 0 && (
            <motion.div
              ref={suggestionsRef}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="absolute top-full mt-2 w-full z-50"
            >
              <Card className="bg-slate-800/95 backdrop-blur-xl border border-slate-700/50 shadow-2xl">
                <CardBody className="p-2">
                  {suggestions.map((suggestion, index) => (
                    <motion.button
                      key={index}
                      type="button"
                      onMouseDown={(e) => {
                        e.preventDefault();
                        handleSuggestionClick(suggestion);
                      }}
                      onMouseEnter={() => setSelectedIndex(index)}
                      className={`w-full text-left px-3 sm:px-4 py-2 sm:py-3 rounded-lg transition-all duration-150 flex items-center gap-2 sm:gap-3 ${
                        selectedIndex === index
                          ? 'bg-blue-500/20 text-blue-300'
                          : 'text-slate-300 hover:bg-slate-700/50'
                      }`}
                      whileHover={{ x: 4 }}
                    >
                      <svg className="w-3 h-3 sm:w-4 sm:h-4 text-slate-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                      <span className="flex-1 truncate text-sm sm:text-base">{suggestion}</span>
                      {selectedIndex === index && (
                        <svg className="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      )}
                    </motion.button>
                  ))}
                </CardBody>
              </Card>
            </motion.div>
          )}
        </motion.div>
        <motion.div
          animate={{
            opacity: showButton ? 1 : 0,
            width: showButton ? 'auto' : '0px',
            marginLeft: showButton ? '0rem' : '0rem',
          }}
          transition={{
            type: "spring",
            stiffness: 150,
            damping: 20
          }}
          style={{ overflow: 'hidden' }}
        >
          <Button
            type="submit"
            size="lg"
            radius="full"
            isDisabled={!query.trim() || loading}
            className="px-6 sm:px-10 h-11 sm:h-12 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 shadow-2xl shadow-blue-500/30 hover:shadow-blue-500/50 transition-all duration-300 font-semibold text-white border-0 whitespace-nowrap text-sm sm:text-base"
          >
            {loading ? <Spinner size="sm" color="white" /> : "Search"}
          </Button>
        </motion.div>
      </div>
    </form>
  );
};

export default SearchBox;
