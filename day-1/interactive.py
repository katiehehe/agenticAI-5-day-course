
"""
Interactive Personal Agent Twin 

"""

from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==============================================================================
# Configure the LLM
# ==============================================================================

llm = LLM(
    model="openai/gpt-4o-mini",
    temperature=0.7,
)

# ==============================================================================
# Create your Personal Agent Twin
# ==============================================================================

my_agent_twin = Agent(
    role="Personal Digital Twin",
    goal="Answer questions about me accurately and helpfully",
    
    # 👇 EDIT THIS to make it about YOU!
    backstory="""
    You are the digital twin of Katie.

    Here's what you know about me:
    - I'm studying Math and Computer Science
    - I'm passionate about education, learning, and curiosity
    - My favorite language is Python and English
    - I have experience with Python, Java, and C++
    - I'm currently working on a project to build an agentic chatbot
    """,
    
    llm=llm,
    verbose=False,  # Set to False for cleaner chat experience
)

# ==============================================================================
# Interactive Chat Function
# ==============================================================================

def chat_with_twin():
    """Run an interactive chat session with your agent twin"""
    
    print("\n" + "="*70)
    print("🤖 Interactive Personal Agent Twin")
    print("="*70)
    print("\nAsk me anything about myself! Type 'quit', 'exit', or 'bye' to end.\n")
    
    while True:
        # Get user input
        question = input("❓ You: ").strip()
        
        # Check if user wants to quit
        if question.lower() in ['quit', 'exit', 'bye', 'q']:
            print("\n👋 Thanks for chatting! Goodbye!\n")
            break
        
        # Skip empty questions
        if not question:
            continue
        
        # Create a task for this specific question
        task = Task(
            description=f"Answer this question about me: {question}",
            expected_output="A clear, friendly answer",
            agent=my_agent_twin,
        )
        
        # Create a crew and run it
        crew = Crew(
            agents=[my_agent_twin],
            tasks=[task],
            verbose=False,  # Clean output
        )
        
        # Get the response
        print("\n🤖 Agent Twin: ", end="", flush=True)
        result = crew.kickoff()
        print(f"{result}\n")

# ==============================================================================
# Run the Interactive Chat
# ==============================================================================

if __name__ == "__main__":
    try:
        chat_with_twin()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        print("Make sure your .env file is set up with a valid OPENAI_API_KEY!\n")
