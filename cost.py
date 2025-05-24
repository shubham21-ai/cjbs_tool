from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType, Tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import DuckDuckGoSearchRun
from data_manager import SatelliteDataManager
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
os.environ["SERPAPI_API_KEY"] = SERPAPI_API_KEY

class CostBot:
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
        ]

    def _initialize_schema(self):
        """Initialize the response schema"""
        self.response_schema = [
            ResponseSchema(name="launch_cost", description="Launch cost in USD"),
            ResponseSchema(name="launch_cost_source", description="Source URL for launch cost data"),
            ResponseSchema(name="launch_vehicle", description="Launch vehicle used"),
            ResponseSchema(name="launch_vehicle_source", description="Source URL for launch vehicle information"),
            ResponseSchema(name="launch_date", description="Launch date"),
            ResponseSchema(name="launch_date_source", description="Source URL for launch date information"),
            ResponseSchema(name="launch_site", description="Launch site"),
            ResponseSchema(name="launch_site_source", description="Source URL for launch site information"),
            ResponseSchema(name="launch_mass", description="JSON object containing max_leo and actual_mass"),
            ResponseSchema(name="launch_mass_source", description="Source URL for launch mass information"),
            ResponseSchema(name="launch_success", description="Launch success status (1 for success, 0 for failure)"),
            ResponseSchema(name="launch_success_source", description="Source URL for launch success information"),
            ResponseSchema(name="vehicle_reusability", description="Vehicle reusability status (1 for reusable, 0 for not)"),
            ResponseSchema(name="reusability_details", description="Details about vehicle reusability"),
            ResponseSchema(name="reusability_source", description="Source URL for reusability information"),
            ResponseSchema(name="mission_cost", description="JSON object containing all cost components"),
            ResponseSchema(name="mission_cost_source", description="Source URL for mission cost information")
        ]

    def _initialize_parser(self):
        """Initialize the output parser"""
        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schema)
        self.format_instructions = self.output_parser.get_format_instructions()

    def _initialize_prompt(self):
        """Initialize the prompt template"""
        template = """
You are a satellite launch cost expert who can search and analyze satellite launch information using available tools.
You need to find comprehensive launch cost and mission information about the given satellite.

Take the input below delimited by triple backticks and use it to search and analyze using the available tools.
Input: ```{input}```

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
            temperature=0.7
        )
        
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

    def process_satellite(self, satellite_name):
        """Process satellite information and return parsed output"""
        try:
            # Format the prompt with the satellite name
            formatted_messages = self.prompt.format_messages(
                input=satellite_name,
                format_instructions=self.format_instructions
            )
            
            # Run the agent using invoke instead of run
            response = self.agent.invoke({"input": formatted_messages})
            
            # Parse the response
            parsed_output = self.output_parser.parse(response["output"])
            
            # Add the satellite name to the output
            parsed_output["satellite_name"] = satellite_name
            
            return parsed_output
            
        except Exception as e:
            print(f"Error processing satellite {satellite_name}: {str(e)}")
            return None