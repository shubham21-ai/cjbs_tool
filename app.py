import streamlit as st
import json
from tech import TechAgent
from basic import BasicInfoBot
from cost import CostBot
from data_manager import SatelliteDataManager
import pandas as pd
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the data manager
data_manager = SatelliteDataManager()

# Set page config
st.set_page_config(
    page_title="SkyTrack: Satellite Info Explorer",
    page_icon="🛰️",
    layout="wide"
)

class CaptureStdout:
    def __init__(self, container):
        self.container = container
        self.placeholder = container.empty()
        self.output = []
        
    def write(self, text):
        if text:
            self.output.append(text)
            try:
                self.placeholder.code(''.join(self.output), language="text")
            except Exception as e:
                print(f"Error updating UI: {e}")
                try:
                    self.placeholder = self.container.empty()
                    self.placeholder.code(''.join(self.output), language="text")
                except:
                    pass
        
    def flush(self):
        try:
            if self.output:
                self.placeholder.code(''.join(self.output), language="text")
        except:
            pass

# Title and description
st.title("🛰️ Satellite Information System")
st.markdown("""
This application gathers comprehensive information about satellites using specialized AI agents.
Each agent focuses on different aspects of satellite information:
- Basic Information (altitude, orbital life, etc.)
- Technical Specifications (type, applications, sensors)
- Launch and Cost Information
""")

# Sidebar for satellite selection
st.sidebar.title("Satellite Selection")

# Use session state to manage the current satellite name
if 'satellite_name' not in st.session_state:
    st.session_state.satellite_name = ""

satellite_name_input = st.sidebar.text_input(
    "Enter Satellite Name", 
    value=st.session_state.satellite_name,
    key="satellite_name_input_key"
)

# Update session state when text input changes
if satellite_name_input != st.session_state.satellite_name:
    st.session_state.satellite_name = satellite_name_input
    st.rerun()

# Display existing satellites with delete option
existing_satellites = data_manager.get_all_satellites()
if existing_satellites:
    st.sidebar.markdown("### Previously Searched Satellites")
    for sat in existing_satellites:
        col1, col2 = st.sidebar.columns([4, 1])
        with col1:
            if st.button(sat, key=f"select_sat_{sat}"):
                st.session_state.satellite_name = sat
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"delete_sat_{sat}"):
                data_manager.delete_satellite_data(sat)
                if st.session_state.satellite_name == sat:
                    st.session_state.satellite_name = ""
                st.rerun()

# Add download button for the entire satellite_data.json file
file_path = "satellite_data.json"
if os.path.exists(file_path):
    with open(file_path, "r") as f:
        all_satellite_data = f.read()
    st.sidebar.download_button(
        label="Download All Satellite Data (JSON)",
        data=all_satellite_data,
        file_name="satellite_data.json",
        mime="application/json"
    )

