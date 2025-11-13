import React, { useState, useEffect } from 'react';
import { Input, Button, Spinner } from '@nextui-org/react';
import { motion } from 'framer-motion';

interface SearchBoxProps {
  onSearch: (query: string) => void;
  loading?: boolean;
  initialQuery?: string;
  hasSearched?: boolean;
}

const SearchBox: React.FC<SearchBoxProps> = ({ onSearch, loading = false, initialQuery = '', hasSearched = false }) => {
  const [query, setQuery] = useState(initialQuery);
  const [isFocused, setIsFocused] = useState(false);

  useEffect(() => {
    setQuery(initialQuery);
  }, [initialQuery]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const showButton = !hasSearched || isFocused;

  return (
    <form onSubmit={handleSubmit} className="relative w-full flex max-w-3xl mx-auto">
        {/* <div className='w-5 h-full' /> */}
      <div className="flex flex-1 gap-3 justify-center items-center">
        <motion.div
          className="w-full"
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
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            disabled={loading}
            autoFocus={!hasSearched}
            size="lg"
            radius="full"
            classNames={{
              input: "text-lg text-white placeholder:text-slate-500",
              inputWrapper: "h-12 bg-slate-800/80 backdrop-blur-xl border-2 border-slate-700/50 hover:border-blue-500/50 shadow-2xl hover:shadow-blue-500/20 transition-all duration-300 data-[hover=true]:bg-slate-800/90",
            }}
            startContent={
              <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            }
          />
        </motion.div>
        <motion.div
          animate={{
            opacity: showButton ? 1 : 0,
            width: showButton ? '140px' : '0px',
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
            className="px-10 h-12 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 shadow-2xl shadow-blue-500/30 hover:shadow-blue-500/50 transition-all duration-300 font-semibold text-white border-0 whitespace-nowrap"
            style={{ width: '140px' }}
          >
            {loading ? <Spinner size="sm" color="white" /> : "Search"}
          </Button>
        </motion.div>
      </div>
      {/* <div className=' absolute right-0 w-10 h-full bg-gradient-to-r from-transparent to-slate-900' /> */}
    </form>
  );
};

export default SearchBox;
