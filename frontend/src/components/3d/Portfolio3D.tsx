import React, { useRef, useState, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Html } from '@react-three/drei';
import * as THREE from 'three';
import { PortfolioPoint } from '../../types';
import { formatCurrency } from '../../utils/formatters';
import { useNavigate } from 'react-router-dom';
import { RefreshCw, ExternalLink, Filter, Layers } from 'lucide-react';
import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface Portfolio3DProps {
  points: PortfolioPoint[];
}

// 3D Point Particle
const ScatterPoint: React.FC<{
  point: PortfolioPoint;
  position: [number, number, number];
  isHovered: boolean;
  onHover: (hovered: boolean) => void;
  onClick: () => void;
}> = ({ point, position, isHovered, onHover, onClick }) => {
  const meshRef = useRef<THREE.Mesh>(null);

  const radius = Math.max(0.12, Math.min(0.45, point.size * 0.015));

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
          onHover(true);
        }}
        onPointerOut={() => onHover(false)}
        scale={isHovered ? [1.6, 1.6, 1.6] : [1, 1, 1]}
      >
        <sphereGeometry args={[radius, 16, 16]} />
        <meshStandardMaterial
          color={point.color}
          roughness={0.2}
          metalness={0.6}
          emissive={isHovered ? point.color : '#000000'}
          emissiveIntensity={isHovered ? 0.7 : 0.0}
        />
      </mesh>

      {isHovered && (
        <Html distanceFactor={14} position={[0, radius + 0.3, 0]} center pointerEvents="none">
          <div className="bg-navy-950 text-paper-100 p-2.5 rounded-lg shadow-2xl border border-navy-700 text-xs w-48 font-sans z-50">
            <div className="flex items-center justify-between font-mono mb-1">
              <span className="font-bold text-brass-400">{point.claim_number}</span>
              <span
                className="text-[10px] px-1 rounded font-semibold"
                style={{ backgroundColor: `${point.color}30`, color: point.color }}
              >
                {point.priority}
              </span>
            </div>
            <p className="text-[11px] text-slate-300 mb-1.5 truncate">{point.incident_type}</p>
            <div className="text-[10px] space-y-0.5 font-mono text-slate-400">
              <div className="flex justify-between">
                <span>Paid Loss:</span>
                <span className="text-paper-100">{formatCurrency(point.paid_amount)}</span>
              </div>
              <div className="flex justify-between">
                <span>Recovery Prob:</span>
                <span className="text-teal-400 font-bold">{point.recovery_probability}%</span>
              </div>
              <div className="flex justify-between">
                <span>SOL Deadline:</span>
                <span>{point.days_to_sol} days</span>
              </div>
            </div>
            <p className="text-[9px] text-brass-400 text-center mt-1.5 pt-1 border-t border-navy-800">
              Click to open case dossier
            </p>
          </div>
        </Html>
      )}
    </group>
  );
};

