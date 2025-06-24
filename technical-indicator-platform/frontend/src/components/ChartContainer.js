import React, { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import { stockAPI } from '../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const ChartContainer = ({ stock, results }) => {
  const [priceData, setPriceData] = useState(null);
  const [chartType, setChartType] = useState('performance');

  useEffect(() => {
    if (stock) {
      fetchPriceData();
    }
  }, [stock]);

  const fetchPriceData = async () => {
    try {
      const response = await stockAPI.getStockData(stock.id);
      setPriceData(response.data);
    } catch (error) {
      console.error('Error fetching price data:', error);
    }
  };

  const getPriceChartData = () => {
    if (!priceData) return null;

    return {
      labels: priceData.map(d => new Date(d.date).toLocaleDateString()),
      datasets: [
        {
          label: 'Close Price',
          data: priceData.map(d => d.close_price),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.1)',
          tension: 0.1
        }
      ]
    };
  };

  const getPerformanceChartData = () => {
    return {
      labels: results.map(r => r.indicator_name),
      datasets: [
        {
          label: 'Success Rate (%)',
          data: results.map(r => r.success_rate),
          backgroundColor: results.map(r => 
            r.success_rate > 50 ? 'rgba(75, 192, 75, 0.8)' : 'rgba(192, 75, 75, 0.8)'
          ),
        }
      ]
    };
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: chartType === 'price' ? `${stock.symbol} Price History` : 'Indicator Performance Comparison'
      }
    },
    scales: {
      y: {
        beginAtZero: chartType !== 'price'
      }
    }
  };

  return (
    <div className="chart-container">
      <div className="chart-controls">
        <button 
          className={chartType === 'performance' ? 'active' : ''}
          onClick={() => setChartType('performance')}
        >
          Performance Comparison
        </button>
        <button 
          className={chartType === 'price' ? 'active' : ''}
          onClick={() => setChartType('price')}
        >
          Price History
        </button>
      </div>

      <div className="chart-wrapper">
        {chartType === 'price' && priceData ? (
          <Line data={getPriceChartData()} options={chartOptions} />
        ) : (
          <Bar data={getPerformanceChartData()} options={chartOptions} />
        )}
      </div>
    </div>
  );
};

export default ChartContainer;