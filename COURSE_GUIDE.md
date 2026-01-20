# 📘 MIT IAP NANDA - Complete Course Guide

**5-Day AI Agent Development Intensive**

## 👋 Welcome!

This course takes you from zero to deployed AI agent in 5 days. By the end, you'll compete in an agent battle with your fully functional AI assistant!

## 🗓️ Course Schedule

### Day 1: Foundation (Monday)
**Time**: 3-4 hours  
**Focus**: Understanding basics  
**Output**: Working agent on GitHub

### Day 2: Enhancement (Tuesday)
**Time**: 3-4 hours  
**Focus**: Memory and tools  
**Output**: Agent with capabilities

### Day 3: Deployment (Wednesday)
**Time**: 3-4 hours  
**Focus**: Cloud and APIs  
**Output**: Live agent endpoint

### Day 4: Coordination (Thursday)
**Time**: 3-4 hours  
**Focus**: Multi-agent systems  
**Output**: Coordinated agent team

### Day 5: Competition (Friday)
**Time**: 4-5 hours  
**Focus**: Optimization and battle  
**Output**: Battle-ready champion

## 🎯 Learning Path

```
Day 1: Build          → Simple agent that talks
Day 2: Enhance        → Add memory and tools
Day 3: Deploy         → Make it accessible online
Day 4: Coordinate     → Multiple agents working together
Day 5: Compete        → Battle-optimized agent
```

## 📚 What You'll Build

### End of Day 1
- ✅ Personal AI twin agent
- ✅ Can answer questions about you
- ✅ Pushed to GitHub
- ✅ Understanding of agent loop

### End of Day 2
- ✅ Agent with memory
- ✅ 1-2 integrated tools (Spotify, search, etc.)
- ✅ Remembers conversations
- ✅ Can access external data

### End of Day 3
- ✅ Deployed REST API
- ✅ Accessible from anywhere
- ✅ Health checks working
- ✅ Tested in NANDA testbed

### End of Day 4
- ✅ Multiple specialized agents
- ✅ Coordination protocol working
- ✅ A2A communication
- ✅ Team-based problem solving

### End of Day 5
- ✅ Battle-ready agent
- ✅ Optimized for speed and accuracy
- ✅ Advanced tools integrated
- ✅ Competed in agent battle!

## 🛠️ Prerequisites

### Required
- Python 3.10 or higher
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- GitHub account
- Text editor or IDE (VS Code recommended)

### Helpful But Not Required
- Basic Python knowledge
- Command line familiarity
- Git basics
- Web API concepts

## 💰 Cost Estimate

### OpenAI API
- **GPT-4o-mini**: ~$0.15 per 1M tokens
- **Course estimate**: $2-5 total
- **Battle day**: $1-3 depending on usage

### Cloud Hosting
- **Render Free Tier**: Free (with sleep after 15 min)
- **Railway**: $5 free credit

**Total Course Cost: $3-10** (mostly OpenAI usage)

## 📖 Day-by-Day Breakdown

### Day 1: Agent Loop + AI Twin v0

**Morning** (1.5 hours)
- Introduction to AI agents
- Install dependencies
- Set up environment
- Run first agent

**Afternoon** (1.5 hours)
- Customize agent backstory
- Understand agent-task-crew
- Test agent loop (max 5 turns)
- Push to GitHub

**Key Concepts**: Agent, Task, Crew, LLM, Backstory

**Common Issues**:
- API key setup → Check .env file
- Import errors → Run `pip install -r requirements.txt`
- Agent gives wrong answers → Improve backstory

---

### Day 2: Memory + MCP Tools

**Morning** (1.5 hours)
- Enable memory in agent
- Test short-term memory
- Choose MCP tool (Spotify, Weather, etc.)
- Get API credentials

**Afternoon** (1.5 hours)
- Integrate tool
- Test tool usage
- Combine memory + tools
- Add to NANDA index

**Key Concepts**: Memory (short/long-term), MCP, Tools, API integration

**Common Issues**:
- Memory not persisting → Check `memory=True`
- Tools not working → Verify API keys
- Agent not using tools → Make relevant to task

---

### Day 3: Deploy + REST API + Testbed

**Morning** (1.5 hours)
- Build FastAPI wrapper
- Test locally
- Create deployment config
- Set up Render/Railway account

**Afternoon** (1.5 hours)
- Deploy to cloud
- Configure environment variables
- Test public endpoint
- Submit to NANDA testbed

**Key Concepts**: REST API, FastAPI, Deployment, Environment variables

**Common Issues**:
- Deployment fails → Check requirements.txt
- Timeout errors → Increase timeout settings
- Env vars not working → Check dashboard settings

---

### Day 4: Team Coordination Protocol

**Morning** (1.5 hours)
- Debate protocol
- Create opposing agents
- Implement judge
- Test coordination

