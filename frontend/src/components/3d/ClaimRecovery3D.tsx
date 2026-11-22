import React, { useRef, useState, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Html, Line } from '@react-three/drei';
import * as THREE from 'three';
import { RecoveryGraphData, GraphNode, GraphEdge } from '../../types';
import { formatCurrency } from '../../utils/formatters';
import { Shield, Users, FileText, DollarSign, X, ExternalLink, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface ClaimRecovery3DProps {
  data: RecoveryGraphData;
}

// 3D Node Mesh
const NodeObject: React.FC<{
  node: GraphNode;
  position: [number, number, number];
  isSelected: boolean;
  onClick: () => void;
}> = ({ node, position, isSelected, onClick }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame((_, delta) => {
    if (meshRef.current && node.id === 'core') {
      meshRef.current.rotation.y += delta * 0.4;
    }
  });

  const color = isSelected ? '#FFFFFF' : node.color;
  const scale = hovered ? node.size * 1.25 : node.size;

  return (
    <group position={position}>
      <mesh
        ref={meshRef}
        onClick={(e) => {
          e.stopPropagation();
          onClick();
        }}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHovered(true);
        }}
        onPointerOut={() => setHovered(false)}
        scale={[scale, scale, scale]}
      >
        <sphereGeometry args={[0.5, 32, 32]} />
        <meshStandardMaterial
          color={color}
          roughness={0.3}
          metalness={0.7}
          emissive={isSelected || hovered ? node.color : '#000000'}
          emissiveIntensity={isSelected ? 0.6 : hovered ? 0.4 : 0.0}
        />
      </mesh>

      {/* Floating 3D Label */}
      <Html distanceFactor={12} position={[0, scale * 0.7 + 0.3, 0]} center pointerEvents="none">
        <div
          className={`px-2 py-0.5 rounded text-[11px] font-mono whitespace-nowrap shadow-lg border transition-all ${
            isSelected || hovered
              ? 'bg-navy-950 text-paper-100 border-brass-500 scale-105'
              : 'bg-navy-950/80 text-paper-200 border-navy-700'
          }`}
        >
          {node.label}
        </div>
      </Html>
    </group>
  );
};

// 3D Connection Line
const EdgeLine: React.FC<{
  start: [number, number, number];
  end: [number, number, number];
  color: string;
  weight: number;
}> = ({ start, end, color, weight }) => {
  return (
    <Line
      points={[start, end]}
      color={color}
      lineWidth={Math.max(1, weight * 2)}
      transparent
      opacity={Math.max(0.4, weight)}
    />
  );
};

// Probability Ring around central core node
const ProbabilityRing: React.FC<{ probability: number }> = ({ probability }) => {
  const ringRef = useRef<THREE.Mesh>(null);

  useFrame((_, delta) => {
    if (ringRef.current) {
      ringRef.current.rotation.z += delta * 0.2;
    }
  });

  const thetaLength = (probability / 100) * Math.PI * 2;

  return (
    <mesh ref={ringRef} rotation={[-Math.PI / 2, 0, 0]}>
      <ringGeometry args={[1.1, 1.25, 64, 1, 0, thetaLength]} />
      <meshBasicMaterial color="#2F8F89" side={THREE.DoubleSide} transparent opacity={0.85} />
    </mesh>
  );
};

