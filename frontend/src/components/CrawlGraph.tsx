import React, { useEffect, useState, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

interface CrawlGraphProps {
  nodes: Array<{
    url: string;
    depth: number;
    status: string;
    title?: string;
    parent?: string;
  }>;
}

interface GraphNode {
  id: string;
  name: string;
  url: string;
  depth: number;
  status: string;
  val: number;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

interface GraphLink {
  source: string;
  target: string;
}

const CrawlGraph: React.FC<CrawlGraphProps> = ({ nodes: crawlNodes }) => {
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphLink[] }>({
    nodes: [],
    links: []
  });
  const fgRef = useRef<any>();
  const [isFirstRender, setIsFirstRender] = useState(true);
  const prevNodesRef = useRef<Map<string, any>>(new Map());

  useEffect(() => {
    const existingNodes = prevNodesRef.current;
    const graphNodes: GraphNode[] = [];
    const graphLinks: GraphLink[] = [];

    // Create nodes, preserving existing positions
    crawlNodes.forEach((crawlNode, index) => {
      const nodeId = crawlNode.url;

      // Determine node size based on status
      let val = 5;
      if (crawlNode.depth === 0) val = 15;
      else if (crawlNode.status === 'crawling') val = 8;

      const existingNode = existingNodes.get(nodeId);
      const newNode: any = {
        id: nodeId,
        name: crawlNode.title?.substring(0, 30) || crawlNode.url.substring(0, 30),
        url: crawlNode.url,
        depth: crawlNode.depth,
        status: crawlNode.status,
        val: val,
      };

      // Preserve position if node already exists
      if (existingNode && existingNode.x !== undefined) {
        newNode.x = existingNode.x;
        newNode.y = existingNode.y;
        newNode.vx = 0;
        newNode.vy = 0;
      }

      graphNodes.push(newNode);

      // Create links
      if (crawlNode.parent) {
        graphLinks.push({
          source: crawlNode.parent,
          target: nodeId,
        });
      }
    });

    // Update the ref with current nodes for next render
    const newNodesMap = new Map();
    graphNodes.forEach(node => {
      newNodesMap.set(node.id, node);
    });
    prevNodesRef.current = newNodesMap;

    console.log(`Force Graph: ${graphNodes.length} nodes, ${graphLinks.length} links`);
    setGraphData({ nodes: graphNodes, links: graphLinks });

    // Center graph on first render or when root node appears
    if (isFirstRender && graphNodes.length > 0) {
      setTimeout(() => {
        if (fgRef.current) {
          fgRef.current.zoomToFit(400, 50);
        }
        setIsFirstRender(false);
      }, 100);
    }
  }, [crawlNodes, isFirstRender]);

  return (
    <div className="w-full h-[600px] bg-slate-900 rounded-xl border border-slate-700/50 overflow-hidden">
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        nodeLabel={(node: any) => `${node.name}\nDepth: ${node.depth}\nStatus: ${node.status}`}
        nodeVal={(node: any) => node.val}
        nodeColor={(node: any) => {
          if (node.status === 'completed') return '#10b981';
          if (node.status === 'crawling') return '#3b82f6';
          if (node.status === 'error') return '#ef4444';
          return '#64748b';
        }}
        nodeCanvasObject={(node: any, ctx, globalScale) => {
          const label = node.name;
          const fontSize = 12 / globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;

          // Draw node circle
          ctx.beginPath();
          ctx.arc(node.x, node.y, node.val, 0, 2 * Math.PI);
          ctx.fillStyle = node.color || '#64748b';
          ctx.fill();

          // Draw label
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillStyle = '#ffffff';
          // ctx.fillText(label, node.x, node.y + node.val + fontSize);
        }}
        linkColor={() => '#475569'}
        linkWidth={1.5}
        linkDirectionalParticles={2}
        linkDirectionalParticleWidth={2}
        linkDirectionalParticleSpeed={0.005}
        backgroundColor="#0f172a"
        d3VelocityDecay={0.3}
        d3AlphaDecay={0.01}
        warmupTicks={100}
        cooldownTicks={0}
        enableNodeDrag={true}
        enableZoomInteraction={true}
        enablePanInteraction={true}
        onNodeClick={(node: any) => {
          console.log('Clicked node:', node);
          window.open(node.url, '_blank');
        }}
      />
    </div>
  );
};

export default CrawlGraph;
