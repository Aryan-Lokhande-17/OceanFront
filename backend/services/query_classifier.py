"""Classify user queries into different intent types"""

class QueryClassifier:
    """Classify queries to determine if they need data or explanation"""
    
    # Keywords for different query types
    EXPLANATION_KEYWORDS = [
        'explain', 'why', 'how does', 'what causes', 'describe the', 'tell me about',
        'what is', 'what are', 'science', 'mechanism', 'process', 'effect', 'impact',
        'monsoon', 'seasonal', 'pattern', 'trend', 'variation', 'change', 'affect',
        'understand', 'learn', 'know about', 'insight', 'analysis', 'cause', 'reason',
        'what makes', 'how come', 'what leads to'
    ]
    
    DATA_KEYWORDS = [
        'show me', 'what data', 'available', 'measurements', 'readings', 'values',
        'depth', 'temperature', 'salinity', 'pressure', 'buoy', 'platform',
        'latitude', 'longitude', 'location', 'how many', 'count', 'list',
        'give me', 'retrieve', 'fetch', 'get', 'display', 'table'
    ]
    
    DESCRIPTIVE_KEYWORDS = [
        'what data is available', 'what measurements', 'what information',
        'what do we have', 'describe the data', 'what columns', 'what fields'
    ]
    
    @staticmethod
    def classify(query: str) -> str:
        """
        Classify query intent
        
        Returns:
            'explanation' - User wants scientific explanation/insights
            'data' - User wants actual data values/measurements
            'descriptive' - User wants to know what data is available
            'unknown' - Could not determine intent
        """
        query_lower = query.lower().strip()
        
        # Check for specific patterns first
        if any(term in query_lower for term in ['circulation', 'current', 'gyre', 'eddy', 'upwelling', 'downwelling']):
            if any(word in query_lower for word in ['what', 'how', 'explain', 'describe']):
                return 'explanation'
            return 'data'
                
        # Check for descriptive queries
        if any(keyword in query_lower for keyword in QueryClassifier.DESCRIPTIVE_KEYWORDS):
            return 'descriptive'
        
        # Check for explanation queries
        explanation_indicators = [
            any(keyword in query_lower for keyword in QueryClassifier.EXPLANATION_KEYWORDS),
            query_lower.startswith(('what', 'why', 'how', 'explain', 'describe', 'tell me'))
        ]
        
        if any(explanation_indicators):
            # Exclude if it's actually a data request
            if not any(keyword in query_lower for keyword in ['show', 'display', 'table', 'list', 'data', 'values']):
                return 'explanation'
        
        # Default to data query if not clearly something else
        return 'data'
    
    @staticmethod
    def get_explanation_response(query: str) -> str:
        """Generate oceanographic explanation for the query"""
        query_lower = query.lower()
        
        # Indian Ocean circulation
        if any(term in query_lower for term in ['circulation', 'current', 'gyre', 'indian ocean current']):
            return """## 🌊 Indian Ocean Circulation Patterns

### **Major Current Systems**
- **South Equatorial Current**: Westward flow between 10°S and 5°N
- **Monsoon Currents**: Reverses seasonally with monsoon winds
  - **Summer Monsoon Current**: Northeastward (May-September)
  - **Winter Monsoon Current**: Southwestward (November-February)
- **Southwest Monsoon Current**: Strong flow along Indian coast
- **Leeuwin Current**: Southward flow along Western Australia

### **Seasonal Variations**
- **Summer Monsoon (June-September)**:
  - Strong southwest winds drive northeastward currents
  - Upwelling along Arabian coast
  - Deep mixing in northern Arabian Sea
  
- **Winter Monsoon (December-February)**:
  - Northeast winds reverse surface flow
  - Downwelling in northern Arabian Sea
  - Stronger mixing in Bay of Bengal

### **Key Features**
- **Great Whirl**: Large, seasonal anticyclonic eddy
- **Equatorial Jets**: Strong eastward flows along equator
- **Coastal Upwelling**: Off Somalia and Oman coasts
- **Bay of Bengal**: Strong freshwater influence from rivers

### **Ocean-Atmosphere Interactions**
- Monsoon winds drive surface currents
- Sea surface temperature affects monsoon strength
- Freshwater input impacts ocean stratification
- Affects regional climate and marine ecosystems

Argo floats help track these circulation patterns by measuring:
- Temperature and salinity profiles
- Current velocities
- Water mass properties
- Mixed layer depth variations"""

        # Monsoon/seasonal effects
        if any(word in query_lower for word in ['monsoon', 'seasonal', 'pattern', 'affect']):
            return """## 🌊 Monsoon Effects on Ocean Conditions

The monsoon system significantly impacts Indian Ocean oceanography:

### **Southwest Monsoon (June-September)**
- **Wind-driven upwelling**: Strong winds push surface water away, bringing cold, nutrient-rich water from depth
- **Temperature drop**: Surface temperatures can decrease by 5-10°C in upwelling zones
- **Salinity changes**: Freshwater input from increased rainfall affects coastal salinity
- **Enhanced productivity**: Nutrient upwelling supports phytoplankton blooms

### **Northeast Monsoon (December-February)**
- **Weak upwelling**: Lighter winds result in warmer surface waters
- **Temperature rise**: Surface temperatures increase, especially in the Arabian Sea
- **Stable stratification**: Strong thermocline develops, limiting vertical mixing
- **Lower productivity**: Reduced nutrient availability limits biological activity

### **Transition Periods (March-May, October-November)**
- **Variable conditions**: Wind patterns shift, creating transitional oceanographic states
- **Mixed layer changes**: Thermocline depth fluctuates
- **Migratory species**: Marine life responds to changing food availability

### **Argo Buoy Observations**
Our Argo floats capture these seasonal variations through:
- Temperature profiles at multiple depths
- Salinity measurements showing freshwater influence
- Pressure data indicating water mass movements

These measurements help us understand how monsoons drive ocean circulation and affect marine ecosystems."""
        
        # Temperature patterns
        elif any(word in query_lower for word in ['temperature', 'thermal', 'warm', 'heat']):
            return """## 🌡️ Ocean Temperature Patterns

### **Temperature Structure in the Indian Ocean**
- **Surface layer (0-50m)**: Warmest, influenced by solar heating and monsoons
- **Thermocline (50-200m)**: Rapid temperature decrease with depth
- **Deep waters (>200m)**: Cold, stable temperatures (~4-10°C)

### **Seasonal Variations**
- **Summer (SW Monsoon)**: Upwelling brings cold water; surface temps drop
- **Winter (NE Monsoon)**: Weak upwelling; surface temps rise
- **Transition**: Rapid changes in thermal structure

### **Geographic Patterns**
- **Arabian Sea**: Experiences stronger monsoon effects, larger temperature swings
- **Bay of Bengal**: More stable due to freshwater input from rivers
- **Equatorial region**: Less seasonal variation, more consistent temperatures

### **Biological Implications**
- Temperature affects metabolic rates of marine organisms
- Thermocline acts as barrier to vertical mixing
- Upwelling brings nutrients, supporting food webs

Our Argo buoys track these patterns continuously, providing crucial data for climate and ecosystem studies."""
        
        # Salinity patterns
        elif any(word in query_lower for word in ['salinity', 'salt']):
            return """## 🧂 Ocean Salinity Patterns

### **Salinity Variations in the Indian Ocean**
- **Open ocean**: ~35 PSU (Practical Salinity Units)
- **Coastal areas**: Lower due to river discharge (20-30 PSU)
- **Evaporation zones**: Higher salinity (>36 PSU)

### **Monsoon Influence**
- **SW Monsoon**: Increased rainfall lowers coastal salinity
- **NE Monsoon**: Drier conditions, higher evaporation increases salinity
- **Bay of Bengal**: Freshwater from Ganges-Brahmaputra rivers significantly lowers salinity

### **Density Effects**
- Salinity combined with temperature determines water density
- Affects water mass formation and circulation
- Influences vertical stratification

### **Biological Significance**
- Affects osmoregulation in marine organisms
- Influences nutrient cycling
- Impacts phytoplankton communities

Argo floats measure salinity at multiple depths, helping us understand water mass movements and mixing processes."""
        
        # Pressure/depth
        elif any(word in query_lower for word in ['pressure', 'depth', 'deep']):
            return """## 📊 Pressure and Depth in the Ocean

### **Pressure Characteristics**
- **Surface (0m)**: ~1 atmosphere (101.3 kPa)
- **Increases with depth**: ~1 atmosphere per 10 meters
- **Deep ocean (>1000m)**: Extreme pressures (>100 atmospheres)

### **Depth Zones**
- **Epipelagic (0-200m)**: Sunlit zone, most biological activity
- **Mesopelagic (200-1000m)**: Twilight zone, sparse life
- **Bathypelagic (>1000m)**: Abyssal zone, extreme conditions

### **Oceanographic Importance**
- Pressure affects gas solubility and organism physiology
- Determines water density and circulation patterns
- Influences nutrient availability and mixing

### **Argo Measurements**
- Floats measure pressure to determine depth
- Pressure data helps identify water masses
- Used to calculate water density and circulation

Our Argo buoys can profile down to 2000m, capturing the full range of ocean conditions."""
        
        # General oceanography
        else:
            return """## 🌊 Indian Ocean Oceanography

The Indian Ocean is one of the world's most dynamic marine systems:

### **Key Characteristics**
- **Monsoon-driven**: Unique seasonal wind patterns drive circulation
- **Warm waters**: Tropical and subtropical climate
- **High productivity**: Upwelling zones support rich ecosystems
- **Complex circulation**: Multiple currents and eddies

### **Argo Float Network**
- Autonomous profiling floats measuring temperature, salinity, and pressure
- Global coverage with focus on Indian Ocean
- Data transmitted via satellite in real-time
- Essential for climate monitoring and weather prediction

### **Measurements Available**
- **Temperature**: Surface to 2000m depth
- **Salinity**: Water mass identification
- **Pressure**: Depth and density information
- **Profiles**: Vertical structure of the water column

### **Scientific Applications**
- Climate change monitoring
- Ocean circulation studies
- Biological productivity assessment
- Weather and monsoon prediction

Explore our data to understand these fascinating ocean processes!"""
    
    @staticmethod
    def get_descriptive_response(query: str) -> str:
        """Describe what data is available"""
        return """## 📦 Available Ocean Data

### **Measurements from Argo Buoys**
We have comprehensive oceanographic data from Argo floats in the Indian Ocean:

**Temperature (temp)**
- Range: 25-36°C in our dataset
- Depth profiles: Multiple measurements from surface to 2000m
- Precision: 0.01°C

**Salinity (psal)**
- Range: 0.01-0.02 PSU in our dataset
- Indicates water mass characteristics
- Precision: 0.01 PSU

**Pressure (pres)**
- Range: -0.20 to 0.30 dbar in our dataset
- Indicates depth and water density
- Used to calculate water mass properties

### **Location Information**
- **Latitude/Longitude**: Precise buoy positions
- **Platforms**: 2 unique Argo buoys (IDs: 1901514, 1901605)
- **Coverage**: Indian Ocean region (Arabian Sea, Bay of Bengal)

### **Data Volume**
- **Total Records**: 567 measurements
- **Unique Buoys**: 2
- **Depth Levels**: Multiple profiles per buoy
- **Time Coverage**: 2019 Argo profiles

### **Data Quality**
- NOAA Argo program data
- Quality-controlled measurements
- Real-time transmission capability

### **How to Query**
Ask for specific measurements:
- "Show me temperature data"
- "What depth measurements are available?"
- "Display salinity for each buoy"
- "How many unique buoys do we have?"

Or ask for explanations:
- "Explain monsoon effects"
- "How does temperature vary with depth?"
- "What causes salinity changes?"
"""
