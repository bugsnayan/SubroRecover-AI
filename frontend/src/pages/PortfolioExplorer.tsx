import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { Portfolio3D } from '../components/3d/Portfolio3D';
import { Globe2, Layers, Filter, Compass } from 'lucide-react';

export const PortfolioExplorer: React.FC = () => {
  const { data: portfolioData, isLoading } = useQuery({
    queryKey: ['portfolio-3d'],
    queryFn: () => api.getPortfolio3D(),
  });

  return (
    <div className="space-y-6 pb-12">
      {/* Page Title & Context Header */}
      <div className="bg-paper-50 dark:bg-navy-800/90 border border-paper-200 dark:border-navy-700/80 rounded-2xl p-5 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Compass className="w-5 h-5 text-brass-500" />
              <h2 className="text-base font-bold text-navy-950 dark:text-paper-100 tracking-tight">
                3D Portfolio Risk & Opportunity Explorer
              </h2>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-2xl leading-relaxed">
              Spatial multi-dimensional analysis of the 180-claim subrogation portfolio. High-urgency
              cases cluster in the high-exposure, impending SOL coordinate space. Click any node to
              open the full case dossier.
            </p>
          </div>

          <div className="flex items-center gap-4 text-xs font-mono">
            <div className="text-right">
              <span className="text-[10px] font-semibold text-slate-400 block">Total claims plotted</span>
              <span className="text-base font-bold text-brass-500">{portfolioData?.total_points ?? 180}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 3D Visualization Canvas Container */}
      {isLoading ? (
        <div className="w-full h-[650px] rounded-2xl border border-paper-300 dark:border-navy-800 bg-paper-50 dark:bg-navy-950 flex items-center justify-center font-mono text-xs text-slate-400">
          Loading 3D point cloud vector coordinates...
        </div>
      ) : portfolioData ? (
        <Portfolio3D points={portfolioData.points} />
      ) : null}
    </div>
  );
};
