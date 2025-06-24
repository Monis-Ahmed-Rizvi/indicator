import React from 'react';
import ComparisonTable from './ComparisonTable';
import ChartContainer from './ChartContainer';

const ResultsDashboard = ({ results, stock }) => {
  return (
    <div className="results-dashboard">
      <h2>Analysis Results for {stock.symbol}</h2>
      
      <div className="results-summary">
        <div className="summary-cards">
          {results.map((result) => (
            <div key={result.id} className="summary-card">
              <h3>{result.indicator_name}</h3>
              <div className="metric">
                <span className="label">Success Rate</span>
                <span className={`value ${result.success_rate > 50 ? 'positive' : 'negative'}`}>
                  {result.success_rate.toFixed(2)}%
                </span>
              </div>
              <div className="metric">
                <span className="label">Avg Return</span>
                <span className={`value ${result.avg_return > 0 ? 'positive' : 'negative'}`}>
                  {result.avg_return.toFixed(2)}%
                </span>
              </div>
              <div className="metric">
                <span className="label">Total Signals</span>
                <span className="value">{result.total_signals}</span>
              </div>
              <div className="metric">
                <span className="label">Max Drawdown</span>
                <span className="value negative">{result.max_drawdown.toFixed(2)}%</span>
              </div>
              <div className="metric">
                <span className="label">Sharpe Ratio</span>
                <span className="value">{result.sharpe_ratio.toFixed(2)}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <ComparisonTable results={results} />
      
      <ChartContainer stock={stock} results={results} />
    </div>
  );
};

export default ResultsDashboard;