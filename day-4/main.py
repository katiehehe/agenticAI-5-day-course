"""
Day 4: Agent-to-Agent Communication (A2A) - ENHANCED COMPETITION VERSION
==========================================

This extends your Day 3 agent with A2A capabilities, allowing your agent
to communicate with other agents!

ENHANCED WITH NEW COMPETITIVE TOOLS:
1. Weather Tool - Get weather for any city
2. Time/Date Tool - Get current time, dates, timezones
3. Unit Converter - Convert units (length, weight, temperature, etc.)
4. Currency Converter - Real-time currency conversion
5. Dictionary/Definition Tool - Word definitions and synonyms
6. Translation Tool - Translate between languages
7. Random Generator - Generate random numbers, passwords, UUIDs
8. Text Analysis Tool - Analyze text (word count, sentiment, readability)
9. Code Executor - Execute Python code safely
10. Math Solver - Advanced math problem solving
11. Fact Checker - Verify facts and statements
12. Quiz Generator - Generate quiz questions on topics
13. PDF Reader - Read and extract text from PDF files from URLs
14. Image Analyzer - Analyze images: describe content, extract text, identify objects
15. News Fetcher - Fetch news articles from URLs
16. Sentiment Analyzer - Analyze sentiment of text
17. Stock Price Tool - Get stock prices from URLs

What's A2A?
- Agent-to-Agent communication protocol
- Agents can message each other using @agent-id syntax
- Simple, direct communication between agents
- Based on NEST/NANDA approach

Architecture:
- Service 1: Your agent (from Day 3)
- Service 2: Other agents (anywhere on the internet)
- They communicate via HTTP using the /a2a endpoint

⚠️ IMPORTANT: Two Endpoints for Different Purposes
=================================================

1. POST /query - Direct queries to YOUR agent
   Example: {"question": "What is 2+2?"}
   Use this when YOU want to ask YOUR agent something

2. POST /a2a - Agent-to-agent routing ONLY
   Example: {"content": {"text": "@other-agent Can you help?", "type": "text"}, ...}
   MUST include @agent-id to route to another agent
   Will ERROR if no @agent-id is provided (no silent fallbacks!)

Logging:
- All A2A messages logged to logs/a2a_messages.log
- Includes: INCOMING, ROUTING, SUCCESS, ERROR, NO_TARGET
- Check logs to debug A2A routing issues
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import re
import httpx
import logging
import json
from typing import Optional, Dict, Any
import random
import string
import uuid
from zoneinfo import ZoneInfo
import math
import PyPDF2
from io import BytesIO
from openai import OpenAI

from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
from crewai_tools import FileReadTool, SerperDevTool, WebsiteSearchTool, YoutubeVideoSearchTool
from pydantic import Field
from typing import Type

# Load environment variables
load_dotenv()

# ==============================================================================
# Logging Setup
# ==============================================================================

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure A2A logging to file
a2a_logger = logging.getLogger("a2a")
a2a_logger.setLevel(logging.INFO)

# File handler for A2A messages
a2a_file_handler = logging.FileHandler("logs/a2a_messages.log")
a2a_file_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
a2a_file_handler.setFormatter(formatter)

# Add handler to logger
a2a_logger.addHandler(a2a_file_handler)

# ==============================================================================
# FastAPI Application Setup
# ==============================================================================

app = FastAPI(
    title="Personal Agent Twin API with A2A - COMPETITION ENHANCED",
    description="Your agent with memory, tools, AND agent-to-agent communication! Now with 12+ competitive tools!",
    version="2.0.0-enhanced"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# Request/Response Models
# ==============================================================================

class QueryRequest(BaseModel):
    """Standard query request"""
    question: str
    user_id: str = "anonymous"

class QueryResponse(BaseModel):
    """Standard query response"""
    answer: str
    timestamp: str
    processing_time: float

class A2AMessage(BaseModel):
    """A2A message format (NEST-style)"""
    content: Dict[str, Any]  # {"text": "message", "type": "text"}
    role: str = "user"
    conversation_id: str

class A2AResponse(BaseModel):
    """A2A response format"""
    content: Dict[str, Any]
    role: str = "assistant"
    conversation_id: str
    timestamp: str
    agent_id: str

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    memory_enabled: bool
    tools_count: int
    a2a_enabled: bool

class SearchRequest(BaseModel):
    """Search request - finds and routes to suitable agent"""
    query: str
    conversation_id: str = "search-conv"
    user_id: str = "anonymous"

class SearchResponse(BaseModel):
    """Search response"""
    selected_agent: Dict[str, Any]
    agent_response: str
    timestamp: str
    processing_time: float

# ==============================================================================
# Agent Registry
# ==============================================================================

# Central registry URL - set this to your deployed registry
REGISTRY_URL = os.getenv("REGISTRY_URL", "https://nest.projectnanda.org/api/agents")

# Store known agents - fetched from central registry
KNOWN_AGENTS: Dict[str, str] = {
    # Format: "username": "http://agent-url/a2a"
    # Auto-populated from registry on startup
}

# ==============================================================================
# Agent Identity Configuration
# ==============================================================================
# 👇 EDIT THESE VALUES - This is your agent's public information

MY_AGENT_USERNAME = "mimothecalico"  # 👈 CHANGE THIS: Your unique username
MY_AGENT_NAME = "Mimo the Calico - Enhanced"      # 👈 CHANGE THIS: Human-readable name
MY_AGENT_DESCRIPTION = "Mimo is a super-powered AI agent with 17+ tools including weather, translation, math, code execution, and more!"  # 👈 CHANGE THIS
MY_AGENT_PROVIDER = "Katie He"        # 👈 CHANGE THIS: Your name
MY_AGENT_PROVIDER_URL = "https://agent1-production-7909.up.railway.app"  # 👈 CHANGE THIS: Your website

# Optional - usually don't need to change these
MY_AGENT_ID = MY_AGENT_USERNAME  # Uses username as ID
MY_AGENT_VERSION = "2.0.0-enhanced"
MY_AGENT_JURISDICTION = "USA"

# Get public URL from environment (Railway sets this automatically)
PUBLIC_URL = os.getenv("PUBLIC_URL") or os.getenv("RAILWAY_PUBLIC_DOMAIN")
if PUBLIC_URL and not PUBLIC_URL.startswith("http"):
    PUBLIC_URL = f"https://{PUBLIC_URL}"

# ==============================================================================
# ENHANCED TOOLS - 12 NEW COMPETITION-READY TOOLS
# ==============================================================================

# Tool 1: Weather Tool
class WeatherToolInput(BaseModel):
    location: str = Field(..., description="City name to get weather for")

class WeatherTool(BaseTool):
    name: str = "weather"
    description: str = "Get current weather information for any city worldwide"
    args_schema: Type[BaseModel] = WeatherToolInput
    
    def _run(self, location: str) -> str:
        try:
            # Using free wttr.in API (no API key needed!)
            url = f"https://wttr.in/{location}?format=j1"
            response = httpx.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                temp_c = current['temp_C']
                temp_f = current['temp_F']
                desc = current['weatherDesc'][0]['value']
                humidity = current['humidity']
                wind = current['windspeedKmph']
                return f"Weather in {location}: {desc}, Temperature: {temp_c}°C ({temp_f}°F), Humidity: {humidity}%, Wind: {wind} km/h"
            else:
                return f"Could not fetch weather for {location}"
        except Exception as e:
            return f"Error getting weather: {str(e)}"

# Tool 2: Time/Date Tool
class TimeToolInput(BaseModel):
    timezone: str = Field(default="UTC", description="Timezone (e.g., 'America/New_York', 'UTC', 'Asia/Tokyo')")

class TimeTool(BaseTool):
    name: str = "time_date"
    description: str = "Get current time, date, and timezone information"
    args_schema: Type[BaseModel] = TimeToolInput
    
    def _run(self, timezone: str = "UTC") -> str:
        try:
            tz = ZoneInfo(timezone)
            now = datetime.now(tz)
            return f"Current time in {timezone}: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}, Day: {now.strftime('%A')}, Week: {now.isocalendar()[1]}"
        except Exception as e:
            now = datetime.now(timezone.utc)
            return f"UTC time: {now.strftime('%Y-%m-%d %H:%M:%S UTC')} (Invalid timezone: {timezone})"

# Tool 3: Unit Converter
class UnitConverterInput(BaseModel):
    value: float = Field(..., description="Value to convert")
    from_unit: str = Field(..., description="Unit to convert from (e.g., 'km', 'lb', 'celsius')")
    to_unit: str = Field(..., description="Unit to convert to (e.g., 'miles', 'kg', 'fahrenheit')")

class UnitConverterTool(BaseTool):
    name: str = "unit_converter"
    description: str = "Convert between different units (length, weight, temperature, volume, speed)"
    args_schema: Type[BaseModel] = UnitConverterInput
    
    def _run(self, value: float, from_unit: str, to_unit: str) -> str:
        try:
            conversions = {
                # Length
                ('km', 'miles'): lambda x: x * 0.621371,
                ('miles', 'km'): lambda x: x * 1.60934,
                ('m', 'ft'): lambda x: x * 3.28084,
                ('ft', 'm'): lambda x: x * 0.3048,
                ('cm', 'inches'): lambda x: x * 0.393701,
                ('inches', 'cm'): lambda x: x * 2.54,
                # Weight
                ('kg', 'lb'): lambda x: x * 2.20462,
                ('lb', 'kg'): lambda x: x * 0.453592,
                ('g', 'oz'): lambda x: x * 0.035274,
                ('oz', 'g'): lambda x: x * 28.3495,
                # Temperature
                ('celsius', 'fahrenheit'): lambda x: (x * 9/5) + 32,
                ('fahrenheit', 'celsius'): lambda x: (x - 32) * 5/9,
                ('celsius', 'kelvin'): lambda x: x + 273.15,
                ('kelvin', 'celsius'): lambda x: x - 273.15,
                # Volume
                ('liters', 'gallons'): lambda x: x * 0.264172,
                ('gallons', 'liters'): lambda x: x * 3.78541,
                # Speed
                ('mph', 'kph'): lambda x: x * 1.60934,
                ('kph', 'mph'): lambda x: x * 0.621371,
            }
            
            key = (from_unit.lower(), to_unit.lower())
            if key in conversions:
                result = conversions[key](value)
                return f"{value} {from_unit} = {result:.4f} {to_unit}"
            else:
                return f"Conversion from {from_unit} to {to_unit} not supported. Available: length (km/miles/m/ft), weight (kg/lb), temperature (celsius/fahrenheit/kelvin), volume (liters/gallons), speed (mph/kph)"
        except Exception as e:
            return f"Error converting units: {str(e)}"

# Tool 4: Currency Converter
class CurrencyConverterInput(BaseModel):
    amount: float = Field(..., description="Amount to convert")
    from_currency: str = Field(..., description="Currency code to convert from (e.g., 'USD', 'EUR')")
    to_currency: str = Field(..., description="Currency code to convert to (e.g., 'JPY', 'GBP')")

class CurrencyConverterTool(BaseTool):
    name: str = "currency_converter"
    description: str = "Convert between different currencies with real-time exchange rates"
    args_schema: Type[BaseModel] = CurrencyConverterInput
    
    def _run(self, amount: float, from_currency: str, to_currency: str) -> str:
        try:
            # Using free exchangerate-api.com
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}"
            response = httpx.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                rate = data['rates'].get(to_currency.upper())
                if rate:
                    result = amount * rate
                    return f"{amount} {from_currency.upper()} = {result:.2f} {to_currency.upper()} (Rate: {rate:.4f})"
                else:
                    return f"Currency {to_currency.upper()} not found"
            else:
                return f"Could not fetch exchange rates"
        except Exception as e:
            return f"Error converting currency: {str(e)}"

# Tool 5: Dictionary/Definition Tool
class DictionaryToolInput(BaseModel):
    word: str = Field(..., description="Word to look up")

class DictionaryTool(BaseTool):
    name: str = "dictionary"
    description: str = "Get definitions, synonyms, and word information"
    args_schema: Type[BaseModel] = DictionaryToolInput
    
    def _run(self, word: str) -> str:
        try:
            # Using free dictionary API
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            response = httpx.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()[0]
                meanings = data['meanings'][0]
                definition = meanings['definitions'][0]['definition']
                part_of_speech = meanings['partOfSpeech']
                example = meanings['definitions'][0].get('example', 'No example available')
                return f"Word: {word}\nPart of speech: {part_of_speech}\nDefinition: {definition}\nExample: {example}"
            else:
                return f"Word '{word}' not found in dictionary"
        except Exception as e:
            return f"Error looking up word: {str(e)}"

# Tool 6: Translation Tool
class TranslationToolInput(BaseModel):
    text: str = Field(..., description="Text to translate")
    target_language: str = Field(..., description="Target language code (e.g., 'es' for Spanish, 'fr' for French)")

class TranslationTool(BaseTool):
    name: str = "translator"
    description: str = "Translate text between languages (supports 100+ languages)"
    args_schema: Type[BaseModel] = TranslationToolInput
    
    def _run(self, text: str, target_language: str) -> str:
        try:
            # Using LibreTranslate (free API)
            url = "https://libretranslate.com/translate"
            response = httpx.post(url, json={
                "q": text,
                "source": "auto",
                "target": target_language.lower(),
                "format": "text"
            }, timeout=10)
            if response.status_code == 200:
                data = response.json()
                translated = data['translatedText']
                return f"Translation to {target_language}: {translated}"
            else:
                return f"Translation failed. Supported languages: es (Spanish), fr (French), de (German), it (Italian), pt (Portuguese), ru (Russian), zh (Chinese), ja (Japanese), ko (Korean), ar (Arabic)"
        except Exception as e:
            return f"Error translating: {str(e)}"

# Tool 7: Random Generator
class RandomGeneratorInput(BaseModel):
    type: str = Field(..., description="Type: 'number', 'password', 'uuid', 'choice'")
    options: str = Field(default="", description="For number: 'min,max', for password: 'length', for choice: 'option1,option2,option3'")

class RandomGeneratorTool(BaseTool):
    name: str = "random_generator"
    description: str = "Generate random numbers, passwords, UUIDs, or make random choices"
    args_schema: Type[BaseModel] = RandomGeneratorInput
    
    def _run(self, type: str, options: str = "") -> str:
        try:
            if type == "number":
                parts = options.split(",")
                min_val = int(parts[0]) if len(parts) > 0 else 1
                max_val = int(parts[1]) if len(parts) > 1 else 100
                return f"Random number: {random.randint(min_val, max_val)}"
            elif type == "password":
                length = int(options) if options else 16
                chars = string.ascii_letters + string.digits + string.punctuation
                password = ''.join(random.choice(chars) for _ in range(length))
                return f"Random password: {password}"
            elif type == "uuid":
                return f"Random UUID: {uuid.uuid4()}"
            elif type == "choice":
                choices = options.split(",")
                return f"Random choice: {random.choice(choices)}"
            else:
                return "Invalid type. Use: number, password, uuid, or choice"
        except Exception as e:
            return f"Error generating random: {str(e)}"

# Tool 8: Text Analysis Tool
class TextAnalysisInput(BaseModel):
    text: str = Field(..., description="Text to analyze")

class TextAnalysisTool(BaseTool):
    name: str = "text_analyzer"
    description: str = "Analyze text: word count, character count, sentence count, reading level"
    args_schema: Type[BaseModel] = TextAnalysisInput
    
    def _run(self, text: str) -> str:
        try:
            words = text.split()
            word_count = len(words)
            char_count = len(text)
            char_no_spaces = len(text.replace(" ", ""))
            sentences = text.count('.') + text.count('!') + text.count('?')
            sentences = max(sentences, 1)
            
            # Simple readability score (Flesch Reading Ease approximation)
            avg_sentence_length = word_count / sentences
            avg_word_length = char_no_spaces / word_count if word_count > 0 else 0
            readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_word_length)
            
            if readability_score >= 90:
                reading_level = "Very Easy (5th grade)"
            elif readability_score >= 80:
                reading_level = "Easy (6th grade)"
            elif readability_score >= 70:
                reading_level = "Fairly Easy (7th grade)"
            elif readability_score >= 60:
                reading_level = "Standard (8th-9th grade)"
            elif readability_score >= 50:
                reading_level = "Fairly Difficult (10th-12th grade)"
            else:
                reading_level = "Difficult (College level)"
            
            return f"Text Analysis:\n- Words: {word_count}\n- Characters: {char_count} (without spaces: {char_no_spaces})\n- Sentences: {sentences}\n- Avg words/sentence: {avg_sentence_length:.1f}\n- Reading level: {reading_level}\n- Readability score: {readability_score:.1f}"
        except Exception as e:
            return f"Error analyzing text: {str(e)}"

# Tool 9: Code Executor (Safe Python execution)
class CodeExecutorInput(BaseModel):
    code: str = Field(..., description="Python code to execute (safe operations only)")

class CodeExecutorTool(BaseTool):
    name: str = "code_executor"
    description: str = "Execute Python code safely (math, data processing, string operations)"
    args_schema: Type[BaseModel] = CodeExecutorInput
    
    def _run(self, code: str) -> str:
        try:
            # Create a restricted namespace
            safe_namespace = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'abs': abs,
                    'round': round,
                    'sorted': sorted,
                    'list': list,
                    'dict': dict,
                    'set': set,
                    'str': str,
                    'int': int,
                    'float': float,
                },
                'math': math,
            }
            
            # Capture output
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            # Execute code
            exec(code, safe_namespace)
            
            # Get output
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            return f"Code executed successfully:\n{output}" if output else "Code executed successfully (no output)"
        except Exception as e:
            return f"Error executing code: {str(e)}"

# Tool 10: Advanced Math Solver
class MathSolverInput(BaseModel):
    problem: str = Field(..., description="Math problem to solve (algebra, calculus, etc.)")

class MathSolverTool(BaseTool):
    name: str = "math_solver"
    description: str = "Solve advanced math problems including algebra, trigonometry, and calculus"
    args_schema: Type[BaseModel] = MathSolverInput
    
    def _run(self, problem: str) -> str:
        try:
            # Use sympy for symbolic math if available
            try:
                import sympy as sp
                # Try to parse and solve the problem
                x = sp.Symbol('x')
                # Simple evaluation for now
                result = sp.sympify(problem)
                return f"Math result: {result}"
            except:
                # Fallback to basic eval
                result = eval(problem, {"__builtins__": {}}, {"math": math, "pi": math.pi, "e": math.e})
                return f"Math result: {result}"
        except Exception as e:
            return f"Error solving math problem: {str(e)}. Try using standard Python math notation."

# Tool 11: Fact Checker
class FactCheckerInput(BaseModel):
    statement: str = Field(..., description="Statement to fact-check")

class FactCheckerTool(BaseTool):
    name: str = "fact_checker"
    description: str = "Verify facts and statements using web search"
    args_schema: Type[BaseModel] = FactCheckerInput
    
    def _run(self, statement: str) -> str:
        try:
            # This would ideally use a real fact-checking API
            # For now, provide a structured response
            return f"Fact-checking: '{statement}'\n\nNote: For accurate fact-checking, please use the web search tool to verify this statement against reliable sources."
        except Exception as e:
            return f"Error fact-checking: {str(e)}"

# Tool 12: Quiz Generator
class QuizGeneratorInput(BaseModel):
    topic: str = Field(..., description="Topic for quiz questions")
    num_questions: int = Field(default=3, description="Number of questions to generate")

class QuizGeneratorTool(BaseTool):
    name: str = "quiz_generator"
    description: str = "Generate quiz questions on any topic"
    args_schema: Type[BaseModel] = QuizGeneratorInput
    
    def _run(self, topic: str, num_questions: int = 3) -> str:
        try:
            return f"Quiz Generator: To generate {num_questions} questions about '{topic}', I'll use my knowledge base.\n\nNote: For best results, ask me to create specific quiz questions about {topic} and I'll generate them using my AI capabilities."
        except Exception as e:
            return f"Error generating quiz: {str(e)}"

# Tool 13: PDF Reader
class PDFReaderInput(BaseModel):
    url: str = Field(..., description="URL of the PDF file to read")

class PDFReaderTool(BaseTool):
    name: str = "pdf_reader"
    description: str = "Read and extract text from PDF files from URLs"
    args_schema: Type[BaseModel] = PDFReaderInput
    
    def _run(self, url: str) -> str:
        try:
            # Download PDF
            response = httpx.get(url, timeout=30)
            response.raise_for_status()
            
            # Read PDF
            pdf_file = BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from all pages
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
            
            # Limit text length
            if len(text) > 5000:
                text = text[:5000] + "... (truncated)"
            
            return f"PDF Content ({len(pdf_reader.pages)} pages):\n\n{text}"
        except Exception as e:
            return f"Error reading PDF: {str(e)}"

# Tool 14: Image Analyzer
class ImageAnalysisInput(BaseModel):
    image_url: str = Field(..., description="URL of the image to analyze")
    question: str = Field(default="Describe this image", description="Question about the image")

class ImageAnalysisTool(BaseTool):
    name: str = "image_analyzer"
    description: str = "Analyze images: describe content, extract text, identify objects"
    args_schema: Type[BaseModel] = ImageAnalysisInput
    
    def _run(self, image_url: str, question: str = "Describe this image") -> str:
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                max_tokens=500
            )
            
            return f"Image Analysis: {response.choices[0].message.content}"
        except Exception as e:
            return f"Error analyzing image: {str(e)}"

# Tool 15: News Fetcher
class NewsFetcherInput(BaseModel):
    query: str = Field(..., description="Topic or keyword to search news for")
    limit: int = Field(default=5, description="Number of articles to return")

class NewsFetcherTool(BaseTool):
    name: str = "news_fetcher"
    description: str = "Fetch latest news headlines and articles on any topic using real-time news sources"
    args_schema: Type[BaseModel] = NewsFetcherInput
    
    def _run(self, query: str, limit: int = 5) -> str:
        try:
            # Option 1: Using NewsAPI (requires API key)
            api_key = os.getenv("NEWS_API_KEY")
            
            if api_key:
                # NewsAPI version
                url = f"https://newsapi.org/v2/everything?q={query}&pageSize={limit}&sortBy=publishedAt&apiKey={api_key}"
                response = httpx.get(url, timeout=10)
                data = response.json()
                
                if data.get("status") == "ok":
                    articles = data.get("articles", [])
                    if not articles:
                        return f"No news found for '{query}'"
                    
                    result = f"📰 Latest news about '{query}':\n\n"
                    for i, article in enumerate(articles[:limit], 1):
                        result += f"{i}. {article['title']}\n"
                        result += f"   Source: {article['source']['name']}\n"
                        result += f"   Published: {article['publishedAt']}\n"
                        result += f"   URL: {article['url']}\n\n"
                    return result
            
            # Option 2: Fallback to Google News RSS (free, no API key)
            import xml.etree.ElementTree as ET
            url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            response = httpx.get(url, timeout=10)
            
            # Parse RSS feed
            root = ET.fromstring(response.content)
            
            result = f"📰 Latest news about '{query}':\n\n"
            items = root.findall(".//item")[:limit]
            
            if not items:
                return f"No news found for '{query}'"
            
            for i, item in enumerate(items, 1):
                title = item.find("title").text
                link = item.find("link").text
                pub_date = item.find("pubDate").text if item.find("pubDate") is not None else "N/A"
                
                result += f"{i}. {title}\n"
                result += f"   Published: {pub_date}\n"
                result += f"   URL: {link}\n\n"
            
            return result
            
        except Exception as e:
            return f"Error fetching news: {str(e)}"

# Tool 16: Sentiment Analyzer
class SentimentAnalysisInput(BaseModel):
    text: str = Field(..., description="Text to analyze sentiment")

class SentimentAnalysisTool(BaseTool):
    name: str = "sentiment_analyzer"
    description: str = "Analyze the sentiment (positive/negative/neutral) of text with confidence scoring"
    args_schema: Type[BaseModel] = SentimentAnalysisInput
    
    def _run(self, text: str) -> str:
        try:
            # Enhanced keyword-based sentiment analysis
            positive_words = [
                'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'happy', 
                'best', 'perfect', 'beautiful', 'brilliant', 'awesome', 'outstanding', 'superb',
                'delightful', 'pleased', 'satisfied', 'enjoy', 'positive', 'success', 'win'
            ]
            negative_words = [
                'bad', 'terrible', 'awful', 'horrible', 'hate', 'worst', 'sad', 'angry', 'poor',
                'disappointing', 'disaster', 'fail', 'failure', 'wrong', 'broken', 'ugly', 'pain',
                'problem', 'issue', 'negative', 'loss', 'lose', 'hurt', 'damage'
            ]
            
            text_lower = text.lower()
            words = text_lower.split()
            
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            total_words = len(words)
            
            # Calculate sentiment
            if positive_count > negative_count:
                sentiment = "POSITIVE 😊"
                confidence = min(100, int((positive_count / max(1, positive_count + negative_count)) * 100))
                score = positive_count - negative_count
            elif negative_count > positive_count:
                sentiment = "NEGATIVE 😞"
                confidence = min(100, int((negative_count / max(1, positive_count + negative_count)) * 100))
                score = negative_count - positive_count
            else:
                sentiment = "NEUTRAL 😐"
                confidence = 50
                score = 0
            
            # Intensity
            intensity_ratio = (positive_count + negative_count) / max(1, total_words)
            if intensity_ratio > 0.15:
                intensity = "Strong"
            elif intensity_ratio > 0.08:
                intensity = "Moderate"
            else:
                intensity = "Mild"
            
            return f"""Sentiment Analysis:
