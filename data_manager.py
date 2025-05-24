import json
import os
from datetime import datetime

class SatelliteDataManager:
    def __init__(self):
        self.data_file = "satellite_data.json"
        self.load_data()

    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def save_data(self):
        """Save data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def append_satellite_data(self, satellite_name, data_type, data):
        """Append or update satellite data"""
        if satellite_name not in self.data:
            self.data[satellite_name] = {}
        
        self.data[satellite_name][data_type] = {
            "data": data,
            "last_updated": datetime.now().isoformat()
        }
        self.save_data()

    def get_satellite_data(self, satellite_name, data_type=None):
        """Get satellite data for a specific satellite and optionally a specific data type"""
        if satellite_name not in self.data:
            return None
        
        if data_type:
            return self.data[satellite_name].get(data_type)
        return self.data[satellite_name]

    def get_all_satellites(self):
        """Get a list of all satellites in the database"""
        return list(self.data.keys())

    def delete_satellite_data(self, satellite_name):
        """Delete all data for a specific satellite"""
        if satellite_name in self.data:
            del self.data[satellite_name]
            self.save_data()
            return True
        return False
