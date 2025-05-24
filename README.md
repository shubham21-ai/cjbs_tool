# Satellite Information System 🛰️

A comprehensive satellite information gathering system that uses AI agents to collect and analyze detailed information about satellites. The system provides information across three main categories: Basic Information, Technical Specifications, and Launch & Cost Information.

## Features

### 1. Basic Information Bot
Gathers fundamental satellite data including:
- Orbital altitude and source
- Orbital lifetime and source
- Launch orbit classification and source
- Number of payloads and source

### 2. Technical Specifications Bot
Collects detailed technical information including:
- Satellite type and source
- Satellite application and source
- Sensor specifications and source
- Technological breakthroughs and source

### 3. Launch & Cost Bot
Provides comprehensive launch and cost data including:
- Launch cost and source
- Launch vehicle details and source
- Launch date and site information
- Mission cost breakdown and source
- Vehicle reusability information

## Prerequisites

- Python 3.8 or higher
- Google API Key (for Gemini 1.5 Flash)
- Tavily API Key (for web search)
- SerpAPI Key (optional)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd satellite-information-system
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your API keys:
```env
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
SERPAPI_API_KEY=your_serpapi_key
```

## Usage

### Running the Web Interface

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the provided local URL (typically http://localhost:8501)

### Using the Interface

1. **Satellite Selection**
   - Enter a satellite name in the sidebar
   - View previously searched satellites
   - Delete old satellite data if needed

2. **Information Categories**
   - Basic Information Tab: View fundamental satellite data
   - Technical Specifications Tab: Access detailed technical information
   - Launch & Cost Tab: Review launch and cost-related data
   - Raw JSON Tab: View all collected data in JSON format

3. **Data Management**
   - Download individual category data as JSON
   - Download complete satellite data
   - View last update timestamps

### Using the Bots Programmatically

```python
from basic import BasicInfoBot
from tech import TechAgent
from cost import CostBot

# Initialize bots
basic_bot = BasicInfoBot()
tech_bot = TechAgent()
cost_bot = CostBot()

# Process a satellite
satellite_name = "Starlink-1"

# Get basic information
basic_info = basic_bot.process_satellite(satellite_name)

# Get technical specifications
tech_specs = tech_bot.process_satellite(satellite_name)

# Get launch and cost information
launch_cost = cost_bot.process_satellite(satellite_name)
```

## Data Storage

The system uses a JSON-based storage system (`satellite_data.json`) to maintain:
- Historical satellite data
- Source URLs for verification
- Timestamps for data freshness

## Error Handling

The system includes robust error handling for:
- API rate limits
- Network issues
- Invalid satellite names
- Data parsing errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini API for AI capabilities
- Tavily Search for web search functionality
- Streamlit for the web interface
- LangChain for AI agent framework

## Support

For issues and feature requests, please create an issue in the repository.

## Roadmap

- [ ] Add support for batch processing
- [ ] Implement data validation
- [ ] Add more satellite data sources
- [ ] Enhance error recovery
- [ ] Add data visualization features 