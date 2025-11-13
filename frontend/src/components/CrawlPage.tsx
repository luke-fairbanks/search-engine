import React, { useState, useEffect, useRef } from 'react';
import { Input, Button, Card, CardBody, Chip, Switch, Tabs, Tab } from '@nextui-org/react';
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
  const [maxPages, setMaxPages] = useState(100);
  const [saveToMongo, setSaveToMongo] = useState(false);
  const [crawlStats, setCrawlStats] = useState<CrawlStats>({
    totalPages: 0,
    completedPages: 0,
    queueSize: 0,
    duration: 0,
    status: 'idle'
  });
  const [crawledNodes, setCrawledNodes] = useState<CrawlNode[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    return () => {
      // Cleanup WebSocket on unmount
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const startCrawl = () => {
    if (!startUrl.trim()) return;

    // Initialize WebSocket connection
    const ws = new WebSocket('ws://localhost:5001/ws/crawl');
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      setCrawlStats(prev => ({ ...prev, status: 'crawling' }));
      setCrawledNodes([]);

      // Send crawl configuration
      const config = {
        action: 'start',
        url: startUrl,
        maxDepth,
        maxPages,
        saveToMongo
      };
      console.log('Sending config:', config);
      ws.send(JSON.stringify(config));
    };

    ws.onmessage = (event) => {
      console.log('WebSocket message:', event.data);
      const data = JSON.parse(event.data);

      if (data.type === 'node') {
        // Update or add node
        setCrawledNodes(prev => {
          const existingIndex = prev.findIndex(n => n.url === data.node.url);
          if (existingIndex >= 0) {
            // Update existing node
            const updated = [...prev];
            updated[existingIndex] = data.node;
            return updated;
          } else {
            // Add new node
            return [...prev, data.node];
          }
        });
      } else if (data.type === 'stats') {
        // Update stats
        setCrawlStats(data.stats);
      } else if (data.type === 'complete') {
        console.log('Crawl complete');
        setCrawlStats(prev => ({ ...prev, status: 'completed' }));
        ws.close();
      } else if (data.type === 'error') {
        console.error('Crawl error:', data);
        setCrawlStats(prev => ({ ...prev, status: 'error' }));
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
      setCrawlStats(prev => ({ ...prev, status: 'error' }));
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
      setIsConnected(false);
    };
  };

  const stopCrawl = () => {
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({ action: 'stop' }));
      wsRef.current.close();
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-gray-900 via-slate-900 to-gray-950 py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4"
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
            Web Crawler
          </h1>
          <p className="text-slate-400">Start crawling from any URL and watch the graph grow in real-time</p>
        </motion.div>

        {/* Configuration Card */}
        <Card className="mb-4 bg-slate-800/60 border border-slate-700/40">
          <CardBody className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <Input
                label="Start URL"
                placeholder="https://example.com"
                value={startUrl}
                onValueChange={setStartUrl}
                disabled={crawlStats.status === 'crawling'}
                classNames={{
                  input: "text-white",
                  inputWrapper: "bg-slate-700/50 border-slate-600/50"
                }}
              />
              <Input
                type="number"
                label="Max Depth"
                value={maxDepth.toString()}
                onValueChange={(val) => setMaxDepth(parseInt(val) || 2)}
                disabled={crawlStats.status === 'crawling'}
                classNames={{
                  input: "text-white",
                  inputWrapper: "bg-slate-700/50 border-slate-600/50"
                }}
              />
              <Input
                type="number"
                label="Max Pages"
                value={maxPages.toString()}
                onValueChange={(val) => setMaxPages(parseInt(val) || 100)}
                disabled={crawlStats.status === 'crawling'}
                classNames={{
                  input: "text-white",
                  inputWrapper: "bg-slate-700/50 border-slate-600/50"
                }}
              />
            </div>

            <div className="flex items-center gap-4 mb-4">
              <Switch
                isSelected={saveToMongo}
                onValueChange={setSaveToMongo}
                isDisabled={crawlStats.status === 'crawling'}
                classNames={{
                  wrapper: "group-data-[selected=true]:bg-gradient-to-r from-blue-500 to-purple-600"
                }}
              >
                <span className="text-white text-sm">Save to MongoDB</span>
              </Switch>
              {saveToMongo && (
                <Chip size="sm" variant="flat" className="bg-green-500/20 text-green-300">
                  Database enabled
                </Chip>
              )}
            </div>

            <div className="flex gap-3">
              {crawlStats.status !== 'crawling' ? (
                <Button
                  onClick={startCrawl}
                  isDisabled={!startUrl.trim()}
                  className="bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold"
                >
                  Start Crawling
                </Button>
              ) : (
                <Button
                  onClick={stopCrawl}
                  color="danger"
                  className="font-semibold"
                >
                  Stop Crawling
                </Button>
              )}

              {isConnected && (
                <Chip color="success" variant="flat">
                  Connected
                </Chip>
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
