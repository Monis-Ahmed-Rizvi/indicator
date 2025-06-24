import React, { useState } from 'react';

const ComparisonTable = ({ results }) => {
  const [sortBy, setSortBy] = useState('success_rate');
  const [sortOrder, setSortOrder] = useState('desc');

  const sortedResults = [...results].sort((a, b) => {
    const aValue = a[sortBy];
    const bValue = b[sortBy];
    
    if (sortOrder === 'desc') {
      return bValue - aValue;
    } else {
      return aValue - bValue;
    }
  });

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  return (
    <div className="comparison-table">
      <h3>Indicator Performance Ranking</h3>
      <table>
        <thead>
          <tr>
            <th>Indicator</th>
            <th onClick={() => handleSort('success_rate')} className="sortable">
              Success Rate {sortBy === 'success_rate' && (sortOrder === 'desc' ? '↓' : '↑')}
            </th>
            <th onClick={() => handleSort('avg_return')} className="sortable">
              Avg Return {sortBy === 'avg_return' && (sortOrder === 'desc' ? '↓' : '↑')}
            </th>
            <th onClick={() => handleSort('total_signals')} className="sortable">
              Signals {sortBy === 'total_signals' && (sortOrder === 'desc' ? '↓' : '↑')}
            </th>
            <th onClick={() => handleSort('sharpe_ratio')} className="sortable">
              Sharpe Ratio {sortBy === 'sharpe_ratio' && (sortOrder === 'desc' ? '↓' : '↑')}
            </th>
            <th onClick={() => handleSort('max_drawdown')} className="sortable">
              Max Drawdown {sortBy === 'max_drawdown' && (sortOrder === 'desc' ? '↓' : '↑')}
            </th>
          </tr>
        </thead>
        <tbody>
          {sortedResults.map((result) => (
            <tr key={result.id}>
              <td>{result.indicator_name}</td>
              <td className={result.success_rate > 50 ? 'positive' : 'negative'}>
                {result.success_rate.toFixed(2)}%
              </td>
              <td className={result.avg_return > 0 ? 'positive' : 'negative'}>
                {result.avg_return.toFixed(2)}%
              </td>
              <td>{result.total_signals}</td>
              <td>{result.sharpe_ratio.toFixed(2)}</td>
              <td className="negative">{result.max_drawdown.toFixed(2)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ComparisonTable;