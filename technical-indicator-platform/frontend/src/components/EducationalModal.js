import React from 'react';

const EducationalModal = ({ isOpen, onClose, indicator }) => {
  if (!isOpen || !indicator) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        <h2>{indicator.display_name}</h2>
        <p className="indicator-category">{indicator.category}</p>
        <p>{indicator.description}</p>
        <div className="modal-section">
          <h3>How it works</h3>
          <p>{indicator.explanation}</p>
        </div>
        <div className="modal-section">
          <h3>Formula</h3>
          <code>{indicator.formula}</code>
        </div>
        <div className="modal-disclaimer">
          <strong>Remember:</strong> No indicator is perfect. Always use multiple indicators 
          and consider market conditions before making trading decisions.
        </div>
      </div>
    </div>
  );
};

export default EducationalModal;