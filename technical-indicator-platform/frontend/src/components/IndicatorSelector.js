import React, { useState, useEffect } from 'react';
import { stockAPI } from '../services/api';

const IndicatorSelector = ({ selectedIndicators, onIndicatorChange }) => {
  const [indicators, setIndicators] = useState([]);

  useEffect(() => {
    fetchIndicators();
  }, []);

  const fetchIndicators = async () => {
    try {
      const response = await stockAPI.getIndicators();
      setIndicators(response.data);
    } catch (error) {
      console.error('Error fetching indicators:', error);
    }
  };

  const handleIndicatorToggle = (indicatorName) => {
    if (selectedIndicators.includes(indicatorName)) {
      onIndicatorChange(selectedIndicators.filter(ind => ind !== indicatorName));
    } else {
      onIndicatorChange([...selectedIndicators, indicatorName]);
    }
  };

  return (
    <div className="indicator-selector">
      <h3>Select Indicators</h3>
      <div className="indicator-grid">
        {indicators.map((indicator) => (
          <div key={indicator.name} className="indicator-item">
            <label>
              <input
                type="checkbox"
                checked={selectedIndicators.includes(indicator.name)}
                onChange={() => handleIndicatorToggle(indicator.name)}
              />
              <div className="indicator-info">
                <span className="indicator-name">{indicator.display_name}</span>
                <span className="indicator-category">{indicator.category}</span>
                <span className="indicator-description">{indicator.description}</span>
              </div>
            </label>
          </div>
        ))}
      </div>
    </div>
  );
};

export default IndicatorSelector;