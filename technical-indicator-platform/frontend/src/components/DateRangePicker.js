import React from 'react';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";

const DateRangePicker = ({ dateRange, onDateRangeChange }) => {
  const handleStartDateChange = (date) => {
    onDateRangeChange({
      ...dateRange,
      startDate: date
    });
  };

  const handleEndDateChange = (date) => {
    onDateRangeChange({
      ...dateRange,
      endDate: date
    });
  };

  const setPresetRange = (months) => {
    const end = new Date();
    const start = new Date();
    start.setMonth(start.getMonth() - months);
    
    onDateRangeChange({
      startDate: start,
      endDate: end
    });
  };

  return (
    <div className="date-range-picker">
      <h3>Select Date Range</h3>
      
      <div className="preset-buttons">
        <button onClick={() => setPresetRange(1)}>1 Month</button>
        <button onClick={() => setPresetRange(3)}>3 Months</button>
        <button onClick={() => setPresetRange(6)}>6 Months</button>
        <button onClick={() => setPresetRange(12)}>1 Year</button>
      </div>
      
      <div className="date-inputs">
        <div>
          <label>Start Date</label>
          <DatePicker
            selected={dateRange.startDate}
            onChange={handleStartDateChange}
            maxDate={dateRange.endDate}
          />
        </div>
        <div>
          <label>End Date</label>
          <DatePicker
            selected={dateRange.endDate}
            onChange={handleEndDateChange}
            minDate={dateRange.startDate}
            maxDate={new Date()}
          />
        </div>
      </div>
    </div>
  );
};

export default DateRangePicker;