"""
Day 4: Google A2A Protocol - Agent-to-Agent Communication
==========================================================

This implements a simple version of Google's Agent-to-Agent (A2A)
communication protocol for standardized agent interaction.
"""

from crewai import Agent, Task, Crew, LLM
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
import json

from dotenv import load_dotenv

load_dotenv()

# ==============================================================================
# A2A Message Format
# ==============================================================================

class A2AMessage(BaseModel):
    """Standardized A2A message format"""
    protocol: str = "a2a"
    version: str = "1.0"
    from_agent: str
    to_agent: str
    message_type: str  # "request", "response", "notification"
    task: Dict[str, Any]
    timestamp: str = datetime.now().isoformat()
    correlation_id: Optional[str] = None

class A2ACapabilities(BaseModel):
    """Agent capabilities declaration"""
    agent_id: str
    capabilities: list[str]
    expertise_domains: list[str]
    available: bool = True
    max_concurrent_tasks: int = 1

# ==============================================================================
# Create A2A-Enabled Agents
# ==============================================================================

llm = LLM(model="openai/gpt-4o-mini", temperature=0.7)

# Agent 1: Research Specialist
research_agent = Agent(
    role="Research Specialist",
    goal="Handle research requests via A2A protocol",
    backstory="""
    You are a research specialist that communicates via the A2A protocol.
    You handle research tasks and return structured responses.
    """,
    llm=llm,
    verbose=True,
)

# Agent 2: Analysis Specialist
analysis_agent = Agent(
    role="Analysis Specialist",
    goal="Handle analysis requests via A2A protocol",
    backstory="""
    You are an analysis specialist that communicates via the A2A protocol.
    You analyze data and return structured insights.
    """,
    llm=llm,
    verbose=True,
)

# Agent 3: Synthesis Coordinator
coordinator_agent = Agent(
    role="Coordinator",
    goal="Coordinate multiple agents via A2A protocol",
    backstory="""
    You are a coordinator that manages multi-agent workflows.
    You delegate tasks and synthesize results using A2A protocol.
    """,
    llm=llm,
    verbose=True,
)

# ==============================================================================
# A2A Communication Functions
# ==============================================================================

def create_a2a_request(
    from_agent: str,
    to_agent: str,
    task_description: str,
    task_input: Dict[str, Any],
    correlation_id: Optional[str] = None
) -> A2AMessage:
    """Create an A2A request message"""
    return A2AMessage(
        from_agent=from_agent,
        to_agent=to_agent,
        message_type="request",
        task={
            "description": task_description,
            "input": task_input,
            "deadline": (datetime.now()).isoformat()
        },
        correlation_id=correlation_id or datetime.now().isoformat()
    )

def process_a2a_request(message: A2AMessage, agent: Agent) -> A2AMessage:
    """Process an A2A request and return response"""
    
    print(f"\n📨 Processing A2A Request:")
    print(f"   From: {message.from_agent}")
    print(f"   To: {message.to_agent}")
    print(f"   Task: {message.task['description']}")
    print()
    
    # Create task from A2A message
    task = Task(
        description=message.task['description'],
        expected_output="Structured response to the request",
        agent=agent,
    )
    
    # Execute task
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=False,
    )
    
    result = crew.kickoff()
    
    # Create A2A response
    response = A2AMessage(
        from_agent=message.to_agent,
        to_agent=message.from_agent,
        message_type="response",
        task={
            "description": message.task['description'],
            "result": str(result),
            "status": "completed"
        },
        correlation_id=message.correlation_id
    )
    
    return response

# ==============================================================================
# Multi-Agent A2A Workflow
# ==============================================================================

def a2a_workflow(question: str):
    """
    Solve a question using A2A coordination
    
    Args:
        question: The question to answer
        
    Returns:
        Final synthesized answer
    """
    
    print("\n" + "="*70)
    print("🌐 A2A PROTOCOL COORDINATION")
    print("="*70)
    print(f"\nQuestion: {question}\n")
    
    # Step 1: Coordinator creates research request
    research_request = create_a2a_request(
        from_agent="coordinator",
        to_agent="research_specialist",
        task_description=f"Research the following question: {question}",
        task_input={"question": question},
        correlation_id="task-001"
    )
    
    print("📤 Coordinator → Research Specialist")
    print(f"   Request: {research_request.task['description']}\n")
    
    # Step 2: Research agent processes request
    research_response = process_a2a_request(research_request, research_agent)
    
    print("📥 Research Specialist → Coordinator")
    print(f"   Status: {research_response.task['status']}")
    print(f"   Result preview: {research_response.task['result'][:100]}...\n")
    
    # Step 3: Coordinator creates analysis request
    analysis_request = create_a2a_request(
        from_agent="coordinator",
        to_agent="analysis_specialist",
        task_description=f"Analyze these research findings: {research_response.task['result']}",
        task_input={"research": research_response.task['result']},
        correlation_id="task-002"
    )
    
    print("📤 Coordinator → Analysis Specialist")
    print(f"   Request: Analyze research findings\n")
    
    # Step 4: Analysis agent processes request
    analysis_response = process_a2a_request(analysis_request, analysis_agent)
    
    print("📥 Analysis Specialist → Coordinator")
    print(f"   Status: {analysis_response.task['status']}")
    print(f"   Result preview: {analysis_response.task['result'][:100]}...\n")
    
    # Step 5: Coordinator synthesizes
    synthesis_task = Task(
        description=f"""
        Synthesize the following into a final answer for: {question}
        
        Research findings:
        {research_response.task['result']}
        
        Analysis insights:
        {analysis_response.task['result']}
        
        Provide a comprehensive, well-structured answer.
        """,
        expected_output="Final synthesized answer",
        agent=coordinator_agent,
    )
    
    print("🔄 Coordinator: Synthesizing results...\n")
    
    crew = Crew(
        agents=[coordinator_agent],
        tasks=[synthesis_task],
        verbose=False,
    )
    
    final_result = crew.kickoff()
    
    print("="*70)
    print("✅ FINAL ANSWER (via A2A Coordination)")
    print("="*70)
    print(final_result)
    print("="*70 + "\n")
    
    return final_result

# ==============================================================================
# Main Execution
# ==============================================================================

if __name__ == "__main__":
    print("\n🌐 GOOGLE A2A PROTOCOL DEMONSTRATION\n")
    print("This demonstrates standardized agent-to-agent communication.\n")
    
    # Example question
    question = "What are the key trends in artificial intelligence for 2026?"
    
    # Or create your own:
    # question = input("Enter your question: ")
    
    result = a2a_workflow(question)

# ==============================================================================
# Tips for Students
# ==============================================================================
"""
EXPERIMENT WITH:

1. Add more agent types:
   - Create specialist agents for different domains
   - Add agents with different expertise
   
2. Complex workflows:
   - Chain multiple agents together
   - Create branching workflows
   - Implement conditional delegation
   
3. Real A2A integration:
   - Connect to other students' deployed agents
   - Use HTTP to send A2A messages
   - Build an A2A registry service
   
4. Error handling:
   - Handle agent unavailability
   - Implement retries
   - Add timeout handling
   
5. Monitoring:
   - Track message flows
   - Log coordination patterns
   - Measure response times

A2A PROTOCOL BENEFITS:

- Standardized communication format
- Clear task delegation
- Traceable workflows (correlation_id)
- Agent capability discovery
- Interoperability between different agent systems
"""