# Main content area
if st.session_state.satellite_name:
    satellite_name = st.session_state.satellite_name
    st.header(f"Information for {satellite_name}")
    
    # Create tabs for different information categories
    tab1, tab2, tab3, tab4 = st.tabs(["Basic Information", "Technical Specifications", "Launch & Cost", "Raw JSON"])
    
    # Process and display basic information
    with tab1:
        st.subheader("Basic Information")
        basic_info_data = data_manager.get_satellite_data(satellite_name, "basic_info")
        if basic_info_data and "data" in basic_info_data:
            data = basic_info_data["data"]
            st.json(data)
            json_str = json.dumps(data, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"{satellite_name}_basic_info.json",
                mime="application/json"
            )
        else:
            if st.button("Gather Basic Information", key=f"gather_basic_{satellite_name}"):
                with st.spinner("Gathering basic information..."):
                    try:
                        basic_bot = BasicInfoBot()
                        with st.chat_message("assistant"):
                            terminal_container = st.container()
                            terminal_container.markdown("#### Agent Execution Log:")
                            status = terminal_container.empty()
                            status.info("Agent starting...")
                            stdout_capture = CaptureStdout(terminal_container)
                            old_stdout = sys.stdout
                            sys.stdout = stdout_capture
                            
                            try:
                                result = basic_bot.process_satellite(satellite_name)
                                status.success("Agent finished.")
                                if result:
                                    st.success("Basic information gathered successfully!")
                                    st.json(result)
                                    json_str = json.dumps(result, indent=2)
                                    st.download_button(
                                        label="Download JSON",
                                        data=json_str,
                                        file_name=f"{satellite_name}_basic_info.json",
                                        mime="application/json"
                                    )
                                    # Save the data
                                    data_manager.append_satellite_data(satellite_name, "basic_info", result)
                                else:
                                    st.error("Failed to gather basic information.")
                            except Exception as e:
                                status.error(f"Agent failed: {e}")
                                st.error(f"Error: {str(e)}")
                            finally:
                                sys.stdout = old_stdout
                    except Exception as e:
                        st.error(f"Failed to initialize BasicInfoBot: {str(e)}")
    
    # Process and display technical specifications
    with tab2:
        st.subheader("Technical Specifications")
        tech_specs_data = data_manager.get_satellite_data(satellite_name, "technical_specs")
        if tech_specs_data and "data" in tech_specs_data:
            data = tech_specs_data["data"]
            st.json(data)
            json_str = json.dumps(data, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"{satellite_name}_tech_specs.json",
                mime="application/json"
            )
        else:
            if st.button("Gather Technical Specifications", key=f"gather_tech_{satellite_name}"):
                with st.spinner("Gathering technical specifications..."):
                    try:
                        tech_bot = TechAgent()
                        with st.chat_message("assistant"):
                            terminal_container = st.container()
                            terminal_container.markdown("#### Agent Execution Log:")
                            status = terminal_container.empty()
                            status.info("Agent starting...")
                            stdout_capture = CaptureStdout(terminal_container)
                            old_stdout = sys.stdout
                            sys.stdout = stdout_capture
                            
                            try:
                                result = tech_bot.process_satellite(satellite_name)
                                status.success("Agent finished.")
                                if result:
                                    st.success("Technical specifications gathered successfully!")
                                    st.json(result)
                                    json_str = json.dumps(result, indent=2)
                                    st.download_button(
                                        label="Download JSON",
                                        data=json_str,
                                        file_name=f"{satellite_name}_tech_specs.json",
                                        mime="application/json"
                                    )
                                    # Save the data
                                    data_manager.append_satellite_data(satellite_name, "technical_specs", result)
                                else:
                                    st.error("Failed to gather technical specifications.")
                            except Exception as e:
                                status.error(f"Agent failed: {e}")
                                st.error(f"Error: {str(e)}")
                            finally:
                                sys.stdout = old_stdout
                    except Exception as e:
                        st.error(f"Failed to initialize TechAgent: {str(e)}")
    
    # Process and display launch and cost information
    with tab3:
        st.subheader("Launch and Cost Information")
        launch_cost_data = data_manager.get_satellite_data(satellite_name, "launch_cost_info")
        if launch_cost_data and "data" in launch_cost_data:
            data = launch_cost_data["data"]
            st.json(data)
            json_str = json.dumps(data, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"{satellite_name}_launch_cost.json",
                mime="application/json"
            )
        else:
            if st.button("Gather Launch and Cost Information", key=f"gather_launch_{satellite_name}"):
                with st.spinner("Gathering launch and cost information..."):
                    try:
                        cost_bot = CostBot()
                        with st.chat_message("assistant"):
                            terminal_container = st.container()
                            terminal_container.markdown("#### Agent Execution Log:")
                            status = terminal_container.empty()
                            status.info("Agent starting...")
                            stdout_capture = CaptureStdout(terminal_container)
                            old_stdout = sys.stdout
                            sys.stdout = stdout_capture
                            
                            try:
                                result = cost_bot.process_satellite(satellite_name)
                                status.success("Agent finished.")
                                if result:
                                    st.success("Launch and cost information gathered successfully!")
                                    st.json(result)
                                    json_str = json.dumps(result, indent=2)
                                    st.download_button(
                                        label="Download JSON",
                                        data=json_str,
                                        file_name=f"{satellite_name}_launch_cost.json",
                                        mime="application/json"
                                    )
                                    # Save the data
                                    data_manager.append_satellite_data(satellite_name, "launch_cost_info", result)
                                else:
                                    st.error("Failed to gather launch and cost information.")
                            except Exception as e:
                                status.error(f"Agent failed: {e}")
                                st.error(f"Error: {str(e)}")
                            finally:
                                sys.stdout = old_stdout
                    except Exception as e:
                        st.error(f"Failed to initialize CostBot: {str(e)}")
    
    # Display raw JSON data
    with tab4:
        st.subheader("Raw JSON Data")
        all_data = {
            "basic_info": basic_info_data.get("data", {}) if basic_info_data else {},
            "technical_specs": tech_specs_data.get("data", {}) if tech_specs_data else {},
            "launch_cost_info": launch_cost_data.get("data", {}) if launch_cost_data else {}
        }
        if any(all_data.values()):
            st.json(all_data)
            json_str = json.dumps(all_data, indent=2)
            st.download_button(
                label="Download Combined JSON",
                data=json_str,
                file_name=f"{satellite_name}_all_data.json",
                mime="application/json"
            )
        else:
            st.info("No data available for this satellite yet.")
    
    # Display last updated time if available
    if any([basic_info_data, tech_specs_data, launch_cost_data]):
        latest_data = max(
            [basic_info_data.get("last_updated") if basic_info_data else None,
             tech_specs_data.get("last_updated") if tech_specs_data else None,
             launch_cost_data.get("last_updated") if launch_cost_data else None],
            key=lambda x: x if x is not None else ""
        )
        if latest_data:
            st.sidebar.markdown(f"Last updated: {latest_data}")

else:
    st.info("Please enter a satellite name in the sidebar to begin.")