export const Portfolio3D: React.FC<Portfolio3DProps> = ({ points }) => {
  const [viewMode, setViewMode] = useState<'3d' | '2d'>('3d');
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [priorityFilter, setPriorityFilter] = useState<'All' | 'High' | 'Medium' | 'Low'>('All');
  const navigate = useNavigate();

  // Normalize points into a centered bounding box for Three.js
  const { normalizedPoints, maxValues } = useMemo(() => {
    let maxPaid = 1;
    let maxProb = 100;
    let maxDays = 1;

    points.forEach((p) => {
      if (p.paid_amount > maxPaid) maxPaid = p.paid_amount;
      if (p.days_to_sol > maxDays) maxDays = p.days_to_sol;
    });

    const norm = points.map((p) => {
      // Map to [-6, 6] coordinate space
      const normX = (p.paid_amount / maxPaid) * 12 - 6;
      const normY = (p.recovery_probability / maxProb) * 8 - 4;
      const normZ = (p.days_to_sol / maxDays) * 12 - 6;

      return {
        point: p,
        pos: [normX, normY, normZ] as [number, number, number],
      };
    });

    return { normalizedPoints: norm, maxValues: { maxPaid, maxDays } };
  }, [points]);

  const filteredPoints = useMemo(() => {
    if (priorityFilter === 'All') return normalizedPoints;
    return normalizedPoints.filter((np) => np.point.priority === priorityFilter);
  }, [normalizedPoints, priorityFilter]);

  return (
    <div className="relative w-full h-[650px] rounded-2xl overflow-hidden border border-paper-300 dark:border-navy-800 bg-paper-50 dark:bg-navy-950 shadow-inner">
      {/* Top Floating Controls */}
      <div className="absolute top-4 left-4 z-10 flex flex-wrap items-center gap-2 bg-paper-100/90 dark:bg-navy-900/90 backdrop-blur-md px-3 py-2 rounded-xl border border-paper-300 dark:border-navy-700 text-xs shadow-md">
        <span className="font-semibold text-brass-500">Portfolio Explorer</span>
        <span className="text-slate-400">•</span>
        <button
          onClick={() => setViewMode(viewMode === '3d' ? '2d' : '3d')}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-paper-200 dark:bg-navy-800 hover:text-brass-500 font-medium transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Switch to {viewMode === '3d' ? '2D Scatter View' : '3D Spatial Field'}
        </button>

        <span className="text-slate-400">•</span>

        {/* Priority Filter Toggle */}
        <div className="flex items-center gap-1">
          {(['All', 'High', 'Medium', 'Low'] as const).map((p) => (
            <button
              key={p}
              onClick={() => setPriorityFilter(p)}
              className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                priorityFilter === p
                  ? 'bg-brass-500 text-navy-950 font-bold'
                  : 'text-slate-500 dark:text-slate-400 hover:bg-paper-200 dark:hover:bg-navy-800'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Axis Legend Overlay */}
      <div className="absolute bottom-4 left-4 z-10 bg-paper-100/90 dark:bg-navy-900/90 backdrop-blur-md px-3.5 py-2.5 rounded-xl border border-paper-300 dark:border-navy-700 text-xs font-mono space-y-1 shadow-md">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-rust-500" />
          <span className="text-slate-400">X-Axis:</span>
          <span className="text-paper-900 dark:text-paper-100">Carrier Paid Exposure ($)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-teal-500" />
          <span className="text-slate-400">Y-Axis:</span>
          <span className="text-paper-900 dark:text-paper-100">Recovery Probability (%)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-brass-500" />
          <span className="text-slate-400">Z-Axis:</span>
          <span className="text-paper-900 dark:text-paper-100">Days to SOL Expiration</span>
        </div>
      </div>

      {/* 3D Scene */}
      {viewMode === '3d' ? (
        <Canvas camera={{ position: [0, 8, 14], fov: 50 }}>
          <ambientLight intensity={0.8} />
          <pointLight position={[15, 20, 15]} intensity={1.2} />
          <pointLight position={[-15, -10, -15]} intensity={0.5} color="#2F8F89" />

          {/* Coordinate Guide Box */}
          <gridHelper args={[16, 16, '#CFA968', '#1D2D42']} position={[0, -4, 0]} />

          {filteredPoints.map(({ point, pos }) => (
            <ScatterPoint
              key={point.id}
              point={point}
              position={pos}
              isHovered={hoveredId === point.id}
              onHover={(hovered) => setHoveredId(hovered ? point.id : null)}
              onClick={() => navigate(`/claims/${point.claim_id}`)}
            />
          ))}

          <OrbitControls
            enablePan={true}
            enableZoom={true}
            enableRotate={true}
            maxDistance={25}
            minDistance={4}
          />
        </Canvas>
      ) : (
        /* Standard 2D Scatter Chart Fallback / Alternative */
        <div className="w-full h-full p-8 pt-16 flex flex-col justify-between">
          <ResponsiveContainer width="100%" height="88%">
            <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 20 }}>
              <XAxis
                type="number"
                dataKey="x"
                name="Paid Amount"
                unit="$"
                tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
                stroke="#8FA0B3"
                fontSize={12}
              />
              <YAxis
                type="number"
                dataKey="y"
                name="Recovery Probability"
                unit="%"
                stroke="#8FA0B3"
                fontSize={12}
              />
              <ZAxis type="number" dataKey="size" range={[60, 400]} name="Exposure" />
              <Tooltip
                cursor={{ strokeDasharray: '3 3' }}
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload as PortfolioPoint;
                    return (
                      <div className="bg-navy-950 p-2.5 rounded-lg border border-navy-700 text-xs font-sans text-paper-100 shadow-xl">
                        <p className="font-bold text-brass-400 font-mono mb-1">{data.claim_number}</p>
                        <p className="text-slate-400">{data.incident_type}</p>
                        <p className="font-mono mt-1">Paid: {formatCurrency(data.paid_amount)}</p>
                        <p className="font-mono text-teal-400 font-bold">Prob: {data.recovery_probability}%</p>
                        <p className="font-mono text-slate-400">SOL: {data.days_to_sol} days</p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Scatter
                name="Claims"
                data={filteredPoints.map((np) => np.point)}
                onClick={(e: any) => navigate(`/claims/${e.claim_id}`)}
                className="cursor-pointer"
              >
                {filteredPoints.map((np, index) => (
                  <Cell key={`cell-${index}`} fill={np.point.color} />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
          <div className="text-center text-xs text-slate-400">
            Click any bubble to open the full claim investigation dossier
          </div>
        </div>
      )}
    </div>
  );
};
