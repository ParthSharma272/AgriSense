import React, { useState } from 'react';
import ChatBox from './components/ChatBox';
import DataVisualizer from './components/DataVisualizer';
import InsightToggle from './components/InsightToggle';
import './App.css';

function App() {
  const [policyMode, setPolicyMode] = useState(false);
  const [showDataView, setShowDataView] = useState(false);
  const [currentVisualization, setCurrentVisualization] = useState(null);

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <h1 className="gradient-text">🌾 AgriSense 2.0</h1>
            <p className="tagline">Intelligent Agricultural Q&A System for India</p>
          </div>
          <div className="header-controls">
            <InsightToggle 
              enabled={policyMode} 
              onChange={setPolicyMode}
            />
            <button 
              className="view-toggle"
              onClick={() => setShowDataView(!showDataView)}
            >
              {showDataView ? '💬 Chat View' : '📊 Data View'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="app-main">
        <div className={`content-wrapper ${showDataView ? 'data-view' : 'chat-view'}`}>
          {/* Chat Section */}
          <section className={`chat-section ${showDataView ? 'minimized' : ''}`}>
            <ChatBox 
              policyMode={policyMode}
              onVisualizationReceived={setCurrentVisualization}
            />
          </section>

          {/* Data Visualization Section */}
          {showDataView && (
            <section className="data-section animate-slide-in">
              <DataVisualizer visualization={currentVisualization} />
            </section>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>
          Powered by 🤗 Hugging Face • Data from data.gov.in • 
          <span className="gradient-text"> Open Source</span>
        </p>
      </footer>
    </div>
  );
}

export default App;
