import streamlit as st
import time
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import base64
import psycopg2
from psycopg2.extras import DictCursor
import io

# Constants
MIN_MOISTURE_THRESHOLD = 30
MAX_MOISTURE_THRESHOLD = 100

# Base64 encoded background images
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return encoded_string
    except:
        return ""

# Background images (replace these with your actual image paths)
login_bg = get_base64_image("w12.jpg")  # Replace with your login image path
irrigation_bg = get_base64_image("w17.jpg")  # Replace with your irrigation image path
tips_bg = get_base64_image("w19.jpg")  # Replace with your tips image path
history_bg = get_base64_image("pc1.jpg")  # Replace with your history image path
crop_bg = get_base64_image("farm58.jpg")  # Replace with your crop management image path
dashboard_bg = get_base64_image("dash2.jpg")  # Replace with your dashboard image path
export_bg = get_base64_image("dash2.jpg")  # Replace with your export image path

# Enhanced Water saving tips with more details (without emojis)
water_saving_tips = {
    "Wheat": {
        "Clay": [
            "Use conservation tillage to improve water retention",
            "Implement furrow irrigation with 60cm spacing",
            "Alternate wetting and drying (AWD) during non-critical stages",
            "Crop rotation with legumes every 2 years"
        ],
        "Loam": [
            "Install soil moisture sensors for precision irrigation",
            "Schedule irrigation at 60-70% depletion of available water",
            "Use short-duration wheat varieties (110-120 days)",
            "Apply hydrogel polymers @ 2.5kg/ha"
        ],
        "Silt": [
            "Prepare raised beds (15-20cm height)",
            "Use sprinkler irrigation at 0.8 ETc",
            "Apply wheat straw mulch @ 5 tons/ha",
            "Use superabsorbent polymers in root zone"
        ],
        "Sand": [
            "Install subsurface clay pot irrigation",
            "Apply farmyard manure @ 10-15 tons/ha",
            "Drip irrigation with daily 4-6mm application",
            "Zinc-coated urea for better NUE"
        ]
    },
    "Cotton": {
        "Clay": [
            "Paired row planting (90/30cm)",
            "Pitcher irrigation @ 1 pitcher/plant",
            "Intercropping with green gram",
            "Broad bed furrow system"
        ],
        "Loam": [
            "Deficit irrigation (70% ET) during vegetative stage",
            "Automated drip system with tensiometers",
            "Use drought-tolerant hybrids",
            "Apply KNO3 foliar spray @ 2%"
        ],
        "Silt": [
            "Laser land leveling for uniform water distribution",
            "Irrigation at 50% DASM (depth of available soil moisture)",
            "Paddy straw mulch @ 4 tons/ha",
            "Skip-row planting pattern"
        ],
        "Sand": [
            "Subsurface geomembrane barriers",
            "Pulse drip irrigation (2hr ON/4hr OFF)",
            "Apply compost tea every 15 days",
            "Use water-retaining polymers"
        ]
    },
    "Rice": {
        "Clay": [
            "System of Rice Intensification (SRI) method",
            "Alternate wetting and drying (AWD) irrigation",
            "Apply silicon @ 500kg/ha",
            "Direct seeded rice with laser leveling"
        ],
        "Loam": [
            "Sensor-based irrigation scheduling",
            "Aerobic rice cultivation",
            "Micro-sprinkler irrigation",
            "Use of anti-transpirants"
        ],
        "Silt": [
            "Raised bed cultivation",
            "Intermittent irrigation (2cm after hairline cracks)",
            "Short duration varieties (110-115 days)",
            "Straw incorporation @ 5 tons/ha"
        ],
        "Sand": [
            "Clay subsoiling @ 30cm depth",
            "Drip irrigation with daily 6-8mm",
            "Green manuring with Sesbania",
            "Zinc-coated urea application"
        ]
    },
    "Sugarcane": {
        "Clay": [
            "Trench planting (30cm deep)",
            "Furrow irrigation with 1.2 IW/CPE ratio",
            "Paired row planting (120/60cm)",
            "Apply pressmud @ 10 tons/ha"
        ],
        "Loam": [
            "Drip irrigation with 0.8 PE",
            "ET-based scheduling",
            "Early maturing varieties (10-11 months)",
            "Foliar K application @ 1%"
        ],
        "Silt": [
            "Subsurface drip at 30cm depth",
            "Ratoon management with trash mulching",
            "Trash mulching @ 8-10 tons/ha",
            "Partial rootzone drying"
        ],
        "Sand": [
            "Clay lining of fields",
            "Intercropping with cluster bean",
            "Pulse irrigation (4 days interval)",
            "Use of biochar @ 5 tons/ha"
        ]
    },
    "Maize": {
        "Clay": [
            "Ridge and furrow system",
            "Irrigation at 50% DASM",
            "Zero tillage with residue cover",
            "Apply PAM (polyacrylamide)"
        ],
        "Loam": [
            "Conservation tillage",
            "Soil moisture sensor-based irrigation",
            "Drought-tolerant hybrids",
            "Foliar ZnSO4 @ 0.5%"
        ],
        "Silt": [
            "Sprinkler irrigation at 0.7 ET",
            "Straw mulch @ 4 tons/ha",
            "Intercropping with cowpea",
            "Irrigation at 25% depletion"
        ],
        "Sand": [
            "Subsurface irrigation with clay pipes",
            "Apply FYM @ 15 tons/ha",
            "Drip irrigation with daily 5mm",
            "Use hydrogel @ 3kg/ha"
        ]
    },
    "Grams": {
        "Clay": [
            "Broad bed furrow system",
            "Life-saving irrigation at flowering",
            "Timely sowing (1st fortnight of Nov)",
            "Kaolin spray @ 6%"
        ],
        "Loam": [
            "Minimum tillage",
            "ET-based irrigation scheduling",
            "Short duration varieties (90-100 days)",
            "Boron foliar spray @ 0.2%"
        ],
        "Silt": [
            "Sprinkler irrigation at 0.6 ET",
            "Crop residue mulch @ 3 tons/ha",
            "Intercropping with linseed",
            "Irrigation at 40% depletion"
        ],
        "Sand": [
            "Clay amendment @ 10 tons/ha",
            "FYM application @ 10 tons/ha",
            "Pulse drip irrigation",
            "Use of rhizobium culture"
        ]
    }
}

# Database connection - Updated for Neon Postgres
def connect_db():
    try:
        conn = psycopg2.connect(
            host="ep-falling-pond-addqml8d-pooler.c-2.us-east-1.aws.neon.tech",
            database="neondb",
            user="neondb_owner",
            password="npg_emHPU1b7qSOL",
            port="5432",
            sslmode="require",
            connect_timeout=10
        )
        return conn
    except Exception as e:
        st.error(f" Connection failed: {str(e)}")
        return None

