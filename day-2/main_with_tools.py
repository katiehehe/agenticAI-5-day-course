"""
Day 2: Personal Agent Twin with MCP Tools
==========================================

This version adds tools to your agent via the Model Context Protocol (MCP).
We'll use web search as an example - you can swap in other tools!
"""

from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()

# ==============================================================================
# Define Custom Tools (MCP-style)
# ==============================================================================

@tool("web_search")
def web_search(query: str) -> str:
    """
    Search the web for information.
    
    Args:
        query: The search query string
        
    Returns:
        Search results as a string
    """
    # This is a placeholder - in production, you'd use a real search API
    # Options: Brave Search, Serper, Google Custom Search, etc.
    
    # For demo purposes:
    return f"""
    Search results for: {query}
    
    [Note: This is a demo tool. To use real web search, add an API key for:
     - Brave Search: https://brave.com/search/api/
     - Serper: https://serper.dev/
     - Or other search providers]
    
    Example results would appear here...
    """

@tool("calculator")
def calculator(expression: str) -> str:
    """
    Perform mathematical calculations.
    
    Args:
        expression: A mathematical expression to evaluate (e.g., "2 + 2")
        
    Returns:
        The result of the calculation
    """
    try:
        # Safe evaluation of mathematical expressions
        result = eval(expression, {"__builtins__": {}}, {})
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"

# ==============================================================================
# Create Agent with Tools
# ==============================================================================

llm = LLM(
    model="openai/gpt-4o-mini",
    temperature=0.7,
)

my_agent_with_tools = Agent(
    role="Personal Digital Twin with Tools",
    goal="Answer questions about me and use tools when needed",
    
    backstory="""
    You are the digital twin of a student learning AI and CrewAI.
    
    Here's what you know about me:
    - I'm a student in the MIT IAP NANDA course
    - I'm learning about AI agents and tools
    - I love technology and problem-solving
    - My favorite programming language is Python
    
    NEW CAPABILITIES - You have access to tools:
    - web_search: Search the internet for information
    - calculator: Perform mathematical calculations
    
    WHEN TO USE TOOLS:
    - Use web_search when you need current information or facts you don't know
    - Use calculator for any mathematical operations
    - Use your own knowledge for questions about me (from backstory)
    
    Be smart about tool selection - only use tools when truly needed!
    """,
    
    tools=[web_search, calculator],  # 🛠️ Add tools here!
    llm=llm,
    verbose=True,
)

# ==============================================================================
# Interactive Chat with Tools
# ==============================================================================

def chat_with_tools():
    """Interactive chat that demonstrates tool usage"""
    
    print("\n" + "="*70)
    print("🛠️  Personal Agent Twin with TOOLS")
    print("="*70)
    print("\nI can now use tools to help answer your questions!")
    print("\nAvailable tools:")
    print("  🔍 web_search - Search the internet")
    print("  🔢 calculator - Perform calculations")
    print("\nType 'quit' to exit.\n")
    
    while True:
        question = input("❓ You: ").strip()
        
        if question.lower() in ['quit', 'exit', 'bye', 'q']:
            print("\n👋 Goodbye!\n")
            break
        
        if not question:
            continue
        
        # Create task
        task = Task(
            description=f"""
            Answer this question: {question}
            
            Use your tools when appropriate:
            - Use web_search for current events, facts you don't know
            - Use calculator for math problems
            - Use your own knowledge for personal questions
            """,
            expected_output="A clear answer, using tools if necessary",
            agent=my_agent_with_tools,
        )
        
        # Create and run crew
        crew = Crew(
            agents=[my_agent_with_tools],
            tasks=[task],
            verbose=True,
        )
        
        print()
        result = crew.kickoff()
        print(f"\n🤖 Agent Twin: {result}\n")

# ==============================================================================
# Main Execution
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🛠️  DAY 2: TOOL-ENABLED AGENT")
    print("="*70)
    print("\nNew in this version:")
    print("✅ Tools: Agent can use external tools")
    print("✅ Web Search: Find current information")
    print("✅ Calculator: Perform calculations")
    print("\n" + "="*70 + "\n")
    
    try:
        chat_with_tools()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")

# ==============================================================================
# Tool Tips for Students
# ==============================================================================
"""
TESTING TOOLS:

1. Ask something that requires calculation:
   You: "What's 123 * 456?"
   
2. Ask something that needs web search:
   You: "What's the weather like today?"
   
3. Ask something personal:
   You: "What am I learning?"
   (Should answer from backstory without tools)

ADDING YOUR OWN TOOLS:

@tool("my_tool")
def my_tool(param: str) -> str:
    '''Tool description here'''
    # Your code here
    return result

Then add to agent:
    tools=[web_search, calculator, my_tool]

REAL MCP TOOLS:

For production, integrate real MCP servers:
- Spotify: Music search and recommendations
- Weather: Current weather data
- GitHub: Repository information
- And many more at: github.com/modelcontextprotocol/servers
"""

