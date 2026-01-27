"""
Personal Agent Twin with Memory and Tools - Day 2
==================================================

This extends Day 1 by adding:
- Memory (Short-Term, Long-Term, Entity, Contextual)
- Tools from CrewAI collection
- Custom tool creation

Students: Follow the steps to add memory and tools to your agent!
"""

from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
from crewai_tools import (
    DirectoryReadTool, 
    FileReadTool, 
    SerperDevTool, 
    WebsiteSearchTool, 
    YoutubeVideoSearchTool,
    YoutubeChannelSearchTool,
    DallETool,
    VisionTool,
    BrowserbaseLoadTool
)
from pydantic import BaseModel, Field
from typing import Type
from dotenv import load_dotenv
import os

load_dotenv()

# Set CrewAI storage to local directory to avoid macOS permission issues
# This creates a 'memory' directory in the current project folder
memory_dir = os.path.join(os.getcwd(), 'memory')
os.environ['CREWAI_STORAGE_DIR'] = memory_dir
os.makedirs(memory_dir, exist_ok=True)

# ==============================================================================
# STEP 1: Configure your LLM (same as Day 1)
# ==============================================================================

llm = LLM(
    model="openai/gpt-4o-mini",
    temperature=0.7,
)

# ==============================================================================
# STEP 2: Define Tools
# ==============================================================================

# Tool 1: Directory Reading
# Allows agent to browse directories
docs_tool = DirectoryReadTool(directory='./blog-posts')

# Tool 2: File Reading
# Allows agent to read specific files
file_tool = FileReadTool()

# Tool 3: Website Search (RAG-based)
# Searches and extracts content from websites
# Note: May fail on macOS due to ChromaDB permission issues
web_rag_tool = None
try:
    web_rag_tool = WebsiteSearchTool()
except PermissionError as e:
    print(f"Warning: WebsiteSearchTool initialization failed (permission error): {e}")
    print("This tool will be skipped. If you need it, check macOS Full Disk Access settings.")
except Exception as e:
    print(f"Warning: WebsiteSearchTool initialization failed: {e}")
    print("This tool will be skipped.")

# Tool 4: YouTube Video Search (RAG-based)
# Searches within video transcripts
# Note: May not work due to YouTube API limitations or ChromaDB permission issues
youtube_video_tool = None
try:
    youtube_video_tool = YoutubeVideoSearchTool()
except PermissionError as e:
    print(f"Warning: YoutubeVideoSearchTool initialization failed (permission error): {e}")
    print("This tool will be skipped. If you need it, check macOS Full Disk Access settings.")
except Exception as e:
    print(f"Warning: YoutubeVideoSearchTool initialization failed: {e}")
    print("This tool will be skipped.")

# Tool 5: YouTube Channel Search (RAG-based)
# Searches within YouTube channel content
youtube_channel_tool = None
try:
    youtube_channel_tool = YoutubeChannelSearchTool()
except PermissionError as e:
    print(f"Warning: YoutubeChannelSearchTool initialization failed (permission error): {e}")
    print("This tool will be skipped. If you need it, check macOS Full Disk Access settings.")
except Exception as e:
    print(f"Warning: YoutubeChannelSearchTool initialization failed: {e}")
    print("This tool will be skipped.")

# Tool 6: DALL-E Tool
# Generates images using DALL-E API (uses your OPENAI_API_KEY)
dalle_tool = DallETool()

# Tool 7: Vision Tool
# Analyzes and describes existing images using OpenAI's Vision API
vision_tool = VisionTool()

# Tool 8: Browserbase Load Tool
# Interacts with and extracts data from web browsers
# Requires BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID in .env
# Get keys at: https://www.browserbase.com
browserbase_tool = None
browserbase_api_key = os.getenv('BROWSERBASE_API_KEY')
browserbase_project_id = os.getenv('BROWSERBASE_PROJECT_ID')
if browserbase_api_key and browserbase_project_id:
    try:
        browserbase_tool = BrowserbaseLoadTool(
            api_key=browserbase_api_key,
            project_id=browserbase_project_id
        )
    except Exception as e:
        print(f"Warning: BrowserbaseLoadTool initialization failed: {e}")
        print("This tool will be skipped. Install browserbase package if needed: pip install browserbase")

# Tool 9: Web Search (requires SERPER_API_KEY in .env)
# Get free key at: https://serper.dev
search_tool = None
if os.getenv('SERPER_API_KEY'):
    search_tool = SerperDevTool()

# ==============================================================================
# STEP 3: Create Custom Tool
# ==============================================================================

