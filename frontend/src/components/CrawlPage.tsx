import React, { useState, useEffect, useRef } from 'react';
import { Input, Button, Card, CardBody, Chip, Tabs, Tab } from '@nextui-org/react';
import { NumberInput } from '@heroui/number-input';
import { motion } from 'framer-motion';
import CrawlGraph from './CrawlGraph';

interface CrawlNode {
  url: string;
  depth: number;
  status: 'pending' | 'crawling' | 'completed' | 'error';
  title?: string;
  linkCount?: number;
  parent?: string;
}

interface CrawlStats {
  totalPages: number;
  completedPages: number;
  queueSize: number;
  duration: number;
  status: 'idle' | 'crawling' | 'completed' | 'error';
}

const CrawlPage: React.FC = () => {
  const [startUrl, setStartUrl] = useState('');
  const [maxDepth, setMaxDepth] = useState(2);
  const [maxPages, setMaxPages] = useState(25);
  const [crawlStats, setCrawlStats] = useState<CrawlStats>({
    totalPages: 0,
    completedPages: 0,
    queueSize: 0,
    duration: 0,
    status: 'idle'
  });
  const [crawledNodes, setCrawledNodes] = useState<CrawlNode[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      // Cleanup polling on unmount
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  const startCrawl = async () => {
    if (!startUrl.trim()) return;

    try {
      setIsConnected(true);
      setCrawlStats(prev => ({ ...prev, status: 'crawling' }));
      setCrawledNodes([]);

      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5001';

      // Start crawl job
      const response = await fetch(`${apiUrl}/api/crawler`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: startUrl,
          maxDepth,
          maxPages
        })
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to start crawl');
      }

      const newJobId = data.job_id;
      setJobId(newJobId);

      // Start polling for updates
      startPolling(newJobId, apiUrl);
    } catch (error: any) {
      console.error('Error starting crawl:', error);
      setCrawlStats(prev => ({ ...prev, status: 'error' }));
      setIsConnected(false);
    }
  };

  const startPolling = (jobId: string, apiUrl: string) => {
    // Clear any existing interval
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }

    // Poll immediately
    pollCrawlStatus(jobId, apiUrl);

    // Then poll every 2 seconds
    pollingIntervalRef.current = setInterval(() => {
      pollCrawlStatus(jobId, apiUrl);
    }, 2000);
  };

  const pollCrawlStatus = async (jobId: string, apiUrl: string) => {
    try {
      // Trigger batch processing
      const processResponse = await fetch(`${apiUrl}/api/crawler/${jobId}/process`, {
        method: 'POST'
      });
      
      if (!processResponse.ok) {
        throw new Error('Failed to process batch');
      }

      const job = await processResponse.json();

      // Update stats
      setCrawlStats({
        totalPages: job.stats.total_pages,
        completedPages: job.stats.completed_pages,
        queueSize: job.stats.queue_size,
        duration: job.stats.duration,
        status: job.status === 'completed' ? 'completed' : 'crawling'
      });

      // Update nodes
      setCrawledNodes(job.nodes);

      // Stop polling if completed
      if (job.status === 'completed' && pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
        setIsConnected(false);
      }
    } catch (error) {
      console.error('Error polling status:', error);
    }
  };

  const stopCrawl = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
    setIsConnected(false);
    setCrawlStats(prev => ({ ...prev, status: 'idle' }));
  };

  return (
    <div className="min-h-[calc(100vh-5rem)] bg-gradient-to-br from-gray-900 via-slate-900 to-gray-950 py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
            Web Crawler
          </h1>
          <p className="text-slate-400 text-base sm:text-lg">Discover and index web content automatically</p>

          {/* How it works section */}
          <div className="mt-4 p-3 sm:p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl">
            <div className="flex items-start gap-2 sm:gap-3">
              <div className="text-xl sm:text-2xl flex-shrink-0">💡</div>
              <div>
                <h3 className="text-blue-300 font-semibold mb-1 text-sm sm:text-base">How it works</h3>
                <p className="text-slate-300 text-xs sm:text-sm leading-relaxed">
                  Enter any URL to start crawling. The crawler will explore linked pages, extract their content,
                  and <span className="text-blue-300 font-semibold">save everything to MongoDB</span>.
                  Once crawled, all pages become instantly searchable on the main search page using a
                  BM25 + PageRank algorithm.
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Configuration Card */}
        <Card className="mb-4 bg-slate-800/60 border border-slate-700/40">
          <CardBody className="p-4 sm:p-6">
            <div className="grid grid-cols-1 gap-4 sm:gap-6">
              {/* URL Input */}
              <div>
                <Input
                  label="Starting URL"
                  placeholder="https://example.com"
                  value={startUrl}
                  onValueChange={setStartUrl}
                  disabled={crawlStats.status === 'crawling'}
                  description="The webpage where crawling begins"
                  classNames={{
                    input: "text-white",
                    inputWrapper: "bg-slate-700/50 border-slate-600/50 hover:bg-slate-700/70 transition-colors",
                    label: "text-slate-300 font-semibold",
                    description: "text-slate-400"
                  }}
                  startContent={
                    <span className="text-slate-400">🌐</span>
                  }
                />
              </div>

              {/* Number inputs with better labels */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-slate-300 font-semibold text-sm mb-2 block">
                    Crawl Depth
                  </label>

                  <NumberInput
                    value={maxDepth}
                    onValueChange={(val: number) => setMaxDepth(Math.max(1, val || 100))}
                    disabled={crawlStats.status === 'crawling'}
                    description="How many links deep to explore (1-5)"
                    min={1}
                    max={5}
                    classNames={{
                      input: "text-white focus:outline-none focus:ring-0 focus:border-transparent placeholder:text-slate-400",
                      inputWrapper: "bg-slate-700/50 border-slate-600/50 hover:bg-slate-700/70 transition-colors focus-within:outline-none focus-within:ring-0 focus-within:border-transparent",
                      description: "text-slate-400",
                    }}
                    size="sm"
                    startContent={
                      <span className="text-slate-400">🔗</span>
                    }
                    />
                  <div className="mt-2 flex gap-1">
                    {[1, 2, 3, 4, 5].map(depth => (
                      <button
                        key={depth}
                        onClick={() => setMaxDepth(depth)}
                        disabled={crawlStats.status === 'crawling'}
                        className={`flex-1 py-1 px-2 rounded text-xs font-semibold transition-all ${
                          maxDepth === depth
                            ? 'bg-blue-500 text-white'
                            : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700'
                        } ${crawlStats.status === 'crawling' ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        {depth}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-slate-300 font-semibold text-sm mb-2 block">
                    Page Limit
                  </label>

                    <NumberInput
                    value={maxPages}
                    onValueChange={(val: number) => setMaxPages(Math.max(1, Math.min(val || 25, 50)))}
                    disabled={crawlStats.status === 'crawling'}
                    description="Max 50 pages (my backend memory is limited to the free tier 😅)"
                    min={1}
                    max={50}
                    classNames={{
                      input: "text-white focus:outline-none focus:ring-0 focus:border-transparent placeholder:text-slate-400",
                      inputWrapper: "bg-slate-700/50 border-slate-600/50 hover:bg-slate-700/70 transition-colors focus-within:outline-none focus-within:ring-0 focus-within:border-transparent",
                      description: "text-slate-400",
                    }}
                    size="sm"
                    startContent={
                      <span className="text-slate-400">📄</span>
                    }
                    />
                  <div className="mt-2 flex gap-1">
                    {[10, 25, 50].map(pages => (
                      <button
                        key={pages}
                        onClick={() => setMaxPages(pages)}
                        disabled={crawlStats.status === 'crawling'}
                        className={`flex-1 py-1 px-2 rounded text-xs font-semibold transition-all ${
                          maxPages === pages
                            ? 'bg-purple-500 text-white'
                            : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700'
                        } ${crawlStats.status === 'crawling' ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        {pages}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Database indicator */}
              <div className="flex items-center gap-3 p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
                <div className="text-xl">💾</div>
                <div className="flex-1">
                  <p className="text-green-300 font-semibold text-sm">Auto-save to MongoDB</p>
                  <p className="text-slate-400 text-xs">All crawled pages are automatically saved and indexed for search</p>
                </div>
                <Chip size="sm" className="bg-green-500/20 text-green-300 border-green-500/30">
                  Enabled
                </Chip>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              {crawlStats.status !== 'crawling' ? (
                <Button
                  onClick={startCrawl}
                  isDisabled={!startUrl.trim()}
                  size="lg"
                  className="bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold shadow-lg hover:shadow-xl hover:scale-105 transition-all"
                >
                  <span className="text-lg">🚀</span>
                  Start Crawling
                </Button>
              ) : (
                <Button
                  onClick={stopCrawl}
                  size="lg"
                  color="danger"
                  className="font-semibold shadow-lg"
                >
                  <span className="text-lg">⏹️</span>
                  Stop Crawling
                </Button>
              )}

              {isConnected && (
                <div className="flex items-center gap-2 px-4 py-2 bg-green-500/20 border border-green-500/30 rounded-xl">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  <span className="text-green-300 font-semibold text-sm">Live</span>
                </div>
              )}
            </div>
          </CardBody>
        </Card>

        {/* Stats */}
        {crawlStats.totalPages > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <Card className="bg-slate-800/60 border border-slate-700/40">
              <CardBody className="p-4">
                <p className="text-slate-400 text-sm">Total Pages</p>
                <p className="text-2xl font-bold text-blue-400">{crawlStats.totalPages}</p>
              </CardBody>
            </Card>
            <Card className="bg-slate-800/60 border border-slate-700/40">
              <CardBody className="p-4">
                <p className="text-slate-400 text-sm">Completed</p>
                <p className="text-2xl font-bold text-green-400">{crawlStats.completedPages}</p>
              </CardBody>
            </Card>
            <Card className="bg-slate-800/60 border border-slate-700/40">
              <CardBody className="p-4">
                <p className="text-slate-400 text-sm">Queue Size</p>
                <p className="text-2xl font-bold text-purple-400">{crawlStats.queueSize}</p>
              </CardBody>
            </Card>
            <Card className="bg-slate-800/60 border border-slate-700/40">
              <CardBody className="p-4">
                <p className="text-slate-400 text-sm">Duration</p>
                <p className="text-2xl font-bold text-pink-400">{crawlStats.duration.toFixed(1)}s</p>
              </CardBody>
            </Card>
          </div>
        )}

        {/* Graph and List Tabs */}
        {crawledNodes.length > 0 && (
          <Card className="bg-slate-800/60 border border-slate-700/40">
            <CardBody className="p-6">
              <Tabs
                aria-label="Crawl visualization options"
                classNames={{
                  tabList: "bg-slate-900/50 border border-slate-700/50",
                  cursor: "bg-gradient-to-r from-blue-500 to-purple-600",
                  tab: "text-slate-400 data-[selected=true]:text-white",
                  tabContent: "group-data-[selected=true]:text-white"
                }}
              >
                <Tab key="graph" title="Graph View">
                  <div className="mt-4">
                    <CrawlGraph nodes={crawledNodes} />
                  </div>
                </Tab>
                <Tab key="list" title="List View">
                  <div className="mt-4 space-y-2 max-h-96 overflow-y-auto">
                    {crawledNodes.map((node, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="flex items-center gap-3 p-3 bg-slate-700/30 rounded-lg border border-slate-600/30"
                      >
                        <div className={`w-2 h-2 rounded-full ${
                          node.status === 'completed' ? 'bg-green-400' :
                          node.status === 'crawling' ? 'bg-blue-400 animate-pulse' :
                          node.status === 'error' ? 'bg-red-400' :
                          'bg-gray-400'
                        }`} />
                        <div className="flex-1 min-w-0">
                          <p className="text-white text-sm font-medium truncate">{node.title || 'Loading...'}</p>
                          <p className="text-slate-400 text-xs truncate">{node.url}</p>
                        </div>
                        <div className="flex gap-2">
                          <Chip size="sm" variant="flat" className="bg-blue-500/20 text-blue-300">
                            Depth: {node.depth}
                          </Chip>
                          {node.linkCount !== undefined && (
                            <Chip size="sm" variant="flat" className="bg-purple-500/20 text-purple-300">
                              Links: {node.linkCount}
                            </Chip>
                          )}
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </Tab>
              </Tabs>
            </CardBody>
          </Card>
        )}
      </div>
    </div>
  );
};

export default CrawlPage;
