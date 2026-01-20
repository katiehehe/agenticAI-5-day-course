"""
Personal Agent Twin - A simple CrewAI example for students
============================================================

This script creates an AI agent that acts as your "digital twin" - 
an agent that knows about you and can answer questions on your behalf.

Students: Edit the BACKSTORY section to create your own personal agent!
"""

from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==============================================================================
# STEP 1: Configure your LLM (Language Model)
# ==============================================================================
# This is the "brain" of your agent. We're using OpenAI's GPT-4o-mini.
# Make sure to set your OPENAI_API_KEY in the .env file!

llm = LLM(
    model="openai/gpt-4o-mini",  # The AI model to use
    temperature=0.7,              # Controls creativity (0.0 = focused, 1.0 = creative)
)


# ==============================================================================
# STEP 2: Create your Personal Agent Twin
# ==============================================================================
# This is where you define WHO your agent is and WHAT it knows about you.
# 
# ✏️ STUDENTS: EDIT THIS SECTION TO MAKE IT YOUR OWN!
# Change the backstory to reflect YOUR interests, personality, and background!

my_agent_twin = Agent(
    role="Personal Digital Twin",
    
    goal="Answer questions about me accurately and helpfully",
    
    # 👇 EDIT THIS BACKSTORY - Make it about YOU!
    backstory="""
    You are the digital twin of a student learning AI and CrewAI.
    
    Here's what you know about me:
    - I'm a student learning about AI agents and automation
    - I'm interested in technology, coding, and building cool projects
    - I love experimenting with new tools like CrewAI
    - My favorite programming language is Python
    - I enjoy problem-solving and creative thinking
    
    When someone asks about me, you provide friendly, accurate information
    based on what I've told you about myself. You're helpful, enthusiastic,
    and represent me well in conversations.
    """,
    
    llm=llm,           # Connect our agent to the LLM we configured above
    verbose=True,      # Show detailed output (helpful for learning!)
)


# ==============================================================================
# STEP 3: Create a Task for your Agent
# ==============================================================================
# Tasks tell your agent WHAT to do. This task answers questions about you.

answer_question_task = Task(
    description="""
    Answer the following question about me: {question}
    
    Use the information from your backstory to provide an accurate,
    friendly, and helpful response. If you don't know something,
    say so honestly rather than making it up.
    """,
    
    expected_output="A clear, friendly answer to the question about me",
    
    agent=my_agent_twin,  # Assign this task to our agent
)


# ==============================================================================
# STEP 4: Create a Crew (Team of Agents)
# ==============================================================================
# A Crew manages your agents and tasks. Even with one agent, we need a Crew!

my_crew = Crew(
    agents=[my_agent_twin],           # List of agents (just one for now)
    tasks=[answer_question_task],     # List of tasks to complete
    verbose=True,                     # Show detailed execution logs
)


# ==============================================================================
# STEP 5: Run your Agent Twin!
# ==============================================================================
# This is where the magic happens - we "kickoff" the crew to complete the task.

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🤖 Personal Agent Twin - Ready to answer questions about you!")
    print("="*70 + "\n")
    
    # Example questions you can ask your agent twin
    # 👇 STUDENTS: Try different questions or make it interactive!
    
    question = "What are my interests and what am I learning?"
    
    print(f"❓ Question: {question}\n")
    
    # Run the crew with the question as input
    result = my_crew.kickoff(inputs={"question": question})
    
    print("\n" + "="*70)
    print("✅ Agent Response:")
    print("="*70)
    print(result)
    print("\n")
    
    # 🎯 BONUS CHALLENGE for students:
    # Can you make this interactive? Try using input() to ask custom questions!
    # Example:
    # while True:
    #     user_question = input("\nAsk a question about me (or 'quit' to exit): ")
    #     if user_question.lower() == 'quit':
    #         break
    #     result = my_crew.kickoff(inputs={"question": user_question})
    #     print(f"\n🤖 Answer: {result}\n")

