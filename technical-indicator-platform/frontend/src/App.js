import React, { useState } from 'react';
import StockSearch from './components/StockSearch';
import IndicatorSelector from './components/IndicatorSelector';
import DateRangePicker from './components/DateRangePicker';
import ResultsDashboard from './components/ResultsDashboard';
import { stockAPI } from './services/api';
import './styles/App.css';

function App() {
  const [selectedStock, setSelectedStock] = useState(null);
  const [selectedIndicators, setSelectedIndicators] = useState([]);
  const [dateRange, setDateRange] = useState({
    startDate: new Date(new Date().setMonth(new Date().getMonth() - 6)),
    endDate: new Date()
  });
  const [analysisResults, setAnalysisResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleRunAnalysis = async () => {
    if (!selectedStock || selectedIndicators.length === 0) {
      alert('Please select a stock and at least one indicator');
      return;
    }

    setLoading(true);
    try {
      const response = await stockAPI.runAnalysis({
        symbol: selectedStock.symbol,
        start_date: dateRange.startDate.toISOString().split('T')[0],
        end_date: dateRange.endDate.toISOString().split('T')[0],
        indicators: selectedIndicators
      });
      
      setAnalysisResults(response.data.results);
    } catch (error) {
      console.error('Analysis error:', error);
      alert('Error running analysis. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>Technical Indicator Backtesting Platform</h1>
        <p className="disclaimer">
          ⚠️ Educational purposes only. Past performance does not guarantee future results.
        </p>
      </header>

      <main className="app-main">
        <div className="config-section">
          <div className="config-panel">
            <h2>Configuration</h2>
            
            <StockSearch 
              onSelectStock={setSelectedStock}
              selectedStock={selectedStock}
            />
            
            <DateRangePicker
              dateRange={dateRange}
              onDateRangeChange={setDateRange}
            />
            
            <IndicatorSelector
              selectedIndicators={selectedIndicators}
              onIndicatorChange={setSelectedIndicators}
            />
            
            <button 
              className="analyze-button"
              onClick={handleRunAnalysis}
              disabled={loading || !selectedStock || selectedIndicators.length === 0}
            >
              {loading ? 'Analyzing...' : 'Run Analysis'}
            </button>
          </div>
        </div>

        <div className="results-section">
          {analysisResults && (
            <ResultsDashboard
              results={analysisResults}
              stock={selectedStock}
            />
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>© 2024 Technical Indicator Platform | Not Financial Advice</p>
      </footer>
    </div>
  );
}

export default App;