class CalculatorInput(BaseModel):
    """Input schema for Calculator tool."""
    expression: str = Field(..., description="Mathematical expression to evaluate")

class CalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = "Performs mathematical calculations. Use for any math operations."
    args_schema: Type[BaseModel] = CalculatorInput
    
    def _run(self, expression: str) -> str:
        """Execute the calculation."""
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"

calculator_tool = CalculatorTool()

# ==============================================================================
# STEP 4: Create Agent with Memory and Tools
# ==============================================================================

# Collect available tools (only add tools that initialized successfully)
available_tools = [
    docs_tool,
    file_tool,
    dalle_tool,
    vision_tool,
    calculator_tool
]

# Add RAG tools if they initialized successfully
if web_rag_tool:
    available_tools.append(web_rag_tool)
if youtube_video_tool:
    available_tools.append(youtube_video_tool)
if youtube_channel_tool:
    available_tools.append(youtube_channel_tool)

# Add optional tools if API keys are configured
if search_tool:
    available_tools.append(search_tool)
if browserbase_tool:
    available_tools.append(browserbase_tool)

my_agent_twin = Agent(
    role="Personal Digital Twin with Memory and Tools",
    
    goal="Answer questions about me, remember our conversations, and use tools when needed",
    
    # Edit this backstory to make it your own!
    backstory="""
    You are the digital twin of a student learning AI and CrewAI.
    
    Here's what you know about me:
    - I'm a student in the MIT IAP NANDA course
    - I'm learning about AI agents, memory systems, and tools
    - I love experimenting with new AI technologies
    - My favorite programming language is Python
    - I'm building this as part of a 5-day intensive course
    
    MEMORY CAPABILITIES:
    You have four types of memory:
    
    1. Short-Term Memory (RAG-based): Stores recent conversation context
       - Remembers what we discussed in this session
       - Uses vector embeddings for retrieval
    
    2. Long-Term Memory: Persists important information across sessions
       - Remembers facts that should survive restarts
       - Stores learnings and preferences
    
    3. Entity Memory (RAG-based): Tracks people, places, concepts
       - Remembers entities mentioned in conversations
       - Stores relationships and attributes
    
    4. Contextual Memory: Combines all memory types
       - Fuses short-term, long-term, and entity memory
       - Provides coherent, context-aware responses
    
    TOOL CAPABILITIES:
    - DirectoryReadTool: Browse and list files in directories
    - FileReadTool: Read specific files
    - WebsiteSearchTool: Search and extract content from websites (RAG)
    - YoutubeVideoSearchTool: Search within video transcripts (RAG)
    - YoutubeChannelSearchTool: Search within YouTube channel content (RAG)
    - DallETool: Generate images using DALL-E - USE THIS when users ask you to create/generate images!
    - VisionTool: Analyze and describe existing images
    - BrowserbaseLoadTool: Extract data from web browsers (if API key configured)
    - SerperDevTool: Web search (if API key configured)
    - Calculator: Perform mathematical calculations
    
    IMPORTANT: When someone asks you to generate, create, or make an image, 
    you MUST use the DallETool. You CAN generate images - don't tell users you can't!
    
    Use tools when you need external information. Use memory to provide
    personalized, context-aware responses.
    """,
    
    tools=available_tools,  # Add tools to agent
    llm=llm,
    verbose=True,
)

# ==============================================================================
# STEP 5: Create Task (same pattern as Day 1)
# ==============================================================================

answer_question_task = Task(
    description="""
    Answer the following question: {question}
    
    Use your memory to recall relevant context from our conversation.
    Use your tools when you need external information or calculations.
    Provide accurate, helpful responses based on your backstory and tools.
    """,
    
    expected_output="A clear, context-aware answer using memory and tools as needed",
    
    agent=my_agent_twin,
)

# ==============================================================================
# STEP 6: Create Crew with Memory Enabled
# ==============================================================================

my_crew = Crew(
    agents=[my_agent_twin],
    tasks=[answer_question_task],
    memory=True,  # This enables all 4 memory types!
    verbose=True,
)

# ==============================================================================
# STEP 7: Run Your Agent Twin with Memory!
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("Personal Agent Twin - Day 2: Memory + Tools")
    print("="*70 + "\n")
    
    # Interactive mode
    print("Ask me questions! I'll remember our conversation and use tools when needed.")
    print("Type 'quit' to exit.\n")
    
    while True:
        question = input("You: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye! I'll remember this conversation.\n")
            break
        
        if not question:
            continue
        
        result = my_crew.kickoff(inputs={"question": question})
        print(f"\nAgent: {result.raw}\n")