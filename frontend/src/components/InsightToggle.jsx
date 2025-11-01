import React from 'react';
import './InsightToggle.css';

const InsightToggle = ({ enabled, onChange }) => {
  return (
    <div className="insight-toggle">
      <label className="toggle-container">
        <input
          type="checkbox"
          checked={enabled}
          onChange={(e) => onChange(e.target.checked)}
        />
        <span className="toggle-slider"></span>
      </label>
      <span className="toggle-label">
        {enabled ? '🎯 Policy Insights ON' : '📊 Data Mode'}
      </span>
      <div className="toggle-description">
        {enabled 
          ? 'Includes policy recommendations and analytical insights'
          : 'Standard data-driven answers'}
      </div>
    </div>
  );
};

export default InsightToggle;
