# 🌾 AgriSense 2.0: Intelligent Agricultural Q&A System for India

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![React](https://img.shields.io/badge/react-18.2+-61DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688)

## 🌍 Project Overview

AgriSense 2.0 is an open-source intelligent Q&A system that allows policymakers, researchers, and citizens to ask natural language questions about India's agricultural economy and its relationship with climate patterns.

It directly connects to live data.gov.in datasets, harmonizes their differing formats (CSV, XLS, JSON, PDF), and builds a retrieval-augmented reasoning system (RAG) with automated visualizations — answering questions with data, reasoning, and credibility.

### 🎯 Key Capabilities

- ✅ **Live data ingestion** from multiple government APIs
- ✅ **Intelligent OCR + table parsing** for messy PDF/XLS data
- ✅ **RAG (Retrieval-Augmented Generation)** pipeline using Hugging Face models
- ✅ **Hybrid Query System** — unstructured + structured querying
- ✅ **Auto visualizations** (line charts, maps, tables) based on query type
- ✅ **Transparent reasoning chain** (shows what data sources were used)
- ✅ **Policy Insight Mode** — interprets trends and suggests data-driven policies

---

## 🧩 System Architecture

### 1. Data Layer

| Component | Technology |
|-----------|-----------|
| **Data Sources** | data.gov.in APIs (IMD Rainfall, Crop Production, Agri GDP) |
| **Formats** | CSV, XLS, JSON, PDF |
| **Extraction** | requests, pandas, PaddleOCR, pdfplumber, openpyxl |
| **Normalization** | Schema unification via Pandas + metadata mapping |
| **Storage** | PostgreSQL + TimescaleDB (for time-series) |

### 2. Intelligence Layer

| Module | Technology |
|--------|-----------|
| **Embeddings** | sentence-transformers/all-MiniLM-L6-v2 |
| **Vector Store** | ChromaDB (local persistent DB) |
| **LLM** | Hugging Face Inference API – mistralai/Mixtral-8x7B-Instruct |
| **Query Parsing** | LangChain + SQLGenerator |
| **Reasoning** | RAG pipeline combining structured + unstructured responses |

### 3. Backend Layer

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI |
| **Task Orchestration** | Prefect (for ETL) |
| **Data Access** | SQLAlchemy + Pandas |
| **Visual API** | Matplotlib/Plotly exports as JSON for frontend rendering |

### 4. Frontend Layer

| Component | Technology |
|-----------|-----------|
| **Framework** | React + Vite |
| **Charts** | Plotly.js, Chart.js, Mapbox GL JS (for geo visualizations) |
| **UI Theme** | Dark neon (cyberpunk aesthetic) |
| **Core Features** | Chat + "Data view" toggle (shows sources, tables, and graphs) |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Node.js 18+** and npm
- **PostgreSQL** (optional, for production)
- **Hugging Face API Token** ([Get one here](https://huggingface.co/settings/tokens))

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/agrisense.git
cd agrisense
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your Hugging Face API token
nano .env  # or use your favorite editor
```

**Important:** Add your Hugging Face API token to `.env`:

```env
HF_API_TOKEN=your_huggingface_token_here
```

### 3. Initialize AgriSense

```bash
# Run initialization script to set up RAG pipeline and sample data
python init_agrisense.py
```

This will:
- Create sample datasets (rainfall and crop production)
- Initialize the ChromaDB vector store
- Index sample data into the RAG pipeline

### 4. Start the Backend Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### 5. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Hugging Face API
HF_API_TOKEN=your_huggingface_token_here
HF_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1

# Database (optional for development)
DATABASE_URL=postgresql://user:password@localhost:5432/agrisense

# Data.gov.in API (optional)
DATA_GOV_API_KEY=your_data_gov_api_key_here

# Application Settings
DEBUG=True
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Vector Store
CHROMA_PERSIST_DIR=./chroma_db

# RAG Settings
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.7
```

### Getting API Keys

1. **Hugging Face Token** (Required):
   - Sign up at [huggingface.co](https://huggingface.co)
   - Go to Settings → Access Tokens
   - Create a new token with "Read" permissions

2. **Data.gov.in API Key** (Optional):
   - Visit [data.gov.in](https://data.gov.in)
   - Register and request an API key
   - Used for live data fetching

---

## 💡 Usage Examples

### Example Queries

Try asking AgriSense:

1. **Trend Analysis**:
   - "How did rainfall affect rice yields in Tamil Nadu between 2015-2022?"
   - "Show me the trend in agricultural GDP over the last decade"

2. **State Comparisons**:
   - "Compare crop production across Karnataka, Punjab, and Maharashtra"
   - "Which states have the highest rice production?"

3. **Correlation Analysis**:
   - "Is there a correlation between rainfall and crop yields?"
   - "How does irrigation affect wheat production?"

4. **Policy Insights** (Enable Policy Mode):
   - "What policy changes could improve agricultural resilience?"
   - "Analyze the impact of MSP on farmer income"

### Policy Insight Mode

Toggle **Policy Insight Mode** in the UI to get:
- Analytical reasoning over quantitative results
- Data-driven policy recommendations
- Trend interpretations and suggestions

Example output:
> "Rainfall variability rose by 12% between 2015–2022, while rice yields dropped by 9%.
> **Policy Suggestion:** Incentivize millet diversification to improve yield stability."

---

## 📊 Features Deep Dive

### 1. RAG (Retrieval-Augmented Generation) Pipeline

```python
# Simplified workflow
User Query → Embedding Model → Vector Search (ChromaDB)
    ↓
Retrieved Context + Query → LLM (Mixtral-8x7B)
    ↓
Answer with Sources + Confidence Score
```

**Benefits:**
- Answers grounded in actual data
- Transparent source attribution
- Confidence scoring for reliability

### 2. Automatic Visualization

AgriSense automatically detects the best chart type:

| Query Type | Visualization |
|------------|--------------|
| Time-based trend | Line Chart |
| State comparison | Bar Chart |
| Correlation analysis | Scatter Plot |
| Geographic distribution | Choropleth Map |

### 3. Data Fusion Layer

Combines multiple datasets intelligently:
- Auto-detects common columns for joining
- Time-series alignment
- Correlation analysis
- Aggregation and grouping

---

## 🛠️ Development

### Running Tests

```bash
cd backend
pytest
```

### Code Formatting

```bash
# Format Python code
black .
flake8 .

# Format React code
cd frontend
npm run lint
```

### Building for Production

#### Backend

```bash
cd backend
pip install -r requirements.txt
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### Frontend

```bash
cd frontend
npm run build
# Output will be in frontend/dist/
```

---

## 🌐 Deployment

### Recommended Stack

| Layer | Platform |
|-------|----------|
| **Frontend** | Netlify / Vercel |
| **Backend API** | Render / Railway |
| **Database** | Neon.tech (Free PostgreSQL) |
| **Vector Store** | Railway persistent storage |
| **LLM API** | Hugging Face Inference API (free tier) |

### Deploy to Render

1. Create a new Web Service
2. Connect your GitHub repository
3. Set environment variables
4. Deploy!

### Environment Setup

Make sure to set all required environment variables in your deployment platform:
- `HF_API_TOKEN`
- `DATABASE_URL`
- `DATA_GOV_API_KEY`
- `CORS_ORIGINS`

---

## 📈 Future Enhancements

### Planned Features

- 🌐 **Multilingual support** using IndicBERT
- 🧾 **PDF report generation** from chat sessions
- ⚙️ **Scheduled data refresh** via Prefect
- 🛰️ **Satellite imagery integration** for drought prediction
- 📦 **Redis caching** for faster responses
- 🔔 **Real-time alerts** for agricultural anomalies
- 🤖 **Voice interface** for low-literacy users

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Data Sources**: data.gov.in, IMD, Ministry of Agriculture
- **AI Models**: Hugging Face, Sentence Transformers

---

## 📞 Support

For questions or issues:
- Open an [Issue](https://github.com/yourusername/agrisense/issues)
- Email: support@agrisense.io
- Twitter: [@AgriSenseAI](https://twitter.com/AgriSenseAI)

---

## 🌟 Star History

If you find AgriSense useful, please consider giving it a star ⭐

---

<p align="center">
  <b>Built with ❤️ for Indian Agriculture</b>
  <br>
  <i>Empowering data-driven decisions for a sustainable future</i>
</p>