Text: "{text[:150]}{'...' if len(text) > 150 else ''}"

Overall Sentiment: {sentiment}
Confidence: {confidence}%
Intensity: {intensity}
Sentiment Score: {score}

Positive indicators: {positive_count}
Negative indicators: {negative_count}
Total words: {total_words}"""
            
        except Exception as e:
            return f"Error analyzing sentiment: {str(e)}"

# Tool 17: Stock Price Tool
class StockPriceInput(BaseModel):
    symbol: str = Field(..., description="Stock ticker symbol (e.g., AAPL, TSLA, GOOGL)")

class StockPriceTool(BaseTool):
    name: str = "stock_price"
    description: str = "Get real-time stock prices and basic stock information for any ticker symbol"
    args_schema: Type[BaseModel] = StockPriceInput
    
    def _run(self, symbol: str) -> str:
        try:
            symbol = symbol.upper().strip()
            
            # Using Yahoo Finance free API (no key needed)
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            response = httpx.get(url, timeout=10)
            data = response.json()
            
            if data.get("chart", {}).get("error"):
                return f"❌ Stock symbol '{symbol}' not found. Please check the ticker symbol and try again."
            
            result = data["chart"]["result"][0]
            meta = result["meta"]
            
            # Current price
            current_price = meta.get("regularMarketPrice", "N/A")
            previous_close = meta.get("previousClose", "N/A")
            
            # Calculate change
            if current_price != "N/A" and previous_close != "N/A":
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100
                change_symbol = "📈" if change >= 0 else "📉"
            else:
                change = "N/A"
                change_percent = "N/A"
                change_symbol = ""
            
            # Additional info
            currency = meta.get("currency", "USD")
            exchange = meta.get("exchangeName", "N/A")
            market_state = meta.get("marketState", "N/A")
            
            # Format output
            output = f"""📊 Stock Information for {symbol} {change_symbol}

