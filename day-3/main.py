"""
Day 3: Agent REST API with FastAPI
===================================

This creates a REST API for your agent that can be deployed to the cloud.
Anyone can now interact with your agent via HTTP!
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv
import os

from crewai import Agent, Task, Crew, LLM

# Load environment variables
load_dotenv()

# ==============================================================================
# FastAPI Application Setup
# ==============================================================================

app = FastAPI(
    title="Personal Agent Twin API",
    description="REST API for interacting with your personal AI agent",
    version="1.0.0"
)

# Enable CORS (allows requests from web browsers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# Request/Response Models
# ==============================================================================

class QueryRequest(BaseModel):
    """Input model for agent queries"""
    question: str
    user_id: str = "anonymous"
    max_turns: int = 5
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are your interests?",
                "user_id": "user123",
                "max_turns": 5
            }
        }

class QueryResponse(BaseModel):
    """Output model for agent responses"""
    answer: str
    agent_id: str
    timestamp: str
    processing_time: float = 0.0

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model: str
    version: str
    timestamp: str

class InfoResponse(BaseModel):
    """Agent information"""
    name: str
    version: str
    capabilities: list[str]
    creator: str
    description: str

# ==============================================================================
# Agent Setup
# ==============================================================================

# Initialize LLM
llm = LLM(
    model="openai/gpt-4o-mini",
    temperature=0.7,
)

# Create agent
agent_twin = Agent(
    role="Personal Digital Twin API",
    goal="Answer questions accurately via REST API",
    
    backstory="""
    You are a personal AI agent accessible via REST API.
    
    About your creator:
    - Student in MIT IAP NANDA course
    - Learning AI agents and deployment
    - Interested in technology and innovation
    - Building cool projects with CrewAI
    
    You provide helpful, accurate responses through an API interface.
    Keep responses concise but informative.
    """,
    
    llm=llm,
    verbose=False,  # Set to True for debugging
)

# ==============================================================================
# API Endpoints
# ==============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Personal Agent Twin API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "info": "/info",
            "query": "/query (POST)"
        },
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse, tags=["Status"])
async def health_check():
    """
    Health check endpoint
    
    Returns the current status of the API and agent.
    """
    return HealthResponse(
        status="healthy",
        model="gpt-4o-mini",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )

@app.get("/info", response_model=InfoResponse, tags=["Agent"])
async def agent_info():
    """
    Get agent information
    
    Returns metadata about the agent and its capabilities.
    """
    return InfoResponse(
        name="Personal Agent Twin",
        version="1.0.0",
        capabilities=["conversation", "memory", "tools", "api-access"],
        creator="MIT IAP NANDA Student",
        description="A personal AI agent that can answer questions about its creator"
    )

@app.post("/query", response_model=QueryResponse, tags=["Agent"])
async def query_agent(request: QueryRequest):
    """
    Query the agent
    
    Send a question to the agent and get a response.
    
    Args:
        request: QueryRequest with question and optional parameters
        
    Returns:
        QueryResponse with the agent's answer
    """
    start_time = datetime.now()
    
    try:
        # Create task for this query
        task = Task(
            description=f"Answer this question: {request.question}",
            expected_output="A clear, concise answer",
            agent=agent_twin,
        )
        
        # Create crew and execute
        crew = Crew(
            agents=[agent_twin],
            tasks=[task],
            verbose=False,
        )
        
        result = crew.kickoff()
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        return QueryResponse(
            answer=str(result),
            agent_id="personal-agent-twin",
            timestamp=end_time.isoformat(),
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@app.get("/stats", tags=["Status"])
async def get_stats():
    """
    Get API statistics (optional endpoint)
    
    Returns basic statistics about API usage.
    """
    return {
        "total_queries": "Not implemented",
        "uptime": "Not implemented",
        "average_response_time": "Not implemented",
        "note": "Implement with a database for production use"
    }

# ==============================================================================
# Error Handlers
# ==============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return {
        "error": "Endpoint not found",
        "message": "This endpoint does not exist. Check /docs for available endpoints.",
        "available_endpoints": ["/", "/health", "/info", "/query"]
    }

# ==============================================================================
# Startup Event
# ==============================================================================

@app.on_event("startup")
async def startup_event():
    """Run when the API starts"""
    print("\n" + "="*70)
    print("🚀 Personal Agent Twin API Starting...")
    print("="*70)
    print(f"\n✅ Model: {llm.model}")
    print("✅ Agent: Initialized")
    print("✅ Endpoints: Ready")
    print("\n📚 Documentation: http://localhost:8000/docs")
    print("="*70 + "\n")

# ==============================================================================
# Run Instructions
# ==============================================================================
"""
LOCAL DEVELOPMENT:
    uvicorn main:app --reload
    
    Then visit:
    - http://localhost:8000 (API root)
    - http://localhost:8000/docs (Interactive documentation)
    - http://localhost:8000/health (Health check)

PRODUCTION DEPLOYMENT:
    Render: Automatically detected
    Railway: Automatically detected
    Manual: uvicorn main:app --host 0.0.0.0 --port $PORT

TESTING:
    # Health check
    curl http://localhost:8000/health
    
    # Query agent
    curl -X POST http://localhost:8000/query \
      -H "Content-Type: application/json" \
      -d '{"question": "What are you learning?"}'
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

