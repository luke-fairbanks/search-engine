import React, { useCallback, useEffect, useState } from 'react';
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  MiniMap,
  BackgroundVariant,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface CrawlGraphProps {
  nodes: Array<{
    url: string;
    depth: number;
    status: string;
    title?: string;
    parent?: string;
  }>;
}

const CrawlGraph: React.FC<CrawlGraphProps> = ({ nodes: crawlNodes }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [nodeMap, setNodeMap] = useState<Map<string, string>>(new Map());

  useEffect(() => {
    const newNodes: Node[] = [];
    const newEdges: Edge[] = [];
    const urlToId = new Map<string, string>();
    const nodePositions = new Map<string, { x: number; y: number }>();

    // First pass: create ID mapping
    crawlNodes.forEach((crawlNode, index) => {
      const nodeId = `node-${index}`;
      urlToId.set(crawlNode.url, nodeId);
    });

    // Group children by parent
    const childrenByParent = new Map<string, any[]>();
    crawlNodes.forEach((node) => {
      if (node.parent) {
        if (!childrenByParent.has(node.parent)) {
          childrenByParent.set(node.parent, []);
        }
        childrenByParent.get(node.parent)!.push(node);
      }
    });

    // Calculate positions recursively starting from root
    const positionNode = (node: any, parentX: number = 0, parentY: number = 0, angle: number = 0, radius: number = 0) => {
      // Skip if already positioned
      if (nodePositions.has(node.url)) return;

      let x: number, y: number;
      if (node.depth === 0) {
        // Root node at center
        x = 0;
        y = 0;
      } else {
        // Position around parent
        x = parentX + Math.cos(angle) * radius;
        y = parentY + Math.sin(angle) * radius;
      }

      nodePositions.set(node.url, { x, y });

      // Position children around this node
      const children = childrenByParent.get(node.url) || [];
      if (children.length > 0) {
        const childRadius = 150 + (node.depth * 80); // Increase radius with depth
        const angleStep = (2 * Math.PI) / children.length;

        children.forEach((child, i) => {
          const childAngle = i * angleStep;
          positionNode(child, x, y, childAngle, childRadius);
        });
      }
    };

    // Find root node (the one with depth 0)
    const rootNode = crawlNodes.find(n => n.depth === 0);
    if (rootNode) {
      positionNode(rootNode);
    }

    // Position any remaining unpositioned nodes in a fallback circle
    const unpositionedNodes = crawlNodes.filter(n => !nodePositions.has(n.url));
    if (unpositionedNodes.length > 0) {
      const fallbackRadius = 400;
      const angleStep = (2 * Math.PI) / unpositionedNodes.length;
      unpositionedNodes.forEach((node, i) => {
        const angle = i * angleStep;
        nodePositions.set(node.url, {
          x: Math.cos(angle) * fallbackRadius,
          y: Math.sin(angle) * fallbackRadius
        });
      });
    }

    // Create nodes with calculated positions
    crawlNodes.forEach((crawlNode, index) => {
      const nodeId = `node-${index}`;
      const pos = nodePositions.get(crawlNode.url) || { x: 0, y: 0 };

      // Determine node color based on status
      let bgColor = '#64748b';
      let borderColor = '#475569';
      if (crawlNode.status === 'completed') {
        bgColor = '#10b981';
        borderColor = '#059669';
      } else if (crawlNode.status === 'crawling') {
        bgColor = '#3b82f6';
        borderColor = '#2563eb';
      } else if (crawlNode.status === 'error') {
        bgColor = '#ef4444';
        borderColor = '#dc2626';
      }

      newNodes.push({
        id: nodeId,
        type: 'default',
        position: pos,
        data: {
          label: (
            <div className="text-[10px] leading-tight">
              <div className="font-semibold truncate max-w-[80px]">
                {crawlNode.title?.substring(0, 15) || '...'}
              </div>
            </div>
          ),
        },
        style: {
          background: bgColor,
          color: 'white',
          border: `1.5px solid ${borderColor}`,
          borderRadius: '6px',
          padding: '6px 8px',
          fontSize: '10px',
          width: 90,
          height: 35,
        },
      });

      // Create edges
      if (crawlNode.parent) {
        const parentId = urlToId.get(crawlNode.parent);
        if (parentId) {
          newEdges.push({
            id: `edge-${parentId}-${nodeId}`,
            source: parentId,
            target: nodeId,
            type: 'smoothstep',
            style: { stroke: '#475569', strokeWidth: 1.5, opacity: 0.5 },
          });
        }
      }
    });

    console.log(`Graph: ${newNodes.length} nodes, ${newEdges.length} edges`);
    setNodes(newNodes);
    setEdges(newEdges);
    setNodeMap(urlToId);
  }, [crawlNodes, setNodes, setEdges]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <div className="w-full h-[600px] bg-slate-900 rounded-xl border border-slate-700/50 overflow-hidden">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
        attributionPosition="bottom-left"
      >
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} color="#334155" />
        <Controls className="bg-slate-800 border border-slate-700" />
        <MiniMap
          className="bg-slate-800 border border-slate-700"
          nodeColor={(node) => {
            return node.style?.background as string || '#64748b';
          }}
        />
      </ReactFlow>
    </div>
  );
};

export default CrawlGraph;
