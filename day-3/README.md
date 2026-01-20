# 🚀 Day 3: Deploy + REST API + Testbed

**Goal:** Deploy your agent to the cloud and expose it via REST API for the NANDA testbed

## 📚 What You'll Learn

- Cloud deployment (Render or Railway)
- Building REST APIs with FastAPI
- Environment variable management in production
- API endpoint design for AI agents
- Testing in NANDA testbed
- Health checks and monitoring

## 🎯 Today's Objectives

- [ ] Create a FastAPI wrapper for your agent
- [ ] Set up deployment on Render or Railway
- [ ] Configure environment variables in production
- [ ] Expose standard endpoints for NANDA
- [ ] Test your deployed agent
- [ ] Submit to NANDA testbed

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies for Day 3:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation

### 2. Test Locally

```bash
# Run the FastAPI server
uvicorn main:app --reload

# In another terminal, test it:
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are your interests?"}'
```

### 3. Deploy to Cloud

Follow the deployment guide below for Render or Railway.

## 📖 Understanding the Architecture

### Before (Day 1-2): Local Agent
```
You → Terminal → Agent → LLM → Response
```

### After (Day 3): Cloud API
```
Anyone → HTTP → FastAPI → Agent → LLM → JSON Response
```

Now your agent can be accessed from anywhere!

## 🏗️ Building the REST API

### main.py - FastAPI Application

Key endpoints you'll implement:

1. **GET /health** - Health check
   ```json
   {"status": "healthy", "model": "gpt-4o-mini"}
   ```

2. **POST /query** - Ask your agent
   ```json
   {
     "question": "What are you learning?"
   }
   ```
   
   Response:
   ```json
   {
     "answer": "I'm learning about AI agents...",
     "agent_id": "your-agent-name",
     "timestamp": "2026-01-20T10:30:00Z"
   }
   ```

3. **GET /info** - Agent information
   ```json
   {
     "name": "Your Agent Twin",
     "version": "1.0",
     "capabilities": ["memory", "tools"],
     "creator": "Your Name"
   }
   ```

## 🌐 Deployment Options

### Option A: Render (Recommended)

1. **Create render.yaml**:
   ```yaml
   services:
     - type: web
       name: my-agent-twin
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

2. **Connect GitHub**:
   - Go to [render.com](https://render.com)
   - Connect your GitHub repository
   - Render will auto-deploy on push!

3. **Set Environment Variables**:
   - Add `OPENAI_API_KEY` in Render dashboard
   - Add any other API keys you need

### Option B: Railway

1. **Create railway.json**:
   ```json
   {
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

2. **Deploy**:
   ```bash
   # Install Railway CLI
   npm install -g railway
   
   # Login and deploy
   railway login
   railway init
   railway up
   ```

3. **Set Environment Variables**:
   ```bash
   railway variables set OPENAI_API_KEY=sk-your-key
   ```

## 📁 Project Structure

```
day-3/
├── main.py                  # FastAPI application
├── agent.py                 # Your agent logic (from Day 2)
├── requirements.txt         # Dependencies
├── render.yaml             # Render configuration
├── railway.json            # Railway configuration
├── Procfile                # Alternative deployment config
├── .env.example            # Example environment variables
└── README.md               # This file!
```

## 🔧 API Implementation Details

### Input Validation

```python
from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str
    user_id: str = "anonymous"
    max_turns: int = 5

class QueryResponse(BaseModel):
    answer: str
    agent_id: str
    timestamp: str
    confidence: float = 1.0
```

### Error Handling

```python
from fastapi import HTTPException

@app.post("/query")
async def query_agent(request: QueryRequest):
    try:
        result = crew.kickoff(inputs={"question": request.question})
        return QueryResponse(
            answer=str(result),
            agent_id="my-agent-twin",
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 🧪 Testing Your Deployed Agent

### 1. Health Check

```bash
curl https://your-app.render.com/health
```

### 2. Query Test

```bash
curl -X POST https://your-app.render.com/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Tell me about yourself"}'
```

### 3. Load Test (Optional)

```bash
# Install hey
brew install hey  # macOS
# or download from https://github.com/rakyll/hey

# Test with 100 requests
hey -n 100 -m POST \
  -H "Content-Type: application/json" \
  -d '{"question":"test"}' \
  https://your-app.render.com/query
```

## 🏃 NANDA Testbed Integration

### Required Endpoints

Your agent must implement:

1. **POST /query** - Main query endpoint
   - Input: `{"question": string}`
   - Output: `{"answer": string, ...}`

2. **GET /health** - Health check
   - Output: `{"status": "healthy"}`

3. **GET /info** - Agent metadata
   - Output: Agent name, capabilities, version

### Submitting to NANDA

1. Deploy your agent and get the URL
2. Test all endpoints
3. Submit to NANDA index with:
   - Agent name
   - API endpoint URL
   - Capabilities description
   - Your name/team

## 🐛 Troubleshooting

**Deployment fails:**
- Check your requirements.txt is complete
- Verify Python version (3.10+ required)
- Check build logs in Render/Railway dashboard

**Agent times out:**
- Increase timeout in Render/Railway settings
- Optimize your agent (reduce max_turns)
- Consider caching responses

**Environment variables not working:**
- Double-check variable names in dashboard
- Restart service after adding variables
- Check for typos in variable names

**Port errors:**
- Use `$PORT` environment variable, not hardcoded port
- Render/Railway assign ports dynamically

## 💰 Cost Considerations

### Free Tiers

**Render:**
- 750 hours/month free
- Sleeps after 15 min inactivity
- 512 MB RAM

**Railway:**
- $5 free credit/month
- No sleep (better for demos)
- 512 MB RAM

**OpenAI:**
- Pay per token
- GPT-4o-mini is very affordable (~$0.15/1M tokens)

### Optimization Tips

1. **Use GPT-4o-mini** instead of GPT-4
2. **Cache common responses** 
3. **Set max_tokens limit**
4. **Rate limit your API**

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Render Deployment Guide](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app/)
- [Uvicorn Server](https://www.uvicorn.org/)

## ✅ Day 3 Checklist

Before moving to Day 4, make sure you:
- [ ] FastAPI server runs locally
- [ ] All endpoints return correct responses
- [ ] Successfully deployed to Render or Railway
- [ ] Environment variables configured
- [ ] Public URL is accessible
- [ ] Tested all endpoints on deployed version
- [ ] Submitted to NANDA testbed

## 🎯 Next Steps

Ready for Day 4? Head to `../day-4/` to build multi-agent coordination!

---

**Pro Tip:** Keep your deployed agent running - you'll use it for Day 4's multi-agent coordination!

