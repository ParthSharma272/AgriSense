import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { FaPaperPlane, FaSpinner, FaRobot, FaUser } from 'react-icons/fa';
import './ChatBox.css';

const ChatBox = ({ policyMode, onVisualizationReceived }) => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m AgriSense, your intelligent agricultural assistant. Ask me about India\'s agricultural data, rainfall patterns, crop yields, or policy insights.',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!input.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('/api/chat', {
        query: input,
        include_reasoning: true,
        include_visualization: true,
        policy_mode: policyMode
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.answer,
        sources: response.data.sources,
        confidence: response.data.confidence,
        policyInsights: response.data.policy_insights,
        visualization: response.data.visualization,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Pass visualization to parent
      if (response.data.visualization) {
        onVisualizationReceived(response.data.visualization);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        role: 'assistant',
        content: error.response?.data?.detail || 'Sorry, I encountered an error. Please try again.',
        error: true,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const exampleQuestions = [
    "How did rainfall affect rice yields in Tamil Nadu between 2015-2022?",
    "Compare crop production across Karnataka, Punjab, and Maharashtra",
    "What is the trend in agricultural GDP over the last decade?",
    "Show me rainfall patterns across different states"
  ];

  const handleExampleClick = (question) => {
    setInput(question);
  };

  return (
    <div className="chatbox">
      <div className="chat-header">
        <div className="status-indicator">
          <span className="status-dot"></span>
          <span>AgriSense Active</span>
        </div>
        {policyMode && (
          <div className="policy-badge">
            <span>🎯 Policy Insight Mode</span>
          </div>
        )}
      </div>

      <div className="messages-container">
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`message ${message.role} ${message.error ? 'error' : ''} animate-slide-in`}
          >
            <div className="message-icon">
              {message.role === 'user' ? <FaUser /> : <FaRobot />}
            </div>
            <div className="message-content">
              <ReactMarkdown>{message.content}</ReactMarkdown>
              
              {message.sources && message.sources.length > 0 && (
                <div className="sources">
                  <p className="sources-title">📚 Sources:</p>
                  <ul>
                    {message.sources.map((source, idx) => (
                      <li key={idx}>
                        {source.dataset || 'Government Dataset'} 
                        {source.row_id && ` (ID: ${source.row_id})`}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {message.confidence !== undefined && (
                <div className="confidence-bar">
                  <span className="confidence-label">Confidence:</span>
                  <div className="confidence-track">
                    <div 
                      className="confidence-fill" 
                      style={{ width: `${message.confidence * 100}%` }}
                    />
                  </div>
                  <span className="confidence-value">
                    {(message.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              )}

              {message.policyInsights && (
                <div className="policy-insights">
                  <p className="insights-title">🎯 Policy Insights:</p>
                  <ReactMarkdown>{message.policyInsights}</ReactMarkdown>
                </div>
              )}

              <span className="timestamp">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
          </div>
        ))}

        {loading && (
          <div className="message assistant loading">
            <div className="message-icon">
              <FaRobot />
            </div>
            <div className="message-content">
              <FaSpinner className="spinner" />
              <span>Analyzing data...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {messages.length === 1 && (
        <div className="example-questions animate-fade-in">
          <p className="examples-title">Try asking:</p>
          <div className="examples-grid">
            {exampleQuestions.map((question, index) => (
              <button
                key={index}
                className="example-btn"
                onClick={() => handleExampleClick(question)}
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about agricultural data, rainfall, crops, or policies..."
          disabled={loading}
          className="chat-input"
        />
        <button 
          type="submit" 
          disabled={loading || !input.trim()}
          className="send-btn"
        >
          {loading ? <FaSpinner className="spinner" /> : <FaPaperPlane />}
        </button>
      </form>
    </div>
  );
};

export default ChatBox;