# Create tables if they don't exist
def initialize_db():
    conn = connect_db()
    if not conn:
        return False
        
    cursor = conn.cursor()
    try:
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(50) NOT NULL
            )
        """)
        
        # Irrigation history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS irrigation_history (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50),
                crop_type VARCHAR(50),
                soil_type VARCHAR(50),
                moisture_level INT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Crops table (from Prosperous Farmer)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Crops (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                season VARCHAR(50),
                yield_per_acre DECIMAL(10,2),
                added_by INTEGER,
                FOREIGN KEY (added_by) REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        return True
    except psycopg2.Error as err:
        st.error(f"Database initialization error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

# Function to get minimum threshold
def get_min_threshold(crop, soil):
    thresholds = {
        "Wheat": {"Clay": 30, "Silt": 25, "Sand": 20, "Loam": 35},
        "Cotton": {"Clay": 40, "Silt": 35, "Sand": 30, "Loam": 45},
        "Maize": {"Clay": 60, "Silt": 55, "Sand": 50, "Loam": 45},
        "Sugarcane": {"Clay": 50, "Silt": 45, "Sand": 30, "Loam": 55},
        "Grams": {"Clay": 40, "Silt": 25, "Sand": 20, "Loam": 45}
    }
    return thresholds.get(crop, {}).get(soil, 0)

# Function to get maximum threshold
def get_max_threshold(crop, soil):
    thresholds = {
        "Wheat": {"Clay": 70, "Silt": 65, "Sand": 60, "Loam": 75},
        "Cotton": {"Clay": 80, "Silt": 75, "Sand": 70, "Loam": 85},
        "Rice": {"Clay": 80, "Silt": 75, "Sand": 70, "Loam": 85},
        "Maize": {"Clay": 80, "Silt": 75, "Sand": 70, "Loam": 85},
        "Sugarcane": {"Clay": 70, "Silt": 65, "Sand": 60, "Loam": 75},
        "Grams": {"Clay": 70, "Silt": 55, "Sand": 60, "Loam": 75}
    }
    return thresholds.get(crop, {}).get(soil, 100)

# Custom CSS for styling with background images
def set_background(image_base64):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{image_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )



def load_css():
    st.markdown("""
        <style>
              
            /* NEW: Perfect Card styling for tabs - NO JAVASCRIPT NEEDED */
            .stTabs [data-baseweb="tab-list"] {
                gap: 15px;
                background-color: transparent;
                justify-content: center;
                margin-bottom: 25px;
                padding: 10px 0;
            }

            .stTabs [data-baseweb="tab"] {
                height: 120px;
                width: 220px;
                padding: 0px;
                margin: 0px;
                background: #000 !important;
                border-radius: 15px;
                color: white !important;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                position: relative;
                overflow: hidden;
                border: none;
                transition: all 0.3s ease;
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            }

            /* Permanent Neon Border - Always Visible */
            .stTabs [data-baseweb="tab"]::before {
                content: '';
                position: absolute;
                inset: 0;
                width: 100%;
                height: 100%;
                border-radius: 15px;
                background: linear-gradient(-45deg, #e81cff 0%, #40c9ff 100%);
                z-index: 1;
                opacity: 0.9;
                animation: neonPulse 3s infinite ease-in-out;
            }

            /* Inner black background */
            .stTabs [data-baseweb="tab"]::after {
                content: "";
                position: absolute;
                inset: 3px;
                background: #000;
                border-radius: 12px;
                z-index: 1;
                transition: all 0.3s ease;
            }

            /* Tab text styling - Perfect centering */
            .stTabs [data-baseweb="tab"] > div {
                width: 100%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 15px;
                box-sizing: border-box;
                z-index: 2;
                position: relative;
            }

            .stTabs [data-baseweb="tab"] > div > p {
                color: white !important;
                font-size: 18px !important;
                font-weight: bold !important;
                margin: 0 !important;
                text-align: center;
                width: 100%;
                text-shadow: 0 0 8px rgba(255, 255, 255, 0.7);
                transition: all 0.3s ease;
            }

            /* Hover effects */
            .stTabs [data-baseweb="tab"]:hover::before {
                animation: neonPulse 1s infinite ease-in-out;
                opacity: 1;
            }

            .stTabs [data-baseweb="tab"]:hover > div > p {
                transform: scale(1.08);
                text-shadow: 0 0 12px #ffffff;
            }

            /* Active tab styling */
            .stTabs [data-baseweb="tab"][aria-selected="true"]::before {
                animation: neonPulse 1.5s infinite ease-in-out;
                opacity: 1;
                filter: brightness(1.2);
            }

            .stTabs [data-baseweb="tab"][aria-selected="true"] > div > p {
                color: #fff !important;
                text-shadow: 0 0 15px #e81cff, 0 0 25px #40c9ff;
                font-size: 19px !important;
            }

            @keyframes neonPulse {
                0%, 100% {
                    filter: brightness(1) blur(1px);
                    opacity: 0.8;
                }
                50% {
                    filter: brightness(1.3) blur(1.5px);
                    opacity: 1;
                }
            }

            /* Remove default Streamlit styling */
            .stTabs [data-baseweb="tab"] {
                border: none !important;
                background: transparent !important;
            }

            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                border: none !important;
                background: transparent !important;
            }

            

            /* Button styling with enhanced hover effects */
            .stButton>button {
                --border-color: linear-gradient(-45deg, #ffae00, #7e03aa, #00fffb);
                --border-width: 0.125em;
                --curve-size: 0.5em;
                --blur: 30px;
                --bg: #080312;
                --color: #afffff;
                color: var(--color);
                cursor: pointer;
                position: relative;
                isolation: isolate;
                display: inline-grid;
                place-content: center;
                padding: 0.5em 1.5em;
                font-size: 17px;
                border: 0;
                text-transform: uppercase;
                box-shadow: 10px 10px 20px rgba(0, 0, 0, 0.6);
                clip-path: polygon(
                    0% var(--curve-size),
                    var(--curve-size) 0,
                    100% 0,
                    100% calc(100% - var(--curve-size)),
                    calc(100% - var(--curve-size)) 100%,
                    0 100%
                );
                transition: color 250ms;
                width: 100%;
                border-radius: 8px;
                font-weight: bold;
            }

            .stButton>button::after,
            .stButton>button::before {
                content: "";
                position: absolute;
                inset: 0;
            }

            .stButton>button::before {
                background: var(--border-color);
                background-size: 300% 300%;
                animation: move-bg7234 5s ease infinite;
                z-index: -2;
            }

            @keyframes move-bg7234 {
                0% {
                    background-position: 31% 0%;
                }

                50% {
                    background-position: 70% 100%;
                }

                100% {
                    background-position: 31% 0%;
                }
            }

            .stButton>button::after {
                background: var(--bg);
                z-index: -1;
                clip-path: polygon(
                    var(--border-width) calc(var(--curve-size) + var(--border-width) * 0.5),
                    calc(var(--curve-size) + var(--border-width) * 0.5) var(--border-width),
                    calc(100% - var(--border-width)) var(--border-width),
                    calc(100% - var(--border-width)) calc(100% - calc(var(--curve-size) + var(--border-width) * 0.5)),
                    calc(100% - calc(var(--curve-size) + var(--border-width) * 0.5)) calc(100% - var(--border-width)),
                    var(--border-width) calc(100% - var(--border-width))
                );
                transition: clip-path 500ms;
            }

            .stButton>button:where(:hover, :focus)::after {
                clip-path: polygon(
                    calc(100% - var(--border-width)) calc(100% - calc(var(--curve-size) + var(--border-width) * 0.5)),
                    calc(100% - var(--border-width)) var(--border-width),
                    calc(100% - var(--border-width)) var(--border-width),
                    calc(100% - var(--border-width)) calc(100% - calc(var(--curve-size) + var(--border-width) * 0.5)),
                    calc(100% - calc(var(--curve-size) + var(--border-width) * 0.5)) calc(100% - var(--border-width)),
                    calc(100% - calc(var(--curve-size) + var(--border-width) * 0.5)) calc(100% - var(--border-width))
                );
                transition: 200ms;
            }

            .stButton>button:where(:hover, :focus) {
                color: #fff;
            }
            
            /* Input field styling */
            .stNumberInput, .stSelectbox, .stTextInput {
                margin-bottom: 20px;
            }
            
            /* Progress bar styling */
            .stProgress > div > div > div {
                background-color: #4CAF50;
            }
            
            /* Alert box styling */
            .stAlert {
                border-radius: 10px;
            }
            
            /* Modified Water tips card styling - removed transparent black background */
            .tip-card {
                background-color: transparent !important;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                border-left: 5px solid #4CAF50;
                box-shadow: none !important;
            }
            .tip-card h4 {
                color: #4CAF50;
                margin-top: 0;
                border-bottom: 1px solid rgba(76, 175, 80, 0.3);
                padding-bottom: 8px;
            }
            .tip-item {
                padding: 8px 0;
                border-bottom: 1px dashed rgba(0, 0, 0, 0.2);
                display: flex;
                align-items: center;
                background-color: transparent !important;
            }
            .tip-item:before {
                content: "•";
                color: #4CAF50;
                font-weight: bold;
                display: inline-block;
                width: 1em;
                margin-left: -1em;
            }
            .tip-item:last-child {
                border-bottom: none;
            }
            
            /* ============================================= */
            /* HISTORY TAB SPECIFIC STYLES - ALL TEXT YELLOW */
            /* ============================================= */
            
            /* Main history container */
            .history-content {
                color: #FFD700 !important;
            }
            
            /* All text elements in history tab */
            .history-content h1,
            .history-content h2,
            .history-content h3,
            .history-content h4,
            .history-content h5,
            .history-content h6,
            .history-content p,
            .history-content div,
            .history-content span {
                color: #FFD700 !important;
                text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
            }
            
            /* Table styling */
            table {
                background-color: rgba(0, 0, 0, 0.7) !important;
                border-radius: 10px;
                color: #FFD700 !important;
                text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
            }
            table th {
                background-color: rgba(0, 0, 0, 0.8) !important;
                font-weight: bold;
                color: #FFD700 !important;
                text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
            }
            
            .history-content .stTable {
                background-color: rgba(0, 0, 0, 0.7) !important;
                border-radius: 10px;
                overflow: hidden;
            }
            
            /* Table headers (crop_type, soil_type, etc.) */
            .history-content .stTable th {
                background-color: rgba(0, 0, 0, 0.8) !important;
                color: #FFD700 !important;
                font-weight: bold;
                text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
            }
            
            /* Table cells */
            .history-content .stTable td {
                color: #FFD700 !important;
                text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
            }
            
            /* Table rows */
            .history-content .stTable tr:nth-child(even) {
                background-color: rgba(0, 0, 0, 0.6) !important;
            }
            
            .history-content .stTable tr:nth-child(odd) {
                background-color: rgba(0, 0, 0, 0.5) !important;
            }
            
            .history-content .stTable tr:hover {
                background-color: rgba(76, 175, 80, 0.3) !important;
            }
            
            /* Chart titles and text */
            .history-content .stPlotlyChart .gtitle,
            .history-content .stPlotlyChart .xtitle,
            .history-content .stPlotlyChart .ytitle,
            .history-content .stPlotlyChart .legendtext {
                fill: #FFD700 !important;
            }
            
            /* ============================================= */
            /* END OF HISTORY TAB SPECIFIC STYLES */
            /* ============================================= */
            
            /* Sidebar styling */
            [data-testid=stSidebar] {
                background-color: rgba(0, 0, 0, 0.5) !important;
                backdrop-filter: blur(10px) !important;
                border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
            }
            [data-testid=stSidebar] * {
                color: white !important;
            }
            [data-testid=stSidebar] label {
                color: white !important;
            }
            
            /* Modified Water saving tips container - removed background */
            .tips-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
                background-color: transparent !important;
            }
            .soil-tip-card {
                background: transparent !important;
                border-radius: 10px;
                padding: 15px;
                box-shadow: none !important;
                border-top: 3px solid #4CAF50;
            }
            .soil-tip-card h4 {
                color: #4CAF50;
                margin-top: 0;
                padding-bottom: 8px;
                border-bottom: 1px solid rgba(76, 175, 80, 0.3);
            }
            .savings-card {
                background: transparent !important;
                border-radius: 10px;
                padding: 15px;
                box-shadow: none !important;
                border-top: 3px solid #4CAF50;
                grid-column: 1 / -1;
            }
            
            
            
            /* Dashboard chart styling to match history tab */
            .dashboard-chart {
                background-color: rgba(0, 0, 0, 0.7) !important;
                border-radius: 10px;
                padding: 15px;
                margin: 15px 0;
            }
            
            .dashboard-chart .gtitle,
            .dashboard-chart .xtitle,
            .dashboard-chart .ytitle,
            .dashboard-chart .legendtext {
                fill: #FFD700 !important;
            }
            
            /* Dashboard cards */
            .dashboard-card {
                position: relative;
                width: 220px;
                height: 320px;
                background: mediumturquoise;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 25px;
                font-weight: bold;
                border-radius: 15px;
                cursor: pointer;
                margin: 15px;
                padding: 20px;
                box-sizing: border-box;
                overflow: hidden;
            }

            .dashboard-card::before,
            .dashboard-card::after {
                position: absolute;
                content: "";
                width: 20%;
                height: 20%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 25px;
                font-weight: bold;
                background-color: lightblue;
                transition: all 0.5s;
            }

            .dashboard-card::before {
                top: 0;
                right: 0;
                border-radius: 0 15px 0 100%;
            }

            .dashboard-card::after {
                bottom: 0;
                left: 0;
                border-radius: 0 100%  0 15px;
            }

            .dashboard-card:hover::before,
            .dashboard-card:hover:after {
                width: 100%;
                height: 100%;
                border-radius: 15px;
                transition: all 0.5s;
            }

            .dashboard-card:hover:after {
                
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                background: rgba(0, 0, 0, 0.2);
            }
            
            .dashboard-card-content {
                z-index: 2;
                text-align: center;
                color: #2c3e50;
            }
            
            .dashboard-card h3 {
                margin-top: 0;
                font-size: 1.2rem;
            }
            
            .dashboard-card p {
                font-size: 0.9rem;
                margin: 10px 0;
            }
            
            .dashboard-card .value {
                font-size: 1.8rem;
                font-weight: bold;
                color: #4CAF50;
                margin: 15px 0;
            }
           
            /* Style for download buttons to match other buttons */
            .stDownloadButton > button {
                --border-color: linear-gradient(-45deg, #ffae00, #7e03aa, #00fffb);
                --border-width: 0.125em;
                --curve-size: 0.5em;
                --blur: 30px;
                --bg: #080312;
                --color: #afffff;
                color: var(--color);
                cursor: pointer;
                position: relative;
                isolation: isolate;
                display: inline-grid;
                place-content: center;
                padding: 0.5em 1.5em;
                font-size: 17px;
                border: 0;
                text-transform: uppercase;
                box-shadow: 10px 10px 20px rgba(0, 0, 0, 0.6);
                clip-path: polygon(
                    0% var(--curve-size),
                    var(--curve-size) 0,
                    100% 0,
                    100% calc(100% - var(--curve-size)),
                    calc(100% - var(--curve-size)) 100%,
                    0 100%
                );
                transition: color 250ms;
                width: 100%;
                border-radius: 8px;
                font-weight: bold;
            }

            .stDownloadButton > button::after,
            .stDownloadButton > button::before {
                content: "";
                position: absolute;
                inset: 0;
            }

            .stDownloadButton > button::before {
                background: var(--border-color);
                background-size: 300% 300%;
                animation: move-bg7234 5s ease infinite;
                z-index: -2;
            }

            .stDownloadButton > button::after {
                background: var(--bg);
                z-index: -1;
                clip-path: polygon(
                    var(--border-width) calc(var(--curve-size) + var(--border-width) * 0.5),
                    calc(var(--curve-size) + var(--border-width) * 0.5) var(--border-width),
                    calc(100% - var(--border-width)) var(--border-width),
                    calc(100% - var(--border-width)) calc(100% - calc(var(--curve-size) + var(--border-width) * 0.5)),
                    calc(100% - calc(var(--curve-size) + var(--border-width) * 0.5)) calc(100% - var(--border-width)),
                    var(--border-width) calc(100% - var(--border-width))
                );
                transition: clip-path 500ms;
            }

            .stDownloadButton > button:where(:hover, :focus)::after {
                clip-path: polygon(
                    calc(100% - var(--border-width)) calc(100% - calc(var(--curve-size) + var(--border-width) * 0.5)),
                    calc(100% - var(--border-width)) var(--border-width),
                    calc(100% - var(--border-width)) var(--border-width),
                    calc(100% - var(--border-width)) calc(100% - calc(var(--curve-size) + var(--border-width) * 0.5)),
                    calc(100% - calc(var(--curve-size) + var(--border-width) * 0.5)) calc(100% - var(--border-width)),
                    calc(100% - calc(var(--curve-size) + var(--border-width) * 0.5)) calc(100% - var(--border-width))
                );
                transition: 200ms;
            }

            .stDownloadButton > button:where(:hover, :focus) {
                color: #fff;
            }
            
            
            /* Metrics styling */
            [data-testid="stMetric"] {
                background-color: rgba(0, 0, 0, 0.7) !important;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }

            [data-testid="stMetricLabel"] {
                color: #FFFFFF !important;
                font-size: 16px !important;
                font-weight: bold !important;
            }

            [data-testid="stMetricValue"] {
                color: #FFD700 !important;
                font-size: 24px !important;
                font-weight: bold !important;
            }

            [data-testid="stMetricDelta"] {
                font-size: 14px !important;
            }

            /* Positive delta */
            [data-testid="stMetricDelta"] svg {
                color: #00FF00 !important;
            }

            /* Negative delta */
            [data-testid="stMetricDelta"] svg[style*="color: rgb(255, 43, 43)"] {
                color: #FF0000 !important;
            }    
            
            
            

            
        </style>
    """, unsafe_allow_html=True)









    
# Custom plotly theme for transparent black charts
def configure_plotly_charts():
    # Line chart configuration
    line_layout = dict(
        plot_bgcolor='rgba(0, 0, 0, 0.7)',
        paper_bgcolor='rgba(0, 0, 0, 0.5)',
        font=dict(color='#FFD700'),
        title_font=dict(color='#FFD700'),
        xaxis=dict(
            gridcolor='rgba(255, 215, 0, 0.2)',
            linecolor='rgba(255, 215, 0, 0.5)',
            showgrid=True,
            title_font=dict(color='#FFD700'),
            tickfont=dict(color='#FFD700')
        ),
        yaxis=dict(
            gridcolor='rgba(255, 215, 0, 0.2)',
            linecolor='rgba(255, 215, 0, 0.5)',
            showgrid=True,
            title_font=dict(color='#FFD700'),
            tickfont=dict(color='#FFD700')
        ),
        legend=dict(
            bgcolor='rgba(0, 0, 0, 0.7)',
            bordercolor='rgba(255, 215, 0, 0.3)',
            font=dict(color='#FFD700')
        )
    )
    
    # Pie chart configuration
    pie_layout = dict(
        plot_bgcolor='rgba(0, 0, 0, 0.7)',
        paper_bgcolor='rgba(0, 0, 0, 0.5)',
        font=dict(color='#FFD700'),
        title_font=dict(color='#FFD700'),
        legend=dict(
            bgcolor='rgba(0, 0, 0, 0.7)',
            bordercolor='rgba(255, 215, 0, 0.3)',
            font=dict(color='#FFD700')
        )
    )
    
    return line_layout, pie_layout

# Prosperous Farmer Functions
def register_user(username, password):
    try:
        if not username.strip():
            if st.session_state.get("language") == "اردو":
                st.error("صارف کا نام خالی نہیں ہو سکتا")
            else:
                st.error("Username cannot be empty")
            return False

        if not username.isalnum():
            if st.session_state.get("language") == "اردو":
                st.error("صارف کا نام صرف حروف اور نمبرز پر مشتمل ہونا چاہیے")
            else:
                st.error("Username must only contain letters and numbers")
            return False

        if len(password) < 6:
            if st.session_state.get("language") == "اردو":
                st.error("پاس ورڈ کم از کم 6 حروف کا ہونا چاہیے")
            else:
                st.error("Password must be at least 6 characters")
            return False

        if password.isnumeric():
            if st.session_state.get("language") == "اردو":
                st.error("پاس ورڈ صرف نمبرز پر مشتمل نہیں ہو سکتا")
            else:
                st.error("Password cannot be entirely numeric")
            return False

        connection = connect_db()
        if not connection:
            return False
            
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            if st.session_state.get("language") == "اردو":
                st.error("صارف کا نام پہلے سے موجود ہے")
            else:
                st.error("Username already exists")
            cursor.close()
            connection.close()
            return False

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id", (username, password))
        user_id = cursor.fetchone()[0]
        connection.commit()
        
        if st.session_state.get("language") == "اردو":
            st.success("کھاتہ کامیابی سے بن گیا ہے! لاگ ان کرنے کے لیے تیار ہے۔")
        else:
            st.success("Account created successfully! Please login")
            
        cursor.close()
        connection.close()
        return True
        
    except psycopg2.Error as err:
        st.error(f"Database error: {err}")
        return False

def login_user(username, password):
    connection = None
    cursor = None
    try:
        connection = connect_db()
        if not connection:
            return None
            
        cursor = connection.cursor(cursor_factory=DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        
        if user:
            st.session_state.logged_in_user = dict(user)
            st.session_state.user_id = user['id']
            
            if st.session_state.get("language") == "اردو":
                st.success("کامیابی سے لاگ ان ہو گئے!")
            else:
                st.success("Login successful!")
            return user
        else:
            if st.session_state.get("language") == "اردو":
                st.error("غلط صارف نام یا پاس ورڈ")
            else:
                st.error("Invalid username or password")
            return None
            
    except psycopg2.Error as err:
        st.error(f"Database error: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def add_crop(name, season, yield_per_acre):
    try:
        connection = connect_db()
        if not connection:
            return False
            
        cursor = connection.cursor()
        
        if not st.session_state.get("logged_in_user"):
            if st.session_state.get("language") == "اردو":
                st.error("لاگ ان کرنے کی ضرورت ہے")
            else:
                st.error("Login required")
            return False

        user_id = st.session_state.logged_in_user['id']
        
        cursor.execute(
            "INSERT INTO Crops (name, season, yield_per_acre, added_by) VALUES (%s, %s, %s, %s) RETURNING id",
            (name, season, yield_per_acre, user_id)
        )
        connection.commit()
        
        if st.session_state.get("language") == "اردو":
            st.success(f"فصل '{name}' کامیابی سے شامل کر دی گئی")
        else:
            st.success(f"Crop '{name}' added successfully")
            
        cursor.close()
        connection.close()
        return True
        
    except psycopg2.Error as err:
        st.error(f"Database error: {err}")
        return False

def get_crops():
    connection = None
    cursor = None
    try:
        connection = connect_db()
        if not connection:
            return []
            
        cursor = connection.cursor(cursor_factory=DictCursor)
        cursor.execute("SELECT id, name, season, yield_per_acre FROM Crops")
        crops = cursor.fetchall()
        return crops
        
    except psycopg2.Error as err:
        st.error(f"Database error: {err}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def delete_crop(crop_id):
    connection = None
    cursor = None
    try:
        connection = connect_db()
        if not connection:
            return
            
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM Crops WHERE id = %s", (crop_id,))
        if not cursor.fetchone():
            if st.session_state.get("language") == "اردو":
                st.error(f"فصل شناخت {crop_id} کے ساتھ موجود نہیں ہے")
            else:
                st.error(f"Crop with ID {crop_id} does not exist")
            return
            
        cursor.execute("DELETE FROM Crops WHERE id = %s", (crop_id,))
        connection.commit()
        
        if st.session_state.get("language") == "اردو":
            st.success(f"فصل شناخت {crop_id} کامیابی سے حذف ہو گئی")
        else:
            st.success(f"Crop with ID {crop_id} deleted successfully")
            
    except psycopg2.Error as err:
        st.error(f"Database error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def search_crops(keyword):
    connection = None
    cursor = None
    try:
        connection = connect_db()
        if not connection:
            return []
            
        cursor = connection.cursor(cursor_factory=DictCursor)
        query = """
            SELECT id, name, season, yield_per_acre 
            FROM Crops 
            WHERE name ILIKE %s OR season ILIKE %s
        """
        cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
        crops = cursor.fetchall()
        return crops
    except psycopg2.Error as err:
        st.error(f"Database error: {err}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            
def update_crop(crop_id, name=None, season=None, yield_per_acre=None):
    connection = None
    cursor = None
    try:
        connection = connect_db()
        if not connection:
            return
            
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Crops WHERE id = %s", (crop_id,))
        crop = cursor.fetchone()

        if not crop:
            if st.session_state.get("language") == "اردو":
                st.error(f"شناخت {crop_id} کے ساتھ فصل موجود نہیں ہے۔ تازہ کاری کا عمل ختم کر دیا گیا۔")
            else:
                st.error(f"Crop with ID {crop_id} does not exist. Update operation aborted.")
            return

        updates = []
        params = []

        if name:
            updates.append("name = %s")
            params.append(name)
        if season:
            updates.append("season = %s")
            params.append(season)
        if yield_per_acre:
            updates.append("yield_per_acre = %s")
            params.append(yield_per_acre)

        params.append(crop_id)
        query = f"UPDATE Crops SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(query, tuple(params))
        connection.commit()

        if st.session_state.get("language") == "اردو":
            st.success(f"شناخت {crop_id} والی فصل کو کامیابی کے ساتھ تازہ کر دیا گیا۔")
        else:
            st.success(f"Crop with ID {crop_id} has been successfully updated.")
            
    except psycopg2.Error as err:
        st.error(f"Database error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_analytics_data_english():
    crops = get_crops()
    if crops:
        df = pd.DataFrame(crops, columns=["id", "name", "season", "yield_per_acre"])
        df.columns = ["ID", "Name", "Season", "Yield (kg/acre)"]
        return df
    return pd.DataFrame(columns=["ID", "Name", "Season", "Yield (kg/acre)"])

def get_analytics_data_urdu():
    crops = get_crops()
    if crops:
        df = pd.DataFrame(crops, columns=["id", "name", "season", "yield_per_acre"])
        df.columns = ["شناخت", "نام", "موسم", "پیداوار (کلوگرام/ایکڑ)"]
        return df
    return pd.DataFrame(columns=["شناخت", "نام", "موسم", "پیداوار (کلوگرام/ایکڑ)"])

def display_dashboard_english():
    df = get_analytics_data_english()
    
    with st.container():
        st.markdown('<h1 style="color: #FFD700;">Analytics Dashboard</h1>', unsafe_allow_html=True)
        
        # Show loader while data is loading
        if df.empty:
            if st.session_state.get("language") == "English":
                st.info("No data available for dashboard")
            else:
                st.info("ڈیش بورڈ کے لیے کوئی ڈیٹا دستیاب نہیں")
            return
        
        # Dashboard cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="dashboard-card-content">
                    <h3>Total Crops</h3>
                    <div class="value" style="color: #FF0000;">{len(df)}</div>
                    <p>Different types of crops in your system</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_yield = df['Yield (kg/acre)'].mean()
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="dashboard-card-content">
                    <h3>Average Yield</h3>
                    <div class="value" style="color: #FF0000;">{avg_yield:.1f}</div>
                    <p>kg per acre across all crops</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_yield = df['Yield (kg/acre)'].sum()
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="dashboard-card-content">
                    <h3>Total Yield</h3>
                    <div class="value" style="color: #FF0000;">{total_yield:.0f}</div>
                    <p>kg across all your farms</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<h2 style="color: #FFD700;">Filter by Season</h2>', unsafe_allow_html=True)
            season = st.selectbox("", ["All", "Rabi", "Kharif"], key="season_filter_en")
        with col2:
            st.markdown('<h2 style="color: #FFD700;">Filter by Crop Name</h2>', unsafe_allow_html=True)
            crop_name = st.selectbox("", ["All"] + list(df['Name'].unique()), key="crop_filter_en")

        if season != "All":
            df = df[df["Season"] == season]
        if crop_name != "All":
            df = df[df["Name"] == crop_name]

        st.markdown('<h2 style="color: #FFD700;">Key Metrics</h2>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Crops", len(df))
        with col2:
            st.metric("Average Yield", f"{df['Yield (kg/acre)'].mean():.2f}")
        with col3:
            st.metric("Total Yield", f"{df['Yield (kg/acre)'].sum():.2f}")

        tab1, tab2 = st.tabs(["Bar Chart", "Pie Chart"])
        
        with tab1:
            fig = px.bar(
                df, 
                x='Name', 
                y='Yield (kg/acre)',
                title="Yield per Acre",
                color='Season',
                color_discrete_sequence=['#FFD700', '#4CAF50', '#2196F3', '#FF5722']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0.7)',
                paper_bgcolor='rgba(0, 0, 0, 0.5)',
                font=dict(color='#FFD700'),
                title_font=dict(color='#FFD700'),
                xaxis=dict(
                    gridcolor='rgba(255, 215, 0, 0.2)',
                    linecolor='rgba(255, 215, 0, 0.5)',
                    showgrid=True,
                    title_font=dict(color='#FFD700'),
                    tickfont=dict(color='#FFD700')
                ),
                yaxis=dict(
                    gridcolor='rgba(255, 215, 0, 0.2)',
                    linecolor='rgba(255, 215, 0, 0.5)',
                    showgrid=True,
                    title_font=dict(color='#FFD700'),
                    tickfont=dict(color='#FFD700')
                ),
                legend=dict(
                    bgcolor='rgba(0, 0, 0, 0.7)',
                    bordercolor='rgba(255, 215, 0, 0.3)',
                    font=dict(color='#FFD700')
                )
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            fig2 = px.pie(
                df,
                names='Season',
                values='Yield (kg/acre)',
                title="Seasonal Distribution",
                color_discrete_sequence=['#FFD700', '#4CAF50', '#2196F3', '#FF5722'],
                hole=0.3
            )
            fig2.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0.7)',
                paper_bgcolor='rgba(0, 0, 0, 0.5)',
                font=dict(color='#FFD700'),
                title_font=dict(color='#FFD700'),
                legend=dict(
                    bgcolor='rgba(0, 0, 0, 0.7)',
                    bordercolor='rgba(255, 215, 0, 0.3)',
                    font=dict(color='#FFD700')
                )
            )
            st.plotly_chart(fig2, use_container_width=True)

def display_dashboard_urdu():
    df = get_analytics_data_urdu()
    
    with st.container():
        st.markdown('<h1 style="color: #FFD700;"> تجزئیاتی ڈیش بورڈ</h1>', unsafe_allow_html=True)
        if df.empty:
            st.info("ڈیش بورڈ کے لیے کوئی ڈیٹا دستیاب نہیں")
            return
        
        # Dashboard cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="dashboard-card-content">
                    <h3>کل فصلیں</h3>
                    <div class="value" style="color: #FFD700;">{len(df)}</div>
                    <p>آپ کے نظام میں مختلف قسم کی فصلیں</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_yield = df['پیداوار (کلوگرام/ایکڑ)'].mean()
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="dashboard-card-content">
                    <h3>اوسط پیداوار</h3>
                    <div class="value" style="color: #FFD700;">{avg_yield:.1f}</div>
                    <p>تمام فصلوں میں فی ایکڑ کلوگرام</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_yield = df['پیداوار (کلوگرام/ایکڑ)'].sum()
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="dashboard-card-content">
                    <h3>کل پیداوار</h3>
                    <div class="value" style="color: #FFD700;">{total_yield:.0f}</div>
                    <p>آپ کے تمام فارموں میں کلوگرام</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<h2 style="color: #FFD700;">موسم کے اعتبار سے فلٹر کریں </h2>', unsafe_allow_html=True)
            season = st.selectbox("", ["تمام", "ربی", "خریف"], key="season_filter_urdu")
        with col2:
            st.markdown('<h2 style="color: #FFD700;">فصل کے اعتبار سے فلٹر کریں</h2>', unsafe_allow_html=True)
            crop_name = st.selectbox("", ["تمام"] + list(df['نام'].unique()), key="crop_filter_urdu")

        if season != "تمام":
            df = df[df["موسم"] == season]
        if crop_name != "تمام":
            df = df[df["نام"] == crop_name]
        st.markdown('<h2 style="color: #FFD700;">اہم اعداد و شمار</h2>', unsafe_allow_html=True)
        
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("کل فصلیں", len(df))
        with col2:
            st.metric("اوسط پیداوار", f"{df['پیداوار (کلوگرام/ایکڑ)'].mean():.2f}")
        with col3:
            st.metric("کل پیداوار", f"{df['پیداوار (کلوگرام/ایکڑ)'].sum():.2f}")

        tab1, tab2 = st.tabs(["بار چارٹ", "پائی چارٹ"])
        
        with tab1:
            fig = px.bar(
                df, 
                x='نام', 
                y='پیداوار (کلوگرام/ایکڑ)',
                title="فی ایکڑ پیداوار",
                color='موسم',
                color_discrete_sequence=['#FFD700', '#4CAF50', '#2196F3', '#FF5722']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0.7)',
                paper_bgcolor='rgba(0, 0, 0, 0.5)',
                font=dict(color='#FFD700'),
                title_font=dict(color='#FFD700'),
                xaxis=dict(
                    gridcolor='rgba(255, 215, 0, 0.2)',
                    linecolor='rgba(255, 215, 0, 0.5)',
                    showgrid=True,
                    title_font=dict(color='#FFD700'),
                    tickfont=dict(color='#FFD700')
                ),
                yaxis=dict(
                    gridcolor='rgba(255, 215, 0, 0.2)',
                    linecolor='rgba(255, 215, 0, 0.5)',
                    showgrid=True,
                    title_font=dict(color='#FFD700'),
                    tickfont=dict(color='#FFD700')
                ),
                legend=dict(
                    bgcolor='rgba(0, 0, 0, 0.7)',
                    bordercolor='rgba(255, 215, 0, 0.3)',
                    font=dict(color='#FFD700')
                )
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            fig2 = px.pie(
                df,
                names='موسم',
                values='پیداوار (کلوگرام/ایکڑ)',
                title="موسم کے لحاظ سے تقسیم",
                color_discrete_sequence=['#FFD700', '#4CAF50', '#2196F3', '#FF5722'],
                hole=0.3
            )
            fig2.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0.7)',
                paper_bgcolor='rgba(0, 0, 0, 0.5)',
                font=dict(color='#FFD700'),
                title_font=dict(color='#FFD700'),
                legend=dict(
                    bgcolor='rgba(0, 0, 0, 0.7)',
                    bordercolor='rgba(255, 215, 0, 0.3)',
                    font=dict(color='#FFD700')
                )
            )
            st.plotly_chart(fig2, use_container_width=True)
            
def display_crop_management_urdu():
    with st.container():
        st.header("فصلوں کا انتظام")
        
        action = st.selectbox(
            "عمل منتخب کریں",
            ["شامل کریں", "دیکھیں", "حذف کریں", "تلاش کریں", "اپ ڈیٹ کریں"],
            key="crop_action_urdu"
        )
        
        if action == "شامل کریں":
            st.markdown('<div class="crop-form">', unsafe_allow_html=True)
            with st.form("add_crop_form_urdu"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("فصل کا نام")
                with col2:
                    season = st.text_input("موسم (مثال: ربی، خریف)")
                yield_per_acre = st.number_input("پیداوار فی ایکڑ (کلوگرام)", min_value=0.0, step=0.1)
                
                if st.form_submit_button("فصل شامل کریں", use_container_width=True):
                    if add_crop(name, season, yield_per_acre):
                        st.success(f"{name} کامیابی سے شامل ہو گئی!")
            st.markdown('</div>', unsafe_allow_html=True)
        
        elif action == "دیکھیں":
            crops = get_crops()
            if crops:
                for crop in crops:
                    st.markdown(f"""
                    <div class="crop-card">
                        <div class="crop-card-content">
                            <h3><span class="crop-card-icon">🌱</span> {crop['name']}</h3>
                            <p><strong>موسم:</strong> {crop['season']}</p>
                            <p><strong>پیداوار فی ایکڑ:</strong> {crop['yield_per_acre']} کلوگرام</p>
                        </div>
                        <div class="crop-card-stats">
                            <div class="stat-item">
                                <div class="stat-value">{crop['id']}</div>
                                <div class="stat-label">شناخت</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">{crop['yield_per_acre']}</div>
                                <div class="stat-label">پیداوار</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("کوئی فصل دستیاب نہیں")
        
        elif action == "حذف کریں":
            st.markdown('<div class="crop-form">', unsafe_allow_html=True)
            crop_id = st.number_input("حذف کرنے کے لیے فصل کی شناخت درج کریں", min_value=1)
            if st.button("حذف کریں", use_container_width=True):
                delete_crop(crop_id)
            st.markdown('</div>', unsafe_allow_html=True)
        
        elif action == "تلاش کریں":
            st.markdown('<div class="crop-form">', unsafe_allow_html=True)
            keyword = st.text_input("نام یا موسم سے تلاش کریں")
            if st.button("تلاش کریں", use_container_width=True):
                
                results = search_crops(keyword)
                if results:
                    for crop in results:
                        st.markdown(f"""
                        <div class="crop-card">
                            <div class="crop-card-content">
                                <h3><span class="crop-card-icon">🔍</span> {crop['name']}</h3>
                                <p><strong>موسم:</strong> {crop['season']}</p>
                                <p><strong>پیداوار فی ایکڑ:</strong> {crop['yield_per_acre']} کلوگرام</p>
                            </div>
                            <div class="crop-card-stats">
                                <div class="stat-item">
                                    <div class="stat-value">{crop['id']}</div>
                                    <div class="stat-label">شناخت</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value">{crop['yield_per_acre']}</div>
                                    <div class="stat-label">پیداوار</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("کوئی مماثل فصل نہیں ملی")
            st.markdown('</div>', unsafe_allow_html=True)
        
        elif action == "اپ ڈیٹ کریں":
            st.markdown('<div class="crop-form">', unsafe_allow_html=True)
            crop_id = st.number_input("اپ ڈیٹ کے لیے فصل کی شناخت", min_value=1)
            name = st.text_input("نیا نام (خالی چھوڑیں تو موجودہ رہے گا)")
            season = st.text_input("نیا موسم (خالی چھوڑیں تو موجودہ رہے گا)")
            yield_per_acre = st.number_input("نئی پیداوار (خالی چھوڑیں تو موجودہ رہے گی)", min_value=0.0, step=0.1)
            
            if st.button("فصل اپ ڈیٹ کریں", use_container_width=True):
                update_crop(crop_id, name or None, season or None, yield_per_acre or None)
            st.markdown('</div>', unsafe_allow_html=True)

# Update the display_export_english() function
def display_export_english():
    with st.container():
        # Create tabs for Irrigation and Crops Data with card styling
        tab1, tab2 = st.tabs([
            "Irrigation Data", 
            "Crops Data"
        ])
        
        # Add custom HTML to style the tabs as cards
       
        
        with tab1:
            # Display card for Irrigation Data
            
            st.markdown('<h2 style="color: #FFD700;">Export Irrigation Data</h2>', unsafe_allow_html=True)
            
            # Get irrigation data
            conn = connect_db()
            if not conn:
                st.error("Database connection failed")
                return
                
            irrigation_data = pd.read_sql(
                "SELECT * FROM irrigation_history WHERE username = %s ORDER BY timestamp DESC", 
                conn, 
                params=(st.session_state.username,)
            )
            conn.close()
            
            if not irrigation_data.empty:
                # Convert timestamp to readable format
                irrigation_data['timestamp'] = pd.to_datetime(irrigation_data['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<h2 style="color: #FFD700;">Irrigation Data:</h2>', unsafe_allow_html=True)
                    st.dataframe(irrigation_data)
                
                with col2:
                    st.markdown('<h2 style="color: #FFD700;">Export Options:</h2>', unsafe_allow_html=True)
                    
                    # Convert to CSV and Excel
                    csv = irrigation_data.to_csv(index=False).encode('utf-8')
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        irrigation_data.to_excel(writer, index=False, sheet_name='Irrigation Data')
                    
                    # Download buttons with custom styling
                    st.download_button(
                        "Download CSV",
                        data=csv,
                        file_name="irrigation_data.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="irrigation_csv"
                    )
                    
                    st.download_button(
                        "Download Excel",
                        data=excel_buffer.getvalue(),
                        file_name="irrigation_data.xlsx",
                        mime="application/vnd.ms-excel",
                        use_container_width=True,
                        key="irrigation_excel"
                    )
            else:
                st.warning("No irrigation data available for export")
        
        with tab2:
            # Display card for Crops Data
            st.markdown('<h2 style="color: #FFD700;">Export Crops Data</h2>', unsafe_allow_html=True)
            
            # Get crops data
            crops = get_crops()
            if crops:
                df = pd.DataFrame(crops, columns=["id", "name", "season", "yield_per_acre"])
                df.columns = ["ID", "Name", "Season", "Yield (kg/acre)"]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<h2 style="color: #FFD700;">Crops Data</h2>', unsafe_allow_html=True)
                    st.dataframe(df)
                
                with col2:
                    st.markdown('<h2 style="color: #FFD700;">Export Options</h2>', unsafe_allow_html=True)
                    
                    
                    # Convert to CSV and Excel
                    csv = df.to_csv(index=False).encode('utf-8')
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Crops Data')
                    
                    # Download buttons with custom styling
                    st.download_button(
                        "Download CSV",
                        data=csv,
                        file_name="crops_data.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="crops_csv"
                    )
                    
                    st.download_button(
                        "Download Excel",
                        data=excel_buffer.getvalue(),
                        file_name="crops_data.xlsx",
                        mime="application/vnd.ms-excel",
                        use_container_width=True,
                        key="crops_excel"
                    )
            else:
                st.warning("No crops data available for export")

# Update the display_export_urdu() function similarly
def display_export_urdu():
    with st.container():
        # Create tabs for Irrigation and Crops Data with card styling
        tab1, tab2 = st.tabs([
            "آبپاشی کا ڈیٹا", 
            "فصلوں کا ڈیٹا"
        ])
        
        
        
        with tab1:
            st.markdown('<h2 style="color: #FFD700;">آبپاشی کا ڈیٹا برآمد کریں</h2>', unsafe_allow_html=True)
            
            # Get irrigation data
            conn = connect_db()
            if not conn:
                st.error("ڈیٹا بیس کنکشن ناکام ہوا")
                return
                
            irrigation_data = pd.read_sql(
                "SELECT * FROM irrigation_history WHERE username = %s ORDER BY timestamp DESC", 
                conn, 
                params=(st.session_state.username,)
            )
            conn.close()
            
            if not irrigation_data.empty:
                # Convert timestamp to readable format
                irrigation_data['timestamp'] = pd.to_datetime(irrigation_data['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<h2 style="color: #FFD700;">آبپاشی کا ڈیٹا:</h2>', unsafe_allow_html=True)
                    
                    st.dataframe(irrigation_data)
                
                with col2:
                    st.markdown('<h2 style="color: #FFD700;">برآمد کے اختیارات</h2>', unsafe_allow_html=True)
                    
                    
                    # Convert to CSV and Excel
                    csv = irrigation_data.to_csv(index=False).encode('utf-8')
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        irrigation_data.to_excel(writer, index=False, sheet_name='Irrigation Data')
                    
                    # Download buttons with custom styling
                    st.download_button(
                        "CSV ڈاؤن لوڈ کریں",
                        data=csv,
                        file_name="آبپاشی_ڈیٹا.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="irrigation_csv_urdu"
                    )
                    
                    st.download_button(
                        "ایکسل ڈاؤن لوڈ کریں",
                        data=excel_buffer.getvalue(),
                        file_name="آبپاشی_ڈیٹا.xlsx",
                        mime="application/vnd.ms-excel",
                        use_container_width=True,
                        key="irrigation_excel_urdu"
                    )
            else:
                st.warning("برآمد کے لیے کوئی آبپاشی کا ڈیٹا دستیاب نہیں")
        
        with tab2:
            # Display card for Crops Data
           
            st.markdown('<h2 style="color: #FFD700;">فصلوں کا ڈیٹا برآمد کریں</h2>', unsafe_allow_html=True)
            
            # Get crops data
            crops = get_crops()
            if crops:
                df = pd.DataFrame(crops, columns=["id", "name", "season", "yield_per_acre"])
                df.columns = ["شناخت", "نام", "موسم", "پیداوار (کلوگرام/ایکڑ)"]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<h2 style="color: #FFD700;">فصلوں کا ڈیٹا:</h2>', unsafe_allow_html=True)
                    
                    st.dataframe(df)
                
                with col2:
                    st.markdown('<h2 style="color: #FFD700;">برآمد کے اختیارات</h2>', unsafe_allow_html=True)
                    
                    # Convert to CSV and Excel
                    csv = df.to_csv(index=False).encode('utf-8')
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Crops Data')
                    
                    # Download buttons with custom styling
                    st.download_button(
                        "CSV ڈاؤن لوڈ کریں",
                        data=csv,
                        file_name="فصلیں_ڈیٹا.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="crops_csv_urdu"
                    )
                    
                    st.download_button(
                        "ایکسل ڈاؤن لوڈ کریں",
                        data=excel_buffer.getvalue(),
                        file_name="فصلیں_ڈیٹا.xlsx",
                        mime="application/vnd.ms-excel",
                        use_container_width=True,
                        key="crops_excel_urdu"
                    )
            else:
                st.warning("برآمد کے لیے کوئی فصلوں کا ڈیٹا دستیاب نہیں")
            
def display_crop_management_english():
    with st.container():
        st.header("Crop Management")
        
        action = st.selectbox(
            "Select Action",
            ["Add", "View", "Delete", "Search", "Update"],
            key="crop_action_en"
        )
        
        if action == "Add":
            st.markdown('<div class="crop-form">', unsafe_allow_html=True)
            with st.form("add_crop_form_en"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Crop Name")
                with col2:
                    season = st.text_input("Season (e.g., Rabi, Kharif)")
                yield_per_acre = st.number_input("Yield per Acre (kg)", min_value=0.0, step=0.1)
                
                if st.form_submit_button("Add Crop", use_container_width=True):
                    if add_crop(name, season, yield_per_acre):
                        st.success(f"{name} added successfully!")
            st.markdown('</div>', unsafe_allow_html=True)
        
        elif action == "View":
            crops = get_crops()
            if crops:
                for crop in crops:
                    st.markdown(f"""
                    <div class="crop-card">
                        <div class="crop-card-content">
                            <h3><span class="crop-card-icon">🌱</span> {crop['name']}</h3>
                            <p><strong>Season:</strong> {crop['season']}</p>
                            <p><strong>Yield per Acre:</strong> {crop['yield_per_acre']} kg</p>
                        </div>
                        <div class="crop-card-stats">
                            <div class="stat-item">
                                <div class="stat-value">{crop['id']}</div>
                                <div class="stat-label">ID</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">{crop['yield_per_acre']}</div>
                                <div class="stat-label">Yield</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No crops available")
        
        elif action == "Delete":
            st.markdown('<div class="crop-form">', unsafe_allow_html=True)
            crop_id = st.number_input("Enter Crop ID to Delete", min_value=1)
            if st.button("Delete", use_container_width=True):
                delete_crop(crop_id)
            st.markdown('</div>', unsafe_allow_html=True)
        
        elif action == "Search":
            st.markdown('<div class="crop-form">', unsafe_allow_html=True)
            keyword = st.text_input("Search by name or season")
            if st.button("Search", use_container_width=True):
                # Show loader while searching
                
                results = search_crops(keyword)
                if results:
                    for crop in results:
                        st.markdown(f"""
                        <div class="crop-card">
                            <div class="crop-card-content">
                                <h3><span class="crop-card-icon">🔍</span> {crop['name']}</h3>
                                <p><strong>Season:</strong> {crop['season']}</p>
                                <p><strong>Yield per Acre:</strong> {crop['yield_per_acre']} kg</p>
                            </div>
                            <div class="crop-card-stats">
                                <div class="stat-item">
                                    <div class="stat-value">{crop['id']}</div>
                                    <div class="stat-label">ID</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value">{crop['yield_per_acre']}</div>
                                    <div class="stat-label">Yield</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No matching crops found")
            st.markdown('</div>', unsafe_allow_html=True)
        
        elif action == "Update":
            st.markdown('<div class="crop-form">', unsafe_allow_html=True)
            crop_id = st.number_input("Crop ID to Update", min_value=1)
            name = st.text_input("New Name (leave blank to keep current)")
            season = st.text_input("New Season (leave blank to keep current)")
            yield_per_acre = st.number_input("New Yield (leave blank to keep current)", min_value=0.0, step=0.1)
            
            if st.button("Update Crop", use_container_width=True):
                update_crop(crop_id, name or None, season or None, yield_per_acre or None)
            st.markdown('</div>', unsafe_allow_html=True)

# Streamlit app
def main():
    # Initialize database
    if not initialize_db():
        st.error("Failed to initialize database. Some features may not work.")
        return
        
    load_css()
    
    # Configure plotly charts
    line_layout, pie_layout = configure_plotly_charts()

    # Session state for authentication
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "Irrigation"
    if 'irrigation_complete' not in st.session_state:
        st.session_state.irrigation_complete = False
    if 'logged_in_user' not in st.session_state:
        st.session_state.logged_in_user = None
    if 'language' not in st.session_state:
        st.session_state.language = "English"
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

    # Login/Signup form
    # Login/Signup form
    if not st.session_state.logged_in:
        set_background(login_bg)
        st.title("Prosperous Farmer")

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("https://cdn-icons-png.flaticon.com/512/3069/3069172.png", width=150)
        with col2:
            st.subheader("Login / Signup")

        # Language selection - FIXED (but maintains original structure)
        lang_option = st.radio(
            "Select Language", 
            ["English", "اردو"],
            horizontal=True,
            key="lang_select_login"
        )

        # Update language in session state and trigger rerun if changed
        if lang_option != st.session_state.get("language", "English"):
            st.session_state.language = lang_option
            st.rerun()

        # Display form elements based on selected language
        if st.session_state.language == "English":
            choice = st.radio("Login/Signup", ["Login", "Signup"], horizontal=True)
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            button_text = choice
        else:
            choice = st.radio("ایک آپشن منتخب کریں", ["لاگ ان", "سائن اپ"], horizontal=True)
            username = st.text_input("صارف کا نام")
            password = st.text_input("پاس ورڈ", type="password")
            button_text = "لاگ ان" if choice == "لاگ ان" else "سائن اپ"

        if st.button(button_text, key="auth_button"):
            conn = connect_db()
            if not conn:
                if st.session_state.language == "English":
                    st.error("Database connection failed")
                else:
                    st.error("ڈیٹا بیس کنکشن ناکام ہوا")
                return

            cursor = conn.cursor()
            if (choice == "Login" or choice == "لاگ ان"):
                cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
                if cursor.fetchone():
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    if st.session_state.language == "English":
                        st.success("Logged in successfully!")
                    else:
                        st.success("کامیابی سے لاگ ان ہو گئے!")
                    time.sleep(1)
                    st.rerun()
                else:
                    if st.session_state.language == "English":
                        st.error("Invalid username or password")
                    else:
                        st.error("غلط صارف نام یا پاس ورڈ")
            elif (choice == "Signup" or choice == "سائن اپ"):
                try:
                    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                    conn.commit()
                    if st.session_state.language == "English":
                        st.success("Account created successfully! Please login")
                    else:
                        st.success("کھاتہ کامیابی سے بن گیا ہے! لاگ ان کرنے کے لیے تیار ہے۔")
                except psycopg2.IntegrityError:
                    if st.session_state.language == "English":
                        st.error("Username already exists")
                    else:
                        st.error("صارف کا نام پہلے سے موجود ہے")
            cursor.close()
            conn.close()
        return

        # Main app functionality with tabs
    st.sidebar.title("Navigation")
    tabs = ["Irrigation", "Water Saving Tips", "Crop Management", "Dashboard", "Export Data", "Irrigation History"]
    st.session_state.current_tab = st.sidebar.radio("Go to", tabs, index=tabs.index(st.session_state.current_tab if st.session_state.current_tab != "History" else "Irrigation History"))

    # Language selection in sidebar
    st.sidebar.markdown("---")
    st.session_state.language = st.sidebar.radio(
        "Language / زبان", 
        ["English", "اردو"],
        key="lang_select_sidebar"
    )

    # Set background based on current tab
    if st.session_state.current_tab == "Irrigation":
        set_background(irrigation_bg)
    elif st.session_state.current_tab == "Water Saving Tips":
        set_background(tips_bg)
    elif st.session_state.current_tab == "Irrigation History":
        set_background(history_bg)
    elif st.session_state.current_tab == "Crop Management":
        set_background(crop_bg)
    elif st.session_state.current_tab == "Dashboard":
        set_background(dashboard_bg)
    elif st.session_state.current_tab == "Export Data":
        set_background(export_bg)

    # Initialize session state for irrigation
    if 'irrigated_crops' not in st.session_state:
        st.session_state.irrigated_crops = set()
    if 'progress' not in st.session_state:
        st.session_state.progress = 0
    if 'irrigation_active' not in st.session_state:
        st.session_state.irrigation_active = False
    if 'irrigation_complete' not in st.session_state:
        st.session_state.irrigation_complete = False

    # Irrigation Tab
    if st.session_state.current_tab == "Irrigation":
        if st.session_state.language == "English":
            st.title("Smart Irrigation Control Panel")
        else:
            st.title("سمارٹ آبپاشی کنٹرول پینل")
        
        # Input fields
        if st.session_state.language == "English":
            moisture_level = st.number_input("Enter current soil moisture level", min_value=0, max_value=100, value=50)
            crop_type = st.selectbox("Select crop type", ["Wheat", "Cotton", "Rice", "Sugarcane", "Maize", "Grams"])
            soil_type = st.selectbox("Select soil type", ["Clay", "Silt", "Sand", "Loam"])
        else:
            moisture_level = st.number_input("موجودہ مٹی کی نمی کی سطح درج کریں", min_value=0, max_value=100, value=50)
            crop_type = st.selectbox("فصل کی قسم منتخب کریں", ["Wheat", "Cotton", "Rice", "Sugarcane", "Maize", "Grams"])
            soil_type = st.selectbox("مٹی کی قسم منتخب کریں", ["Clay", "Silt", "Sand", "Loam"])

        # Check if this crop-soil combination has already been irrigated
        crop_soil_key = f"{crop_type}-{soil_type}"
        if crop_soil_key in st.session_state.irrigated_crops:
            if st.session_state.language == "English":
                st.error(f"This {crop_type} crop in {soil_type} soil has already been irrigated. Please reset irrigation status if you want to irrigate again.")
            else:
                st.error(f"{soil_type} مٹی میں {crop_type} فصل پہلے ہی آبپاشی کی جا چکی ہے۔ اگر آپ دوبارہ آبپاشی کرنا چاہتے ہیں تو آبپاشی کی حیثیت کو دوبارہ ترتیب دیں۔")

        # Buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.session_state.language == "English":
                if st.button("Start Irrigation"):
                    if crop_soil_key in st.session_state.irrigated_crops:
                        st.error(f"This {crop_type} crop in {soil_type} soil has already been irrigated. Please reset irrigation status if you want to irrigate again.")
                    else:
                        min_threshold = get_min_threshold(crop_type, soil_type)
                        max_threshold = get_max_threshold(crop_type, soil_type)
                        if moisture_level < min_threshold or moisture_level > max_threshold:
                            st.warning(f"Soil moisture levels between {min_threshold} and {max_threshold} are suitable for {crop_type} crop in {soil_type} soil type.")
                        else:
                            st.session_state.irrigation_active = True
                            st.session_state.progress = 0
                            st.session_state.irrigation_complete = False
            else:
                if st.button("آبپاشی شروع کریں"):
                    if crop_soil_key in st.session_state.irrigated_crops:
                        st.error(f"{soil_type} مٹی में {crop_type} فصل پہلے ہی آبپاشی کی جا چکی ہے۔ اگر آپ دوبارہ آبپاشی کرنا چاہتے ہیں تو آبپاشی کی حیثیت کو دوبارہ ترتیب دیں۔")
                    else:
                        min_threshold = get_min_threshold(crop_type, soil_type)
                        max_threshold = get_max_threshold(crop_type, soil_type)
                        if moisture_level < min_threshold or moisture_level > max_threshold:
                            st.warning(f"{soil_type} مٹی میں {crop_type} فصل کے لیے {min_threshold} اور {max_threshold} کے درمیان مٹی کی نمی کی سطح موزوں ہے۔")
                        else:
                            st.session_state.irrigation_active = True
                            st.session_state.progress = 0
                            st.session_state.irrigation_complete = False

        with col2:
            if st.session_state.language == "English":
                if st.button("Stop Irrigation"):
                    if st.session_state.irrigation_active:
                        st.session_state.irrigation_active = False
                        st.warning("Irrigation stopped. You'll need to reset irrigation status to irrigate this crop again.")
                        # Mark as complete even if stopped to prevent restarting without reset
                        st.session_state.irrigation_complete = True
            else:
                if st.button("آبپاشی روکیں"):
                    if st.session_state.irrigation_active:
                        st.session_state.irrigation_active = False
                        st.warning("آبپاشی بند کردی گئی۔ اس فصل کو دوبارہ آبپاشی کرنے کے لیے آپ کو آبپاشی کی حیثیت کو دوبارہ ترتیب دینا ہوگا۔")
                        # Mark as complete even if stopped to prevent restarting without reset
                        st.session_state.irrigation_complete = True

        with col3:
            if st.session_state.language == "English":
                if st.button("Reset Irrigation Status"):
                    st.session_state.irrigated_crops.discard(crop_soil_key)
                    st.session_state.progress = 0
                    st.session_state.irrigation_complete = False
                    st.success("Irrigation status has been reset. You can now irrigate crops again.")
            else:
                if st.button("آبپاشی کی حیثیت دوبارہ ترتیب دیں"):
                    st.session_state.irrigated_crops.discard(crop_soil_key)
                    st.session_state.progress = 0
                    st.session_state.irrigation_complete = False
                    st.success("آبپاشی کی حیثیت دوبارہ ترتیب دی گئی ہے۔ اب آپ فصلوں کو دوبارہ آبپاشی کر سکتے ہیں۔")

        # Progress bar
        if st.session_state.irrigation_active and not st.session_state.irrigation_complete:
            progress_bar = st.progress(st.session_state.progress)
            while st.session_state.progress < 100 and st.session_state.irrigation_active:
                time.sleep(0.1)
                st.session_state.progress += 1
                progress_bar.progress(st.session_state.progress)
                if st.session_state.progress >= 100:
                    st.session_state.irrigation_active = False
                    st.session_state.irrigation_complete = True
                    st.session_state.irrigated_crops.add(crop_soil_key)
                    if st.session_state.language == "English":
                        st.success("Soil is fully irrigated.")
                    else:
                        st.success("مٹی پوری طرح سے آبپاشی ہو چکی ہے۔")

                    # Save irrigation history to database
                    conn = connect_db()
                    if not conn:
                        st.error("Database connection failed")
                        return
                        
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO irrigation_history (username, crop_type, soil_type, moisture_level)
                        VALUES (%s, %s, %s, %s)
                    """, (st.session_state.username, crop_type, soil_type, moisture_level))
                    conn.commit()
                    cursor.close()
                    conn.close()

    # Water Saving Tips Tab
    elif st.session_state.current_tab == "Water Saving Tips":
        if st.session_state.language == "English":
            st.title("Water Saving Recommendations")
            
            crop_type = st.selectbox("Select crop type for water saving tips", 
                                   ["Wheat", "Cotton", "Rice", "Sugarcane", "Maize", "Grams"])
            
            soil_type = st.selectbox("Select soil type", ["Clay", "Silt", "Sand", "Loam"], key="soil_type_tips")
            
            if st.button("Get Water Saving Tips"):
                st.subheader(f"Optimized Water Saving Techniques for {crop_type} in {soil_type} Soil")
                
                tips = water_saving_tips.get(crop_type, {}).get(soil_type, [])
                
                if tips:
                    st.markdown("""
                    <div class="tips-container">
                        <div class="soil-tip-card">
                            <h4>Best Practices</h4>
                    """, unsafe_allow_html=True)
                    
                    for tip in tips:
                        st.markdown(f"""
                        <div class="tip-item">{tip}</div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("""
                        </div>
                        <div class="savings-card">
                            <h4>Expected Water Savings</h4>
                            <p>Implementing these techniques can save <strong>30-50%</strong> of irrigation water while maintaining or increasing yield.</p>
                            <p><strong>Pro Tip:</strong> Combine 2-3 methods for maximum efficiency</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("No specific tips available for this crop-soil combination")
        else:
            st.title("پانی بچانے کی سفارشات")
            
            crop_type = st.selectbox("پانی بچانے کی تجاویز کے لیے فصل کی قسم منتخب کریں", 
                                   ["Wheat", "Cotton", "Rice", "Sugarcane", "Maize", "Grams"])
            
            soil_type = st.selectbox("مٹی کی قسم منتخب کریں", ["Clay", "Silt", "Sand", "Loam"], key="soil_type_tips_urdu")
            
            if st.button("پانی بچانے کی تجاویز حاصل کریں"):
                st.subheader(f"{soil_type} مٹی میں {crop_type} کے لیے بہترین پانی بچانے کی تکنیکیں")
                
                tips = water_saving_tips.get(crop_type, {}).get(soil_type, [])
                
                if tips:
                    st.markdown("""
                    <div class="tips-container">
                        <div class="soil-tip-card">
                            <h4>بہترین طریقے</h4>
                    """, unsafe_allow_html=True)
                    
                    for tip in tips:
                        st.markdown(f"""
                        <div class="tip-item">{tip}</div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("""
                        </div>
                        <div class="savings-card">
                            <h4>متوقع پانی کی بچت</h4>
                            <p>ان تکنیکوں کو لاگو کرنے سے پیداوار برقرار رکھتے ہوئے یا بڑھاتے ہوئے آبپاشی کے پانی کی <strong>30-50%</strong> بچت ہو سکتی ہے۔</p>
                            <p><strong>پیشہ ورانہ مشورہ:</strong> زیادہ سے زیادہ کارکردگی کے لیے 2-3 طریقوں کو یکجا کریں</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("اس فصل اور مٹی کے مجموعے کے لیے کوئی مخصوص تجاویز دستیاب نہیں ہیں")

    # Crop Management Tab (from Prosperous Farmer)
    elif st.session_state.current_tab == "Crop Management":
        if st.session_state.language == "English":
            display_crop_management_english()
        else:
            display_crop_management_urdu()

    # Dashboard Tab (from Prosperous Farmer)
    elif st.session_state.current_tab == "Dashboard":
        if st.session_state.language == "English":
            display_dashboard_english()
        else:
            display_dashboard_urdu()

    # Export Data Tab (from Prosperous Farmer)
    elif st.session_state.current_tab == "Export Data":
        if st.session_state.language == "English":
            display_export_english()
        else:
            display_export_urdu()

    # Irrigation History Tab (renamed from History)
    elif st.session_state.current_tab == "Irrigation History":
        st.markdown('<div class="history-content">', unsafe_allow_html=True)
        
        if st.session_state.language == "English":
            # Title with direct styling
            st.markdown('<h1 style="color:#FFD700;text-shadow:-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,1px 1px 0 #000">Irrigation History</h1>', unsafe_allow_html=True)
        else:
            st.markdown('<h1 style="color:#FFD700;text-shadow:-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,1px 1px 0 #000">آبپاشی کی تاریخ</h1>', unsafe_allow_html=True)
        
       
        
        conn = connect_db()
        if not conn:
            st.error("Database connection failed")
            return
            
        history = pd.read_sql("SELECT * FROM irrigation_history WHERE username = %s ORDER BY timestamp DESC", 
                            conn, params=(st.session_state.username,))
        conn.close()
        
        if not history.empty:
            # Convert timestamp to readable format
            history['timestamp'] = pd.to_datetime(history['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Display data in a styled table with transparent black background and yellow text
            st.markdown('<div class="history-table">', unsafe_allow_html=True)
            st.table(history[['crop_type', 'soil_type', 'moisture_level', 'timestamp']])
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Visualization
            if st.session_state.language == "English":
                st.markdown('<h2 style="color:#FFD700;text-shadow:-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,1px 1px 0 #000">Moisture Level Trends</h2>', unsafe_allow_html=True)
            else:
                st.markdown('<h2 style="color:#FFD700;text-shadow:-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,1px 1px 0 #000">نمی کی سطح کے رجحانات</h2>', unsafe_allow_html=True)
                
            fig = px.line(
                history, 
                x="timestamp", 
                y="moisture_level", 
                color="crop_type",
                title="Moisture Level Over Time",
                color_discrete_sequence=['#FFD700', '#4CAF50', '#2196F3', '#FF5722']
            )
            fig.update_layout(line_layout)
            fig.update_layout(
                title_font_color='#FFD700',
                font_color='#FFD700',
                xaxis_title_font_color='#FFD700',
                yaxis_title_font_color='#FFD700',
                legend_font_color='#FFD700'
            )
            st.plotly_chart(fig)
            
            if st.session_state.language == "English":
                st.markdown('<h2 style="color:#FFD700;text-shadow:-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,1px 1px 0 #000">Irrigation by Crop Type</h2>', unsafe_allow_html=True)
            else:
                st.markdown('<h2 style="color:#FFD700;text-shadow:-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,1px 1px 0 #000">فصل کی قسم کے لحاظ سے آبپاشی</h2>', unsafe_allow_html=True)
                
            fig2 = px.pie(
                history, 
                names="crop_type", 
                title="Irrigation Distribution by Crop",
                color_discrete_sequence=['#FFD700', '#4CAF50', '#2196F3', '#FF5722']
            )
            fig2.update_layout(pie_layout)
            fig2.update_layout(
                title_font_color='#FFD700',
                font_color='#FFD700',
                legend_font_color='#FFD700'
            )
            st.plotly_chart(fig2)
        else:
            if st.session_state.language == "English":
                st.info("No irrigation history found")
            else:
                st.info("آبپاشی کی کوئی تاریخ نہیں ملی")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Logout button
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.logged_in_user = None
        st.rerun()
        

if __name__ == "__main__":
    main()
