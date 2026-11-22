import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppShell } from './components/layout/AppShell';

import { Overview } from './pages/Overview';
import { Claims } from './pages/Claims';
import { CaseDetail } from './pages/CaseDetail';
import { PortfolioExplorer } from './pages/PortfolioExplorer';
import { Assistant } from './pages/Assistant';
import { Reports } from './pages/Reports';
import { DataQuality } from './pages/DataQuality';
import { Settings } from './pages/Settings';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AppShell />}>
            <Route index element={<Overview />} />
            <Route path="claims" element={<Claims />} />
            <Route path="claims/:id" element={<CaseDetail />} />
            <Route path="portfolio" element={<PortfolioExplorer />} />
            <Route path="assistant" element={<Assistant />} />
            <Route path="reports" element={<Reports />} />
            <Route path="data-quality" element={<DataQuality />} />
            <Route path="settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
};
