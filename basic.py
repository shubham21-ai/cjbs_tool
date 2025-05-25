from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType, Tool
from langchain_community.tools.tavily_search import TavilySearchResults
from data_manager import SatelliteDataManager
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
import os
from dotenv import load_dotenv
import time
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
os.environ["SERPAPI_API_KEY"] = SERPAPI_API_KEY

class BasicInfoBot:
    def __init__(self):
        self.satellite_data_manager = SatelliteDataManager()
        self._initialize_tools()
        self._initialize_schema()
        self._initialize_parser()
        self._initialize_prompt()
        self._initialize_agent()

    def _initialize_tools(self):
        """Initialize the tools for the agent"""
        self.tools = [
            Tool(
                name="Satellite Data Manager",
                func=self.satellite_data_manager.get_satellite_data,
                description="Useful for getting satellite data based on the user's query.",
            ),
            Tool(
                name="Tavily Search",
                func=TavilySearchResults().run,
                description="Useful for getting information from the web.",
            ),
            Tool(
                name="DuckDuckGo Search",
                func=DuckDuckGoSearchRun().run,
                description="Useful for searching the web using DuckDuckGo search engine."
            )
        ]

    def _initialize_schema(self):
        """Initialize the response schema"""
        self.response_schema = [
            ResponseSchema(name="altitude", description="Orbital altitude in kilometers"),
            ResponseSchema(name="altitude_source", description="Source URL for altitude information"),
            ResponseSchema(name="orbital_life_years", description="Orbital lifetime in years"),
            ResponseSchema(name="orbital_life_source", description="Source URL for orbital lifetime information"),
            ResponseSchema(name="launch_orbit_classification", description="Orbit classification (LEO, MEO, GEO, etc.)"),
            ResponseSchema(name="orbit_classification_source", description="Source URL for orbit classification information"),
            ResponseSchema(name="number_of_payloads", description="Number of payloads on the satellite"),
            ResponseSchema(name="payloads_source", description="Source URL for payload information")
        ]

    def _initialize_parser(self):
        """Initialize the output parser"""
        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schema)
        self.format_instructions = self.output_parser.get_format_instructions()

    def _initialize_prompt(self):
        """Initialize the prompt template"""
        template = """
You are a satellite basic information expert who can search and analyze satellite information using available tools.
You need to find comprehensive basic information about the given satellite.

Take the input below delimited by triple backticks and use it to search and analyze using the available tools.
Input: ```{input}```

Available tools:
IMPORTANT: Do not attempt to use any tools that are not listed above. If a tool is not available(None), do not try to use it.
1. Tavily Search - For getting information from the web
2. DuckDuckGo Search - For searching the web using DuckDuckGo search engine
You can search websites, articles, news information, press releases, parliamentary reports, technical documentation, and scientific papers.

IMPORTANT: Do not attempt to use any tools that are not listed above. If a tool is not available, do not try to use it.

{format_instructions}

Make sure to:
1. Use the available tools (Tavily Search) to find accurate information
2. Include URLs for all source information
3. Format the output exactly as specified in the format instructions
4. Provide detailed and specific information
5. Use reliable sources for all information
"""
        self.prompt = ChatPromptTemplate.from_template(template)

    def _initialize_agent(self):
        """Initialize the agent"""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            api_key=GOOGLE_API_KEY,
            temperature=0.7,
            max_retries=3,
            timeout=120
        )
        
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        reraise=True
    )
    def _process_with_retry(self, satellite_name):
        """Process satellite information with retry logic"""
        formatted_messages = self.prompt.format_messages(
            input=satellite_name,
            format_instructions=self.format_instructions
        )
        
        response = self.agent.invoke({"input": formatted_messages})
        return self.output_parser.parse(response["output"])

    def process_satellite(self, satellite_name):
        """Process satellite information and return parsed output"""
        try:
            # Add a small delay before processing to avoid rate limits
            time.sleep(1)
            
            # Process with retry logic
            parsed_output = self._process_with_retry(satellite_name)
            
            # Add the satellite name to the output
            parsed_output["satellite_name"] = satellite_name
            
            return parsed_output
            
        except Exception as e:
            print(f"Error processing satellite {satellite_name}: {str(e)}")
            if "Resource has been exhausted" in str(e):
                print("API rate limit reached. Please try again in a few minutes.")
            return None
