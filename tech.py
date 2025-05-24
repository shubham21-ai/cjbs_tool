from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType, Tool
from langchain_community.tools.tavily_search import TavilySearchResults
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

class TechAgent:
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
            ResponseSchema(name="satellite_type", description="The type of satellite (Communication/ Earth Observation / Experimental / Navigation / Science & Exploration)"),
            ResponseSchema(name="satellite_type_source", description="URL of the source for satellite type information"),
            ResponseSchema(name="satellite_application", description="Detailed description of the satellite's application"),
            ResponseSchema(name="application_source", description="URL of the source for satellite application information"),
            ResponseSchema(name="sensor_specs", description="Object containing sensor specifications (spectral bands and spatial resolution)"),
            ResponseSchema(name="sensor_specs_source", description="URL of the source for sensor specifications"),
            ResponseSchema(name="technological_breakthroughs", description="Notable technological breakthroughs of the satellite"),
            ResponseSchema(name="breakthrough_source", description="URL of the source for technological breakthroughs")
        ]

    def _initialize_parser(self):
        """Initialize the output parser"""
        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schema)
        self.format_instructions = self.output_parser.get_format_instructions()

    def _initialize_prompt(self):
        """Initialize the prompt template"""
        template = """
You are a satellite technology expert who can search and analyze satellite technical information using available tools.
You need to find comprehensive technical specifications and details about the given satellite.

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
