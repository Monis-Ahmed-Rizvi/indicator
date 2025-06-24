import React, { useState } from 'react';
import { stockAPI } from '../services/api';

const StockSearch = ({ onSelectStock, selectedStock }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setSearching(true);
    try {
      const response = await stockAPI.searchStock(searchQuery);
      onSelectStock(response.data);
      setSearchQuery('');
    } catch (error) {
      alert('Stock not found. Please try another symbol.');
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="stock-search">
      <h3>Select Stock</h3>
      <form onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Enter stock symbol (e.g., AAPL)"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value.toUpperCase())}
          disabled={searching}
        />
        <button type="submit" disabled={searching}>
          {searching ? 'Searching...' : 'Search'}
        </button>
      </form>
      
      {selectedStock && (
        <div className="selected-stock">
          <h4>{selectedStock.symbol}</h4>
          <p>{selectedStock.company_name}</p>
          <p className="sector">{selectedStock.sector}</p>
        </div>
      )}
    </div>
  );
};

export default StockSearch;