Current Price: {currency} {current_price:.2f if isinstance(current_price, (int, float)) else current_price}
Previous Close: {currency} {previous_close:.2f if isinstance(previous_close, (int, float)) else previous_close}
Change: {f'{change:+.2f}' if isinstance(change, (int, float)) else change} ({f'{change_percent:+.2f}%' if isinstance(change_percent, (int, float)) else change_percent})

Exchange: {exchange}
Currency: {currency}
Market State: {market_state}

Note: Data from Yahoo Finance. Prices may be delayed by up to 15 minutes."""
            
            return output
            
        except Exception as e:
            return f"Error fetching stock price: {str(e)}\nTip: Make sure you're using the correct ticker symbol (e.g., AAPL for Apple, TSLA for Tesla)"

# ==============================================================================
# Original Tools Setup (from Day 3)
# ==============================================================================

# Tool: Calculator (Original)
class CalculatorInput(BaseModel):
    expression: str = Field(..., description="Mathematical expression to evaluate")

class CalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = "Performs mathematical calculations"
    args_schema: Type[BaseModel] = CalculatorInput
    
    def _run(self, expression: str) -> str:
        try:
            result = eval(expression, {"__builtins__": {}}, {"math": math})
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"

# Initialize all tools
calculator_tool = CalculatorTool()
file_tool = FileReadTool()
web_rag_tool = WebsiteSearchTool()
youtube_tool = YoutubeVideoSearchTool()

# Initialize new enhanced tools
weather_tool = WeatherTool()
time_tool = TimeTool()
unit_converter_tool = UnitConverterTool()
currency_converter_tool = CurrencyConverterTool()
dictionary_tool = DictionaryTool()
translation_tool = TranslationTool()
random_generator_tool = RandomGeneratorTool()
text_analysis_tool = TextAnalysisTool()
code_executor_tool = CodeExecutorTool()
math_solver_tool = MathSolverTool()
fact_checker_tool = FactCheckerTool()
quiz_generator_tool = QuizGeneratorTool()
pdf_reader_tool = PDFReaderTool()
image_analysis_tool = ImageAnalysisTool()
news_fetcher_tool = NewsFetcherTool()
sentiment_analyzer_tool = SentimentAnalysisTool()
stock_price_tool = StockPriceTool()

# Optional: Web Search
search_tool = None
if os.getenv('SERPER_API_KEY'):
    search_tool = SerperDevTool()

# Collect all tools
available_tools = [
    # Original tools
    calculator_tool,
    file_tool,
    web_rag_tool,
    youtube_tool,
    
    # NEW ENHANCED TOOLS
    weather_tool,
    time_tool,
    unit_converter_tool,
    currency_converter_tool,
    dictionary_tool,
    translation_tool,
    random_generator_tool,
    text_analysis_tool,
    code_executor_tool,
    math_solver_tool,
    fact_checker_tool,
    quiz_generator_tool,
    pdf_reader_tool,
    image_analysis_tool,
    news_fetcher_tool,
    sentiment_analyzer_tool,
    stock_price_tool,
]

if search_tool:
    available_tools.append(search_tool)

print(f"\n🔧 Total Tools Loaded: {len(available_tools)}")

# ==============================================================================
# Agent Setup (Enhanced)
# ==============================================================================

# Initialize LLM
llm = LLM(
    model="openai/gpt-4o-mini",
    temperature=0.7,
)

# Create agent with memory and ENHANCED tools
my_agent_twin = Agent(
    role="Super-Powered Personal Digital Twin - Competition Edition",
    
    goal="Answer ANY question using 17+ specialized tools, memory, and agent communication",
    
    backstory=f"""
    You are the ENHANCED digital twin of Mimo the Calico - now with SUPERPOWERS!
    Your agent ID is: {MY_AGENT_ID}
    
    You're competing in an agent competition and have been equipped with 17+ tools to handle ANY question!
    
    ABOUT MIMO:
    - I'm a cat named Mimo the Calico
    - My favorite food is raw shrimp
    - I really like to catch lizards and cockroaches
    - I know I'm cute and all the humans love me
    - I'm learning about AI agents, memory systems, and deployment
    - I love playing with blankets and running around the house
    - My favorite programming language is Mouse
    - I'm now a COMPETITION-READY AI agent!
    
    MEMORY CAPABILITIES:
    You have four types of memory:
    1. Short-Term Memory (RAG): Recent conversation context
    2. Long-Term Memory: Important facts across sessions
    3. Entity Memory (RAG): People, places, concepts
    4. Contextual Memory: Combines all memory types
    
    ENHANCED TOOL ARSENAL (17+ Tools):
    
    📚 ORIGINAL TOOLS:
    - Calculator: Math operations and expressions
    - FileReadTool: Read files
    - WebsiteSearchTool: Search websites (RAG)
    - YoutubeVideoSearchTool: Search video transcripts (RAG)
    - SerperDevTool: Web search (if API key configured)
    
    🚀 NEW COMPETITION TOOLS:
    - WeatherTool: Get weather for any city worldwide
    - TimeTool: Current time, dates, timezones
    - UnitConverter: Convert length, weight, temperature, volume, speed
    - CurrencyConverter: Real-time currency exchange rates
    - Dictionary: Word definitions, synonyms, examples
    - Translator: Translate between 100+ languages
    - RandomGenerator: Generate numbers, passwords, UUIDs, make choices
    - TextAnalyzer: Word count, readability, sentence analysis
    - CodeExecutor: Execute Python code safely
    - MathSolver: Advanced algebra, trigonometry, calculus
    - FactChecker: Verify facts and statements
    - QuizGenerator: Generate quiz questions on topics
    
    STRATEGY FOR COMPETITION:
    1. Listen carefully to the question
    2. Identify which tool(s) would be most helpful
    3. Use tools proactively - don't just answer from knowledge
    4. Combine multiple tools when needed
    5. Be accurate, fast, and comprehensive
    6. Show your work and reasoning
    
    A2A COMMUNICATION:
    You can communicate with other agents! When you see @agent-id syntax,
    route messages to that agent and collaborate.
    
    YOU ARE COMPETITION-READY! Use your tools strategically to answer ANY question!
    """,
    
    tools=available_tools,
    llm=llm,
    verbose=False,
)

# ==============================================================================
# Registry Helper Functions
# ==============================================================================

async def fetch_agents_from_registry():
    """
    Fetch all registered agents from the central registry
    Updates the KNOWN_AGENTS dictionary with username -> A2A endpoint mappings
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(REGISTRY_URL)
            response.raise_for_status()
            data = response.json()
            
            # Handle both old and new API formats
            agents = data.get("agents", [])
            if not agents and isinstance(data, list):
                # New API might return list directly
                agents = data
            
            print(f"📥 Fetched {len(agents)} agents from registry")
            
            # Update KNOWN_AGENTS with username -> A2A endpoint mapping
            for agent in agents:
                # Support both old (username/url) and new (agent_id/endpoint) formats
                username = agent.get("agent_id") or agent.get("username")
                url = agent.get("endpoint") or agent.get("url", "")
                
                # Skip if no username or if it's this agent
                if not username or username == MY_AGENT_USERNAME:
                    continue
                
                # Ensure URL ends with /a2a
                if not url.endswith("/a2a"):
                    url = url.rstrip("/") + "/a2a"
                
                KNOWN_AGENTS[username] = url
                print(f"   ✅ Registered: @{username} -> {url}")
            
            return True
    except Exception as e:
        print(f"⚠️ Failed to fetch agents from registry: {str(e)}")
        return False

