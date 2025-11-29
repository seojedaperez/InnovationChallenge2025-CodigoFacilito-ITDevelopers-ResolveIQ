import { useEffect } from 'react';
import ReactFlow, {
    Node,
    Edge,
    Controls,
    Background,
    useNodesState,
    useEdgesState,
    MarkerType,
    BackgroundVariant
} from 'reactflow';
import 'reactflow/dist/style.css';
import { ExplanationNode } from '../types';

interface ExplanationGraphProps {
    data: ExplanationNode;
}

const ExplanationGraph = ({ data }: ExplanationGraphProps) => {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);

    useEffect(() => {
        if (!data) return;

        const newNodes: Node[] = [];
        const newEdges: Edge[] = [];
        let yOffset = 0;

        const traverse = (node: ExplanationNode, parentId?: string, depth = 0) => {
            const id = `${node.agent}-${depth}-${yOffset}`;

            // Custom Node Style for Dark Theme
            const isRoot = depth === 0;
            const borderColor = isRoot ? '#00f0ff' : '#0078d4';

            newNodes.push({
                id,
                data: {
                    label: (
                        <div style={{
                            padding: '12px',
                            border: `1px solid ${borderColor}`,
                            borderRadius: '8px',
                            background: 'rgba(10, 14, 23, 0.9)',
                            minWidth: '180px',
                            boxShadow: `0 0 10px ${borderColor}40`,
                            color: 'white',
                            textAlign: 'left'
                        }}>
                            <div style={{
                                textTransform: 'uppercase',
                                fontSize: '10px',
                                color: borderColor,
                                letterSpacing: '1px',
                                marginBottom: '4px'
                            }}>
                                {node.agent}
                            </div>
                            <div style={{ fontSize: '13px', fontWeight: '500', marginBottom: '6px' }}>
                                {node.action.length > 50 ? node.action.substring(0, 50) + '...' : node.action}
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div style={{ fontSize: '10px', color: '#888' }}>
                                    Confidence
                                </div>
                                <div style={{
                                    fontSize: '10px',
                                    color: node.confidence > 0.8 ? '#00ff00' : '#ffaa00',
                                    fontWeight: 'bold'
                                }}>
                                    {(node.confidence * 100).toFixed(0)}%
                                </div>
                            </div>
                        </div>
                    )
                },
                position: { x: depth * 300, y: yOffset * 120 },
                type: 'default',
                style: { background: 'transparent', border: 'none' } // Remove default ReactFlow node styles
            });

            if (parentId) {
                newEdges.push({
                    id: `${parentId}-${id}`,
                    source: parentId,
                    target: id,
                    markerEnd: { type: MarkerType.ArrowClosed, color: '#555' },
                    style: { stroke: '#555', strokeWidth: 2 },
                    animated: true,
                });
            }

            yOffset++;

            if (node.children) {
                node.children.forEach((child) => traverse(child, id, depth + 1));
            }
        };

        traverse(data);

        setNodes(newNodes);
        setEdges(newEdges);
    }, [data, setNodes, setEdges]);

    return (
        <div style={{ height: '100%', width: '100%' }}>
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                fitView
            >
                <Background color="#333" gap={20} variant={BackgroundVariant.Dots} />
                <Controls style={{ filter: 'invert(1)' }} />
            </ReactFlow>
        </div>
    );
};

export default ExplanationGraph;