**Afternoon** (1.5 hours)
- Hierarchical protocol
- Manager-worker pattern
- Google A2A basics
- Cross-team collaboration

**Key Concepts**: Multi-agent systems, Coordination, A2A protocol, Consensus

**Common Issues**:
- Agents disagreeing → Add judge/coordinator
- Too slow → Parallelize where possible
- Communication failing → Check API formats

---

### Day 5: Final Submit + Agent Battle

**Morning** (2 hours)
- Optimize agent for battle
- Add web search tool
- Test across categories
- Benchmark performance

**Afternoon** (2-3 hours)
- Final testing
- Submit to battle
- **AGENT BATTLE!**
- Celebrate and review

**Key Concepts**: Optimization, Performance tuning, Battle strategy

**Common Issues**:
- Too slow → Lower temperature, reduce tools
- Wrong answers → Test more, adjust prompts
- Server crashed → Check logs, restart

## 🏆 Success Metrics

### Technical Goals
- ✅ Working agent that responds accurately
- ✅ Memory and tools functioning
- ✅ Deployed with public endpoint
- ✅ Multi-agent coordination working
- ✅ Battle-ready and tested

### Learning Goals
- ✅ Understand agent architecture
- ✅ Can explain agent loop
- ✅ Know when to use tools vs knowledge
- ✅ Grasp coordination patterns
- ✅ Deployment and API basics

### Portfolio Goals
- ✅ GitHub repo with clear README
- ✅ Deployed agent with public URL
- ✅ Battle participation
- ✅ Project you can showcase

## 💡 Pro Tips

### General
1. **Start simple** - Get basics working first
2. **Test frequently** - Don't wait to find bugs
3. **Read errors** - They usually tell you what's wrong
4. **Ask for help** - Instructors and classmates are here!
5. **Have fun** - Experiment and be creative

### Day 1
- Spend time on a good backstory - it matters!
- Test with different questions
- Make it personal and interesting

### Day 2
- Choose tools relevant to your agent
- Don't add too many tools at once
- Test memory thoroughly

### Day 3
- Test locally before deploying
- Check logs when things go wrong
- Keep endpoint simple and reliable

### Day 4
- Start with 2-3 agents max
- Clear roles prevent confusion
- Test coordination patterns separately

### Day 5
- Accuracy > Speed (but aim for both)
- Test across all categories
- Pre-warm your server before battle
- Stay calm - it's about learning!

## 🐛 Common Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "OpenAI API key not found"
```bash
# Check .env file exists (not env_example.txt)
ls -la .env
# Verify contents
cat .env
```

### "Agent won't use tools"
- Make task description mention tools
- Ensure tool is relevant to question
- Check tool is in agent's tools list

### "Deployment failed"
- Check Python version (3.10+)
- Verify requirements.txt is complete
- Review build logs in dashboard

### "Too slow"
- Lower temperature
- Disable memory if not needed
- Reduce number of tools
- Use gpt-4o-mini instead of gpt-4o

## 📚 Additional Resources

### Official Docs
- [CrewAI Documentation](https://docs.crewai.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Reference](https://platform.openai.com/docs)

### Community
- [CrewAI Discord](https://discord.gg/crewai)
- [NANDA Platform](https://nanda.ai)

### Tools & Services
- [Render](https://render.com/)
- [Railway](https://railway.app/)
- [Serper (Search API)](https://serper.dev/)
- [MCP Servers](https://github.com/modelcontextprotocol/servers)

## ✅ Final Checklist

Before you finish the course:

**Technical**
- [ ] Day 1 agent working
- [ ] Memory and tools integrated
- [ ] Successfully deployed
- [ ] Multi-agent coordination tested
- [ ] Battle participation complete

**Documentation**
- [ ] Code on GitHub
- [ ] README written
- [ ] Comments in code
- [ ] Examples provided

**Learning**
- [ ] Understand agent concepts
- [ ] Can explain to others
- [ ] Ideas for next projects
- [ ] Feedback submitted

## 🎉 Congratulations!

You've completed the MIT IAP NANDA course! You now have:

- Working knowledge of AI agents
- Deployed project in portfolio
- GitHub repo to showcase
- Foundation for future projects
- Network of fellow agent builders

### What's Next?

1. **Improve your agent**
   - Add more tools
   - Better prompts
   - Enhanced coordination

2. **Build something new**
   - Personal assistant
   - Research agent
   - Customer service bot
   - Game-playing agent

3. **Join the community**
   - Share your work
   - Help other learners
   - Stay updated on agent tech

4. **Keep learning**
   - Advanced CrewAI features
   - Other agent frameworks
   - Production deployment
   - AI safety and ethics

---

**Thank you for participating!** 🚀

*Questions? Reach out to course instructors or classmates!*

*Built with ❤️ for MIT IAP 2026*

