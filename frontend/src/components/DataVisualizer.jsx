import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import { FaTable, FaChartLine, FaChartBar, FaMap } from 'react-icons/fa';
import './DataVisualizer.css';

const DataVisualizer = ({ visualization }) => {
  const [activeTab, setActiveTab] = useState('chart');

  useEffect(() => {
    if (visualization) {
      // Default to appropriate tab based on visualization type
      if (visualization.type === 'table') {
        setActiveTab('table');
      } else {
        setActiveTab('chart');
      }
    }
  }, [visualization]);

  if (!visualization) {
    return (
      <div className="data-visualizer empty">
        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <h3>No Visualization Yet</h3>
          <p>Ask a question in the chat to see data visualizations here</p>
          <div className="example-queries">
            <p className="example-title">Try queries like:</p>
            <ul>
              <li>Show rainfall trends over time</li>
              <li>Compare crop yields across states</li>
              <li>Visualize agricultural GDP data</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  const getIcon = (type) => {
    switch (type) {
      case 'line':
        return <FaChartLine />;
      case 'bar':
        return <FaChartBar />;
      case 'map':
        return <FaMap />;
      case 'table':
        return <FaTable />;
      default:
        return <FaChartLine />;
    }
  };

  return (
    <div className="data-visualizer animate-fade-in">
      <div className="visualizer-header">
        <div className="viz-type">
          {getIcon(visualization.type)}
          <span>{visualization.type?.toUpperCase() || 'CHART'}</span>
        </div>
        <div className="viz-tabs">
          <button
            className={`tab-btn ${activeTab === 'chart' ? 'active' : ''}`}
            onClick={() => setActiveTab('chart')}
          >
            📈 Chart
          </button>
          <button
            className={`tab-btn ${activeTab === 'data' ? 'active' : ''}`}
            onClick={() => setActiveTab('data')}
          >
            📋 Data
          </button>
          <button
            className={`tab-btn ${activeTab === 'info' ? 'active' : ''}`}
            onClick={() => setActiveTab('info')}
          >
            ℹ️ Info
          </button>
        </div>
      </div>

      <div className="visualizer-content">
        {activeTab === 'chart' && (
          <div className="chart-container">
            {visualization.data && Object.keys(visualization.data).length > 0 ? (
              <Plot
                data={visualization.data.data || []}
                layout={{
                  ...visualization.data.layout,
                  autosize: true,
                  paper_bgcolor: '#16213e',
                  plot_bgcolor: '#16213e',
                  font: {
                    color: '#e0e0e0'
                  }
                }}
                config={{
                  responsive: true,
                  displayModeBar: true,
                  displaylogo: false
                }}
                style={{ width: '100%', height: '100%' }}
              />
            ) : (
              <div className="no-chart">
                <p>{visualization.message || 'Visualization data not available'}</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'data' && (
          <div className="data-container">
            {visualization.data_summary ? (
              <div className="data-info">
                <div className="info-card">
                  <h4>Dataset Summary</h4>
                  <p><strong>Rows:</strong> {visualization.data_summary.rows || 'N/A'}</p>
                  <p><strong>Columns:</strong> {visualization.data_summary.columns?.length || 0}</p>
                </div>

                {visualization.data_summary.columns && (
                  <div className="info-card">
                    <h4>Columns</h4>
                    <ul className="column-list">
                      {visualization.data_summary.columns.map((col, idx) => (
                        <li key={idx}>
                          <span className="column-name">{col}</span>
                          {visualization.data_summary.numeric_columns?.includes(col) && (
                            <span className="column-badge">numeric</span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {visualization.data_summary.sample_data && (
                  <div className="info-card">
                    <h4>Sample Data</h4>
                    <div className="sample-table">
                      <table>
                        <thead>
                          <tr>
                            {visualization.data_summary.columns.map((col, idx) => (
                              <th key={idx}>{col}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {visualization.data_summary.sample_data.map((row, idx) => (
                            <tr key={idx}>
                              {visualization.data_summary.columns.map((col, colIdx) => (
                                <td key={colIdx}>{row[col]?.toString() || '-'}</td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <p>No data summary available</p>
            )}
          </div>
        )}

        {activeTab === 'info' && (
          <div className="info-container">
            <div className="info-card">
              <h4>Visualization Info</h4>
              <p><strong>Type:</strong> {visualization.type || 'Unknown'}</p>
              <p><strong>Message:</strong> {visualization.message || 'N/A'}</p>
            </div>

            <div className="info-card">
              <h4>About This Visualization</h4>
              <p>
                This visualization was automatically generated based on your query 
                and the available data. The chart type was selected to best represent 
                the data patterns and relationships.
              </p>
            </div>

            <div className="info-card">
              <h4>How to Interpret</h4>
              <ul>
                <li><strong>Line Charts:</strong> Show trends over time</li>
                <li><strong>Bar Charts:</strong> Compare values across categories</li>
                <li><strong>Scatter Plots:</strong> Reveal correlations between variables</li>
                <li><strong>Maps:</strong> Display geographic distributions</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DataVisualizer;