// 2D Canvas Fallback Component
const Canvas2DFallback: React.FC<{
  data: RecoveryGraphData;
  onSelectNode: (node: GraphNode) => void;
}> = ({ data, onSelectNode }) => {
  return (
    <div className="w-full h-[520px] bg-paper-100 dark:bg-navy-950 rounded-xl p-6 flex flex-col justify-between border border-paper-300 dark:border-navy-800 relative overflow-hidden">
      <div className="flex items-center justify-between z-10">
        <div>
          <span className="text-xs font-semibold uppercase text-brass-500 tracking-wider">
            2D Recovery Topology Fallback
          </span>
          <h3 className="text-sm font-bold text-navy-950 dark:text-paper-100">
            {data.claim_number} Network Graph
          </h3>
        </div>
        <div className="text-xs font-mono text-teal-600 dark:text-teal-400 font-semibold px-2 py-1 rounded bg-teal-500/10 border border-teal-500/30">
          Recovery Prob: {data.recovery_probability}%
        </div>
      </div>

      {/* Grid Layout of Nodes */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 my-auto z-10">
        {data.nodes.map((n) => (
          <div
            key={n.id}
            onClick={() => onSelectNode(n)}
            className="p-3 rounded-lg border border-paper-300 dark:border-navy-700 bg-paper-50 dark:bg-navy-900 hover:border-brass-500 cursor-pointer transition-all shadow-sm flex items-center justify-between"
          >
            <div>
              <div className="flex items-center gap-1.5 mb-1">
                <span
                  className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                  style={{ backgroundColor: n.color }}
                />
                <span className="text-xs font-semibold text-navy-950 dark:text-paper-100 font-mono">
                  {n.label}
                </span>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">{n.sublabel || n.type}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="text-center text-[11px] text-slate-400 z-10">
        Click any node to inspect relationship metrics and evidence weighting
      </div>
    </div>
  );
};

export const ClaimRecovery3D: React.FC<ClaimRecovery3DProps> = ({ data }) => {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [viewMode, setViewMode] = useState<'3d' | '2d'>('3d');
  const navigate = useNavigate();

  // Position calculation for orbiting nodes
  const nodePositions = useMemo(() => {
    const map = new Map<string, [number, number, number]>();
    map.set('core', [0, 0, 0]);

    const nonCoreNodes = data.nodes.filter((n) => n.id !== 'core');
    const radius = 4.2;

    nonCoreNodes.forEach((node, idx) => {
      const angle = (idx / nonCoreNodes.length) * Math.PI * 2;
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      // Slight vertical stagger for visual depth
      const y = Math.sin(angle * 2) * 1.2;
      map.set(node.id, [x, y, z]);
    });

    return map;
  }, [data.nodes]);

  return (
    <div className="relative w-full h-[560px] rounded-2xl overflow-hidden border border-paper-300 dark:border-navy-800 bg-paper-50 dark:bg-navy-950 shadow-inner">
      {/* View Mode Toggle Header */}
      <div className="absolute top-4 left-4 z-10 flex items-center gap-2 bg-paper-100/90 dark:bg-navy-900/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-paper-300 dark:border-navy-700 text-xs">
        <span className="font-semibold text-brass-500">3D Recovery Graph</span>
        <span className="text-slate-400">•</span>
        <button
          onClick={() => setViewMode(viewMode === '3d' ? '2d' : '3d')}
          className="flex items-center gap-1 text-slate-600 dark:text-slate-300 hover:text-brass-500 font-medium transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Switch to {viewMode === '3d' ? '2D View' : '3D Orbit'}
        </button>
      </div>

      {/* Recovery Probability Indicator */}
      <div className="absolute top-4 right-4 z-10 bg-paper-100/90 dark:bg-navy-900/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-paper-300 dark:border-navy-700 text-xs font-mono">
        <span className="text-slate-400 mr-2">Adverse Liability:</span>
        <span className="text-rust-500 font-bold">{data.adverse_fault_pct}%</span>
        <span className="text-slate-400 mx-2">|</span>
        <span className="text-slate-400 mr-2">Recovery Prob:</span>
        <span className="text-teal-600 dark:text-teal-400 font-bold">
          {data.recovery_probability}%
        </span>
      </div>

      {/* 3D Scene or 2D Fallback */}
      {viewMode === '3d' ? (
        <Canvas camera={{ position: [0, 6, 8], fov: 45 }}>
          <ambientLight intensity={0.7} />
          <pointLight position={[10, 10, 10]} intensity={1.2} />
          <pointLight position={[-10, -5, -10]} intensity={0.6} color="#2F8F89" />

          {/* Core probability ring */}
          <ProbabilityRing probability={data.recovery_probability} />

          {/* Edge Lines */}
          {data.edges.map((e, idx) => {
            const start = nodePositions.get(e.source) || [0, 0, 0];
            const end = nodePositions.get(e.target) || [0, 0, 0];
            return (
              <EdgeLine
                key={idx}
                start={start}
                end={end}
                color={e.color}
                weight={e.weight}
              />
            );
          })}

          {/* Nodes */}
          {data.nodes.map((node) => {
            const pos = nodePositions.get(node.id) || [0, 0, 0];
            return (
              <NodeObject
                key={node.id}
                node={node}
                position={pos}
                isSelected={selectedNode?.id === node.id}
                onClick={() => setSelectedNode(node)}
              />
            );
          })}

          <OrbitControls
            enablePan={true}
            enableZoom={true}
            enableRotate={true}
            maxDistance={18}
            minDistance={4}
          />
        </Canvas>
      ) : (
        <Canvas2DFallback data={data} onSelectNode={setSelectedNode} />
      )}

      {/* Node Inspector Side Panel */}
      {selectedNode && (
        <div className="absolute top-16 right-4 bottom-4 w-80 bg-paper-50/95 dark:bg-navy-900/95 backdrop-blur-lg border border-paper-300 dark:border-navy-700 rounded-2xl shadow-2xl p-4 flex flex-col justify-between z-20 animate-in slide-in-from-right duration-200">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-paper-200 dark:border-navy-800">
              <div className="flex items-center gap-2">
                <span
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: selectedNode.color }}
                />
                <span className="text-xs uppercase font-semibold text-slate-500 tracking-wider">
                  {selectedNode.type} Node
                </span>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="p-1 rounded-md text-slate-400 hover:text-navy-950 dark:hover:text-paper-100"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="mt-3 space-y-3">
              <div>
                <h4 className="text-sm font-bold text-navy-950 dark:text-paper-100 font-mono">
                  {selectedNode.label}
                </h4>
                {selectedNode.sublabel && (
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                    {selectedNode.sublabel}
                  </p>
                )}
              </div>

              {/* Node Specific Details */}
              {selectedNode.type === 'claim' && (
                <div className="space-y-1.5 text-xs bg-paper-100 dark:bg-navy-950 p-2.5 rounded-lg border border-paper-200 dark:border-navy-800 font-mono">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Paid Loss:</span>
                    <span>{formatCurrency(selectedNode.paid_amount)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Net Recovery:</span>
                    <span className="text-teal-600 dark:text-teal-400 font-semibold">
                      {formatCurrency(selectedNode.net_recovery)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Recovery Prob:</span>
                    <span>{selectedNode.recovery_probability}%</span>
                  </div>
                </div>
              )}

              {selectedNode.type === 'party' && (
                <div className="space-y-1.5 text-xs bg-paper-100 dark:bg-navy-950 p-2.5 rounded-lg border border-paper-200 dark:border-navy-800">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Carrier:</span>
                    <span className="font-semibold">{selectedNode.insurance_carrier}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Vehicle:</span>
                    <span>{selectedNode.sublabel?.split('•')[0] || 'Passenger Vehicle'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Fault Assessment:</span>
                    <span className={selectedNode.is_adverse ? 'text-rust-500 font-bold' : 'text-teal-500 font-bold'}>
                      {selectedNode.is_adverse ? 'Adverse Negligence' : 'Zero Fault'}
                    </span>
                  </div>
                </div>
              )}

              {selectedNode.type === 'evidence' && (
                <div className="space-y-2 text-xs bg-paper-100 dark:bg-navy-950 p-2.5 rounded-lg border border-paper-200 dark:border-navy-800">
                  {selectedNode.citations && (
                    <div>
                      <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                        Citations / Violations
                      </span>
                      <span className="font-semibold text-rust-500">{selectedNode.citations}</span>
                    </div>
                  )}
                  {selectedNode.narrative && (
                    <div>
                      <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                        Investigative Excerpt
                      </span>
                      <p className="text-slate-600 dark:text-slate-300 italic text-[11px] mt-0.5">
                        "{selectedNode.narrative}"
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="pt-3 border-t border-paper-200 dark:border-navy-800 text-[11px] text-slate-400 text-center">
            Weighted connection strength: 0.95
          </div>
        </div>
      )}
    </div>
  );
};
