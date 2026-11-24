import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import ProductDetailPage from './pages/ProductDetailPage';
import AnalysisDashboardPage from './pages/AnalysisDashboardPage';
import ConflictExplorerPage from './pages/ConflictExplorerPage';
import ConflictDetailPage from './pages/ConflictDetailPage';
import PersonalizedInsightsPage from './pages/PersonalizedInsightsPage';

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/products/:productId" element={<ProductDetailPage />} />
        <Route path="/products/:productId/dashboard" element={<AnalysisDashboardPage />} />
        <Route path="/products/:productId/conflicts" element={<ConflictExplorerPage />} />
        <Route path="/products/:productId/conflicts/:conflictId" element={<ConflictDetailPage />} />
        <Route path="/products/:productId/insights" element={<PersonalizedInsightsPage />} />
        <Route path="/analysis" element={<HomePage />} />
        <Route path="*" element={<div className="min-h-screen bg-gray-950 pt-14 flex items-center justify-center text-gray-500">Page not found</div>} />
      </Routes>
    </BrowserRouter>
  );
}
