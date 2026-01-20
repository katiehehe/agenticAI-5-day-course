"""
Day 2: Personal Agent Twin with Memory
========================================

This version adds memory to your agent, allowing it to remember
past conversations and provide more personalized responses.
"""

from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv

load_dotenv()

# ==============================================================================
# Configure the LLM
# ==============================================================================

llm = LLM(
    model="openai/gpt-4o-mini",
    temperature=0.7,
)

# ==============================================================================
# Create Agent with Memory Awareness
# ==============================================================================

my_agent_twin = Agent(
    role="Personal Digital Twin with Memory",
    goal="Answer questions about me and remember our conversations",
    
    backstory="""
    You are the digital twin of a student learning AI and CrewAI.
    
    Here's what you know about me:
    - I'm a student in the MIT IAP NANDA course
    - I'm learning about AI agents, memory, and tools
    - I love experimenting with new AI technologies
    - My favorite programming language is Python
    - I'm building this as part of a 5-day intensive course
    
    IMPORTANT: You have memory capabilities! This means:
    - You can remember facts from our previous conversations
    - You build a better understanding of me over time
    - You reference past discussions when relevant
    - You learn and adapt based on our interactions
    
    When someone asks about me, provide accurate information based on
    both your backstory AND what you've learned from our conversations.
    """,
    
    llm=llm,
    verbose=True,
)

# ==============================================================================
# Interactive Chat with Memory
# ==============================================================================

def chat_with_memory():
    """Interactive chat that demonstrates memory capabilities"""
    
    print("\n" + "="*70)
    print("🧠 Personal Agent Twin with MEMORY")
    print("="*70)
    print("\nI can now remember our conversations!")
    print("Try telling me something, then asking about it later.\n")
    print("Type 'quit' to exit.\n")
    
    # Create crew with memory enabled
    crew = None
    
    while True:
        question = input("❓ You: ").strip()
        
        if question.lower() in ['quit', 'exit', 'bye', 'q']:
            print("\n👋 I'll remember this conversation! Goodbye!\n")
            break
        
        if not question:
            continue
        
        # Create task for this question
        task = Task(
            description=f"""
            Answer this question or respond to this statement: {question}
            
            Use your memory of our past conversations along with your backstory.
            If this is new information about me, acknowledge it and remember it.
            If this references something we discussed before, show that you remember.
            """,
            expected_output="A clear, personalized response that shows awareness of conversation history",
            agent=my_agent_twin,
        )
        
        # Create or use crew with memory enabled
        if crew is None:
            crew = Crew(
                agents=[my_agent_twin],
                tasks=[task],
                memory=True,  # 🧠 This enables memory!
                verbose=True,
            )
        else:
            # Update tasks for existing crew
            crew.tasks = [task]
        
        # Get response
        print("\n🤖 Agent Twin: ", end="", flush=True)
        result = crew.kickoff()
        print(f"{result}\n")

# ==============================================================================
# Main Execution
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧠 DAY 2: MEMORY-ENABLED AGENT")
    print("="*70)
    print("\nNew in this version:")
    print("✅ Memory: Agent remembers past conversations")
    print("✅ Personalization: Gets better over time")
    print("✅ Context awareness: References previous discussions")
    print("\n" + "="*70 + "\n")
    
    try:
        chat_with_memory()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Your conversation is saved! Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        print("Make sure your .env file is set up correctly!\n")

# ==============================================================================
# Memory Tips for Students
# ==============================================================================
"""
TESTING MEMORY:

1. Tell the agent something:
   You: "My birthday is in June"
   
2. Ask about it later:
   You: "When is my birthday?"
   
3. Restart the program and see if it remembers!

MEMORY TYPES:

- Short-term: Current conversation
- Long-term: Persists across sessions (when configured)

EXPERIMENT:
Try restarting the program and asking "What have we discussed?"
"""