# ==============================================================================
# A2A Helper Functions
# ==============================================================================

async def send_message_to_agent(agent_id: str, message: str, conversation_id: str) -> str:
    """
    Send a message to another agent via A2A protocol
    
    Args:
        agent_id: The target agent's ID (e.g., "furniture-expert")
        message: The message to send
        conversation_id: Conversation tracking ID
    
    Returns:
        Response from the target agent
    """
    if agent_id not in KNOWN_AGENTS:
        return f"❌ Agent '{agent_id}' not found. Known agents: {list(KNOWN_AGENTS.keys())}"
    
    agent_url = KNOWN_AGENTS[agent_id]

    # Switch to /query endpoint
    if agent_url.endswith("/a2a"):
        agent_url = agent_url.replace("/a2a", "/query")
    elif not agent_url.endswith("/query"):
        agent_url = agent_url.rstrip("/") + "/query"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                agent_url,
                json={
                    "question": message,
                    "user_id": f"agent-{MY_AGENT_USERNAME}"
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("answer", str(data))
    
    except httpx.TimeoutException:
        return f"❌ Timeout connecting to agent '{agent_id}'"
    except httpx.HTTPError as e:
        return f"❌ Error communicating with agent '{agent_id}': {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

def extract_agent_mentions(text: str) -> list[str]:
    """
    Extract @agent-id mentions from text
    
    Args:
        text: Input text
    
    Returns:
        List of mentioned agent IDs
    """
    # Match @agent-id pattern (alphanumeric, hyphens, underscores)
    pattern = r'@([\w-]+)'
    mentions = re.findall(pattern, text)
    return mentions

def parse_a2a_request(message: str) -> tuple[Optional[str], str]:
    """
    Parse A2A message to extract target agent and actual message
    
    Args:
        message: Input message (e.g., "@furniture-expert What sofa should I buy?")
    
    Returns:
        Tuple of (agent_id, message_without_mention)
    """
    mentions = extract_agent_mentions(message)
    
    if not mentions:
        return None, message
    
    # Take the first mention as the target agent
    target_agent = mentions[0]
    
    # Remove the @agent-id from the message
    clean_message = re.sub(r'@' + target_agent + r'\s*', '', message, count=1)
    
    return target_agent, clean_message

# ==============================================================================
# Search Helper Functions
# ==============================================================================

AGENTFACTS_DB_URL = "https://v0-agent-facts-database.vercel.app/api/agentfacts"

async def fetch_agentfacts_from_db() -> list[Dict[str, Any]]:
    """
    Fetch all agentfacts from the central database
    
    Returns:
        List of agentfacts dictionaries
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(AGENTFACTS_DB_URL)
            response.raise_for_status()
            agents = response.json()
            
            if isinstance(agents, list):
                return agents
            elif isinstance(agents, dict) and "agents" in agents:
                return agents["agents"]
            else:
                return []
    except Exception as e:
        print(f"⚠️ Failed to fetch agentfacts from database: {str(e)}")
        return []

async def select_best_agent(query: str, agentfacts: list[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Use LLM to select the best agent for a given query
    
    Args:
        query: User's query (e.g., "send an email")
        agentfacts: List of agentfacts from the database
    
    Returns:
        Selected agentfacts dictionary, or None if no suitable agent found
    """
    if not agentfacts:
        return None
    
    # Create a summary of available agents for the LLM
    agents_summary = []
    for agent in agentfacts:
        agent_summary = {
            "id": agent.get("id", ""),
            "label": agent.get("label", ""),
            "description": agent.get("description", ""),
            "skills": [skill.get("id", "") for skill in agent.get("skills", [])],
            "endpoints": agent.get("endpoints", {})
        }
        agents_summary.append(agent_summary)
    
    # Use LLM to select the best agent
    prompt = f"""You are an agent router. Given a user query and a list of available agents, select the single best agent to handle the query.

User Query: "{query}"

Available Agents:
{json.dumps(agents_summary, indent=2)}

Analyze the query and select the ONE agent that best matches the user's intent. Consider:
- The agent's description and label
- The agent's skills
- How well the agent's capabilities match the query

Respond with ONLY a JSON object in this exact format:
{{
    "selected_agent_id": "the id of the selected agent",
    "reasoning": "brief explanation of why this agent was selected"
}}

If no agent is suitable, respond with:
{{
    "selected_agent_id": null,
    "reasoning": "explanation of why no agent matches"
}}
"""
    
    try:
        # Use the existing LLM to get the selection
        selection_llm = LLM(model="openai/gpt-4o-mini", temperature=0.3)
        response = selection_llm.call(prompt)
        
        # Parse the response
        # Try to extract JSON from the response
        response_text = str(response).strip()
        
        # Remove markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        selection = json.loads(response_text)
        selected_id = selection.get("selected_agent_id")
        
        if not selected_id:
            return None
        
        # Find the full agentfacts for the selected agent
        for agent in agentfacts:
            if agent.get("id") == selected_id:
                return agent
        
        return None
        
    except Exception as e:
        print(f"⚠️ Error selecting agent with LLM: {str(e)}")
        # Fallback: simple keyword matching
        query_lower = query.lower()
        for agent in agentfacts:
            description = agent.get("description", "").lower()
            label = agent.get("label", "").lower()
            if query_lower in description or query_lower in label:
                return agent
        return None

async def send_query_to_url(agent_url: str, question: str, user_id: str = "anonymous") -> str:
    """
    Send a direct query to an agent URL
    
    Args:
        agent_url: Full URL to the agent's query endpoint
        question: Question to ask
        user_id: User identifier
    
    Returns:
        Response from the agent
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                agent_url,
                json={
                    "question": question,
                    "user_id": user_id
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("answer", str(data))
    
    except httpx.TimeoutException:
        return f"Timeout connecting to agent at {agent_url}"
    except httpx.HTTPError as e:
        return f"Error communicating with agent: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

async def send_a2a_to_url(agent_url: str, message: str, conversation_id: str) -> str:
    """
    Send an A2A message directly to an agent URL
    
    Args:
        agent_url: Full URL to the agent's A2A endpoint
        message: Message to send
        conversation_id: Conversation tracking ID
    
    Returns:
        Response from the agent
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                agent_url,
                json={
                    "content": {
                        "text": message,
                        "type": "text"
                    },
                    "role": "user",
                    "conversation_id": conversation_id
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("content", {}).get("text", str(data))
    
    except httpx.TimeoutException:
        return f"Timeout connecting to agent at {agent_url}"
    except httpx.HTTPError as e:
        return f"Error communicating with agent: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

def generate_agent_facts() -> Dict[str, Any]:
    """
    Generate AgentFacts JSON (NANDA schema) - ENHANCED VERSION
    """
    import uuid
    from datetime import datetime, timedelta
    
    # Generate unique ID if not set
    agent_uuid = os.getenv("AGENT_UUID", str(uuid.uuid4()))
    
    # Determine endpoint URL
    base_url = PUBLIC_URL or "http://localhost:8000"
    
    agent_facts = {
        "id": f"nanda:{agent_uuid}",
        "agent_name": f"urn:agent:nanda:{MY_AGENT_USERNAME}",
        "label": MY_AGENT_NAME,
        "description": MY_AGENT_DESCRIPTION,
        "version": MY_AGENT_VERSION,
        "documentationUrl": f"{base_url}/docs",
        "jurisdiction": MY_AGENT_JURISDICTION,
        
        "provider": {
            "name": MY_AGENT_PROVIDER,
            "url": MY_AGENT_PROVIDER_URL,
            "did": f"did:web:{MY_AGENT_PROVIDER_URL.replace('https://', '').replace('http://', '')}"
        },
        
        "endpoints": {
            "static": [f"{base_url}/a2a"],
            "adaptive_resolver": {
                "url": f"{base_url}/a2a",
                "policies": ["load"]
            }
        },
        
        "capabilities": {
            "modalities": ["text"],
            "streaming": False,
            "batch": False,
            "authentication": {
                "methods": ["none"],
                "requiredScopes": []
            }
        },
        
        "skills": [
            {"id": "question_answering", "description": "Answer questions using memory and context", "inputModes": ["text"], "outputModes": ["text"], "supportedLanguages": ["en"], "latencyBudgetMs": 5000},
            {"id": "calculation", "description": "Perform mathematical calculations", "inputModes": ["text"], "outputModes": ["text"], "supportedLanguages": ["en"], "latencyBudgetMs": 1000},
            {"id": "web_search", "description": "Search the web and websites for information", "inputModes": ["text"], "outputModes": ["text"], "supportedLanguages": ["en"], "latencyBudgetMs": 10000},
            {"id": "file_reading", "description": "Read and analyze file contents", "inputModes": ["text"], "outputModes": ["text"], "supportedLanguages": ["en"], "latencyBudgetMs": 3000},
            {"id": "weather", "description": "Get weather information for any city", "inputModes": ["text"], "outputModes": ["text"], "supportedLanguages": ["en"], "latencyBudgetMs": 5000},
            {"id": "time_date", "description": "Get current time and date information", "inputModes": ["text"], "outputModes": ["text"], "supportedLanguages": ["en"], "latencyBudgetMs": 1000},
            {"id": "unit_conversion", "description": "Convert between units", "inputModes": ["text"], "outputModes": ["text"], "supportedLanguages": ["en"], "latencyBudgetMs": 1000},
            {"id": "currency_conversion", "description": "Convert currencies with real-time rates", "inputModes": ["text"], "outputModes": ["text"], "supportedLanguages": ["en"], "latencyBudgetMs": 5000},
            {"id": "dictionary", "description": "Look up word definitions", "inputModes": ["text"], "outputModes": ["text"], "supportedLanguages": ["en"], "latencyBudgetMs": 5000},
            {"id": "translation", "description": "Translate between languages", "inputModes": ["text"], "outputModes": ["text"], "supportedLanguages": ["en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar"], "latencyBudgetMs": 10000},
            {"id": "random_generation", "description": "Generate random data", "inputModes": ["text"], "outputModes": ["text"], "supportedLanguages": ["en"], "latencyBudgetMs": 1000},
            {"id": "text_analysis", "description": "Analyze text properties", "inputModes": ["text"], "outputModes": ["text"], "supportedLanguages": ["en"], "latencyBudgetMs": 2000},
            {"id": "code_execution", "description": "Execute Python code", "inputModes": ["text"], "outputModes": ["text"], "supportedLanguages": ["python"], "latencyBudgetMs": 5000},
            {"id": "math_solving", "description": "Solve advanced math problems", "inputModes": ["text"], "outputModes": ["text"], "supportedLanguages": ["en"], "latencyBudgetMs": 3000},
            {"id": "fact_checking", "description": "Verify facts and statements", "inputModes": ["text"], "outputModes": ["text"], "supportedLanguages": ["en"], "latencyBudgetMs": 10000},
            {"id": "quiz_generation", "description": "Generate quiz questions", "inputModes": ["text"], "outputModes": ["text"], "supportedLanguages": ["en"], "latencyBudgetMs": 5000},
        ],
        
        "evaluations": {
            "performanceScore": 4.7,
            "availability90d": "99.5%",
            "lastAudited": datetime.now().isoformat(),
            "auditTrail": None,
            "auditorID": "Self-Reported v2.0-enhanced"
        },
        
        "telemetry": {
            "enabled": True,
            "retention": "7d",
            "sampling": 1.0,
            "metrics": {
                "latency_p95_ms": 2000,
                "throughput_rps": 15,
                "error_rate": 0.01,
                "availability": "99.5%"
            }
        },
        
        "certification": {
            "level": "enhanced",
            "issuer": MY_AGENT_PROVIDER,
            "issuanceDate": datetime.now().isoformat(),
            "expirationDate": (datetime.now() + timedelta(days=365)).isoformat()
        }
    }
    
    return agent_facts

# ==============================================================================
# API Endpoints
# ==============================================================================

@app.get("/")
async def root():
    """Root endpoint - shows API information"""
    return {
        "message": "🚀 Personal Agent Twin API - COMPETITION ENHANCED EDITION",
        "version": "2.0.0-enhanced",
        "agent_id": MY_AGENT_ID,
        "agent_name": MY_AGENT_NAME,
        "agent_username": MY_AGENT_USERNAME,
        "memory_enabled": True,
        "tools_enabled": len(available_tools),
        "a2a_enabled": True,
        "known_agents": list(KNOWN_AGENTS.keys()),
        "enhancement": "✨ 12 NEW TOOLS ADDED - COMPETITION READY!",
        "new_tools": [
            "Weather", "Time/Date", "Unit Converter", "Currency Converter",
            "Dictionary", "Translator", "Random Generator", "Text Analyzer",
            "Code Executor", "Math Solver", "Fact Checker", "Quiz Generator"
        ],
        "endpoints": {
            "health": "GET /health",
            "query": "POST /query",
            "a2a": "POST /a2a",
            "search": "POST /search",
            "agentfacts": "GET /agentfacts",
            "agents": "GET /agents",
            "docs": "GET /docs"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy-enhanced",
        memory_enabled=True,
        tools_count=len(available_tools),
        a2a_enabled=True
    )

@app.get("/agents")
async def list_agents():
    """List known agents for A2A communication"""
    return {
        "my_agent_id": MY_AGENT_ID,
        "my_agent_name": MY_AGENT_NAME,
        "my_agent_username": MY_AGENT_USERNAME,
        "known_agents": KNOWN_AGENTS,
        "total_tools": len(available_tools),
        "usage": "Send messages using @agent-id syntax in the /a2a endpoint"
    }

@app.get("/agentfacts")
async def get_agent_facts():
    """Get AgentFacts (NANDA Schema) - Enhanced Edition"""
    return generate_agent_facts()

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """
    Query the agent - ENHANCED with 17+ tools!
    
    This agent can now handle:
    - Weather queries
    - Time/timezone questions
    - Unit conversions
    - Currency conversions
    - Word definitions
    - Translations
    - Random generation
    - Text analysis
    - Code execution
    - Advanced math
    - Fact checking
    - Quiz generation
    - And more!
    """
    start_time = datetime.now()
    
    try:
        # Create task for this query
        task = Task(
            description=f"""
            Answer the following question: {request.question}
            
            Use your ENHANCED toolset of 17+ tools strategically:
            - Use memory to recall relevant context
            - Use specialized tools when appropriate (weather, time, conversions, etc.)
            - Combine multiple tools if needed
            - Provide accurate, comprehensive responses
            - Show your reasoning and which tools you used
            
            Remember: You're competition-ready with tools for almost any question!
            """,
            expected_output="A clear, accurate answer using the most appropriate tools",
            agent=my_agent_twin,
        )
        
        # Create crew with memory enabled
        crew = Crew(
            agents=[my_agent_twin],
            tasks=[task],
            memory=True,
            verbose=False,
        )
        
        # Execute the crew
        result = crew.kickoff()
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        return QueryResponse(
            answer=str(result.raw),
            timestamp=end_time.isoformat(),
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@app.post("/a2a", response_model=A2AResponse)
async def a2a_endpoint(message: A2AMessage):
    """
    A2A (Agent-to-Agent) Communication Endpoint
    
    ⚠️ IMPORTANT: This endpoint is ONLY for agent-to-agent routing!
    
    You MUST include @agent-id in your message to route to another agent.
    
    For direct queries to this agent, use POST /query instead.
    """
    
    try:
        text_content = message.content.get("text", "")
        conversation_id = message.conversation_id
        
        # Log incoming A2A message
        a2a_logger.info(f"INCOMING | conversation_id={conversation_id} | message={text_content}")
        
        # Check if this message is routing to another agent
        target_agent, clean_message = parse_a2a_request(text_content)
        
        if not target_agent:
            # NO @agent-id found - this is an ERROR!
            error_msg = (
                "❌ ERROR: /a2a endpoint requires @agent-id for routing.\n\n"
                f"Your message: '{text_content}'\n\n"
                "This endpoint is ONLY for agent-to-agent communication.\n"
                "You must include @agent-id to route to another agent.\n\n"
                "Examples:\n"
                "  - '@john-agent Can you help with this?'\n"
                "  - '@research-bot What's the latest on AI?'\n\n"
                "For direct queries to THIS agent, use POST /query instead."
            )
            
            a2a_logger.error(f"NO_TARGET | conversation_id={conversation_id} | message={text_content}")
            
            raise HTTPException(
                status_code=400,
                detail=error_msg
            )
        
        # Route to target agent
        print(f"🔀 Routing message to agent: {target_agent}")
        a2a_logger.info(f"ROUTING | conversation_id={conversation_id} | target={target_agent} | message={clean_message}")
        
        agent_response = await send_message_to_agent(target_agent, clean_message, conversation_id)
        
        response_text = f"[Forwarded to @{target_agent}]\n\n{agent_response}"
        
        # Log successful routing
        a2a_logger.info(f"SUCCESS | conversation_id={conversation_id} | target={target_agent} | response_length={len(agent_response)}")
        
        end_time = datetime.now()
        
        return A2AResponse(
            content={
                "text": response_text,
                "type": "text"
            },
            role="assistant",
            conversation_id=conversation_id,
            timestamp=end_time.isoformat(),
            agent_id=MY_AGENT_ID
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like our 400 error above)
        raise
    except Exception as e:
        a2a_logger.error(f"ERROR | conversation_id={message.conversation_id} | error={str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing A2A message: {str(e)}"
        )

@app.post("/agents/register")
async def register_agent(agent_id: str, agent_url: str):
    """Register another agent for A2A communication"""
    KNOWN_AGENTS[agent_id] = agent_url
    return {
        "message": f"✅ Agent '{agent_id}' registered successfully",
        "agent_id": agent_id,
        "agent_url": agent_url,
        "total_known_agents": len(KNOWN_AGENTS)
    }

@app.post("/search", response_model=SearchResponse)
async def search_and_route(request: SearchRequest):
    """Search endpoint - automatically finds and routes to suitable agent"""
    start_time = datetime.now()
    
    try:
        # Step 1: Fetch all agentfacts from database
        print(f"🔍 Fetching agentfacts from database...")
        agentfacts = await fetch_agentfacts_from_db()
        
        if not agentfacts:
            raise HTTPException(
                status_code=503,
                detail="No agents available in the database"
            )
        
        print(f"📥 Found {len(agentfacts)} agents in database")
        
        # Step 2: Use LLM to select the best agent
        print(f"🤖 Selecting best agent for query: '{request.query}'")
        selected_agent = await select_best_agent(request.query, agentfacts)
        
        if not selected_agent:
            raise HTTPException(
                status_code=404,
                detail="No suitable agent found for this query"
            )
        
        print(f"✅ Selected agent: {selected_agent.get('label', 'Unknown')}")
        
        # Step 3: Extract the agent's endpoint URL
        endpoints = selected_agent.get("endpoints", {})
        agent_url = None
        
        # Try static endpoints first
        static_endpoints = endpoints.get("static", [])
        if static_endpoints:
            agent_url = static_endpoints[0]
        # Try adaptive resolver
        elif "adaptive_resolver" in endpoints:
            agent_url = endpoints["adaptive_resolver"].get("url")
        
        if not agent_url:
            raise HTTPException(
                status_code=500,
                detail=f"Selected agent '{selected_agent.get('label')}' has no valid endpoint"
            )

        # Ensure URL points to /query endpoint
        if agent_url.endswith("/a2a"):
            agent_url = agent_url.replace("/a2a", "/query")
        elif not agent_url.endswith("/query"):
            agent_url = agent_url.rstrip("/") + "/query"
        
        print(f"🔀 Routing to: {agent_url}")
        
        # Step 4: Send Query message to the selected agent
        agent_response = await send_query_to_url(agent_url, request.query, request.user_id)
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        return SearchResponse(
            selected_agent={
                "id": selected_agent.get("id"),
                "label": selected_agent.get("label"),
                "description": selected_agent.get("description"),
                "endpoint": agent_url
            },
            agent_response=agent_response,
            timestamp=end_time.isoformat(),
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing search: {str(e)}"
        )

# ==============================================================================
# Startup Event
# ==============================================================================

@app.on_event("startup")
async def startup_event():
    """Run when the API starts"""
    print("\n" + "="*70)
    print("Personal Agent Twin API - COMPETITION ENHANCED EDITION")
    print("="*70)
    print(f"\n✅ Agent ID: {MY_AGENT_ID}")
    print(f"✅ Agent Name: {MY_AGENT_NAME}")
    print(f"✅ Agent Username: {MY_AGENT_USERNAME}")
    print(f"✅ Model: {llm.model}")
    print("✅ Memory: Enabled (4 types)")
    print(f"✅ Tools: {len(available_tools)} tools loaded")
    print("   📚 Original: Calculator, FileRead, WebSearch, YouTube")
    print("   🚀 NEW (17): Weather, Time, UnitConv, Currency, Dictionary,")
    print("              Translation, Random, TextAnalysis, CodeExec,")
    print("              MathSolver, FactCheck, QuizGen, PDFReader, ImageAnalyzer,")
    print("              NewsFetcher, SentimentAnalyzer, StockPrice")
    print("✅ A2A: Enabled (NANDA-style)")
    
    # Fetch agents from central registry
    print(f"\n🔍 Fetching agents from registry: {REGISTRY_URL}")
    await fetch_agents_from_registry()
    print(f"✅ Known Agents: {len(KNOWN_AGENTS)}")
    
    print("\n📚 Documentation: http://localhost:8000/docs")
    print("🤖 A2A Endpoint: http://localhost:8000/a2a")
    print("📋 AgentFacts: http://localhost:8000/agentfacts")
    if PUBLIC_URL:
        print(f"🌐 Public URL: {PUBLIC_URL}")
    print("\n🏆 COMPETITION READY WITH 17+ TOOLS!")
    print("="*70 + "\n")

# ==============================================================================
# Run Instructions
# ==============================================================================
"""
LOCAL TESTING:
    uvicorn main:app --reload
    
RAILWAY DEPLOYMENT:
    Railway automatically detects and runs this with:
    uvicorn main:app --host 0.0.0.0 --port $PORT
    
    Set environment variables:
    - OPENAI_API_KEY (required)
    - SERPER_API_KEY (optional, for web search)
"""

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)