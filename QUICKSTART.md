# AgriSense 2.0 - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/agrisense.git
cd agrisense

# Run the setup script (Linux/Mac)
chmod +x setup.sh
./setup.sh
```

### Step 2: Get Your Hugging Face API Token

1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Click "New token"
3. Give it a name (e.g., "AgriSense")
4. Select "Read" permission
5. Copy the token

### Step 3: Configure Environment

```bash
# Edit the .env file
cd backend
nano .env  # or use any text editor

# Add your token:
HF_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 4: Initialize AgriSense

```bash
# From backend/ directory
source venv/bin/activate  # On Windows: venv\Scripts\activate
python init_agrisense.py
```

You should see:
```
✓ Sample Data: Created
✓ RAG Pipeline: Initialized
✓ AgriSense 2.0 is ready!
```

### Step 5: Start the Servers

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 6: Open Your Browser

Go to: **http://localhost:5173**

## 🎯 Try These Example Queries

Once AgriSense is running, try asking:

1. **"How did rainfall affect rice yields in Tamil Nadu between 2015-2022?"**
   - This will show the correlation between rainfall and crop yields

2. **"Compare rice production between Tamil Nadu and Karnataka"**
   - You'll see a comparative analysis with visualizations

3. **"Show me rainfall trends over the years"**
   - Gets a time-series line chart

4. **Toggle "Policy Insight Mode"** and ask:
   - "What policy recommendations can improve agricultural resilience?"

## 🔧 Troubleshooting

### Issue: "HF_API_TOKEN not set"
**Solution:** Make sure you've added your token to `backend/.env`

### Issue: "ModuleNotFoundError"
**Solution:** 
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Port already in use"
**Solution:** Kill the process or use a different port:
```bash
# Backend on different port
uvicorn main:app --reload --port 8001

# Frontend on different port
npm run dev -- --port 5174
```

### Issue: Frontend can't connect to backend
**Solution:** Check CORS settings in `backend/.env`:
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

## 📚 Learn More

- **Full Documentation:** See [README.md](README.md)
- **API Documentation:** http://localhost:8000/docs (when backend is running)
- **Architecture Details:** Check the README for system architecture

## 🎨 Customize

### Change the AI Model

Edit `backend/.env`:
```env
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.2
```

### Add Your Own Data

```python
# In backend/init_agrisense.py
# Add your DataFrame and index it:
rag.add_dataframe(
    df=your_dataframe,
    text_column='description',
    metadata_columns=['year', 'state'],
    dataset_name='my_dataset'
)
```

### Modify UI Theme

Edit `frontend/src/index.css` to change colors:
```css
:root {
  --accent-primary: #your-color;
  --accent-secondary: #your-color;
}
```

## 🌟 Next Steps

1. **Add Real Data:** Connect to actual data.gov.in APIs
2. **Deploy:** Use the deployment guide in README.md
3. **Contribute:** Fork and submit PRs!

## 💬 Need Help?

- Check the [Issues](https://github.com/yourusername/agrisense/issues) page
- Read the full [README.md](README.md)
- Email: support@agrisense.io

Happy coding! 🌾
