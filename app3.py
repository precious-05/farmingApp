import plotly.express as px
import psycopg2  # Changed from mysql.connector
import pandas as pd
import streamlit as st 
import base64  
import io
import os
from datetime import datetime
from psycopg2.extras import DictCursor  # Added for PostgreSQL dictionary curso


def set_background_and_styles(image_file):
    try:
        with open(image_file, "rb") as file:
            encoded_image = base64.b64encode(file.read()).decode()
            background_style = f"background-image: url('data:image/jpg;base64,{encoded_image}');"
    except FileNotFoundError:
        st.error(f"Error: {image_file} not found! Make sure the image file exists in the same directory")
    
    st.markdown(
        f"""
        <style>
        #root .stApp {{
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
            {background_style}
        }}
            
     </style>
        """,
        unsafe_allow_html=True
    )       
        
        
# Premium UI Configuration (unchanged)
def set_premium_ui():
    st.set_page_config(
        page_title="Prosperous Farmer",
        page_icon="🚜",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown(f"""
    <style>
    /* Modern Gradient Color Scheme */
    :root {{
        --button-gradient-start: #6C63FF;  /* Vibrant purple-blue */
        --button-gradient-end: #4A90E2;   /* Soft blue */
        --tab-gradient-start: #FF7E5F;    /* Coral */
        --tab-gradient-end: #FEB47B;      /* Peach */
        --tab-active-gradient-start: #6C63FF; /* Matching button theme */
        --tab-active-gradient-end: #4A90E2;
        --glass-border: 1px solid rgba(255, 255, 255, 0.2);
        --glass-highlight: 1px solid rgba(255, 255, 255, 0.4);
    }}

    .stSidebar{{
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(12px);
        border-radius: 16px;
        border: var(--glass-border);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        font-weight: 600px !important;
        font-weight: bold;
    }}
    
    /* ===== MODERN BUTTONS ===== */
    .stButton>button, 
    .stDownloadButton>button,
    .stFormSubmitButton>button {{
        background: linear-gradient(
            135deg, 
            var(--button-gradient-start), 
            var(--button-gradient-end)
        ) !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 
            0 4px 12px rgba(0,0,0,0.15),
            inset 0 1px 0 rgba(255,255,255,0.2) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        font-size: 1rem !important;
        text-shadow: 0 1px 1px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
    }}

    /* Button Hover Effect */
    .stButton>button:hover, 
    .stDownloadButton>button:hover,
    .stFormSubmitButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 
            0 8px 20px rgba(108, 99, 255, 0.3),
            0 4px 12px rgba(0,0,0,0.2) !important;
        background: linear-gradient(
            135deg, 
            #7B72FF,  /* Slightly brighter */
            #5A9CFF
        ) !important;
    }}

    /* Button Active/Press Effect */
    .stButton>button:active, 
    .stDownloadButton>button:active,
    .stFormSubmitButton>button:active {{
        transform: translateY(1px);
        box-shadow: 
            0 2px 6px rgba(0,0,0,0.2),
            inset 0 1px 2px rgba(0,0,0,0.2) !important;
    }}

    /* ===== MODERN TABS ===== */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px !important;
        padding: 4px !important;
        background: rgba(255,255,255,0.05) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px);
    }}

    .stTabs [data-baseweb="tab"] {{
        background: linear-gradient(
            135deg, 
            var(--tab-gradient-start), 
            var(--tab-gradient-end)
        ) !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        margin: 0 2px !important;
        text-shadow: 0 1px 1px rgba(0,0,0,0.2);
    }}

    /* Tab Hover Effect */
    .stTabs [data-baseweb="tab"]:hover {{
        transform: translateY(-2px);
        box-shadow: 
            0 6px 16px rgba(255, 126, 95, 0.3),
            0 3px 8px rgba(0,0,0,0.15) !important;
        background: linear-gradient(
            135deg, 
            #FF8E6F,  /* Brighter coral */
            #FEC48B   /* Brighter peach */
        ) !important;
    }}

    /* Active Tab */
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(
            135deg, 
            var(--tab-active-gradient-start), 
            var(--tab-active-gradient-end)
        ) !important;
        box-shadow: 
            0 4px 12px rgba(108, 99, 255, 0.3),
            inset 0 1px 0 rgba(255,255,255,0.2) !important;
        transform: translateY(-1px);
    }}

    /* Active Tab Hover */
    .stTabs [aria-selected="true"]:hover {{
        background: linear-gradient(
            135deg, 
            #7B72FF, 
            #5A9CFF
        ) !important;
    }}

    /* ===== GLASS EFFECTS FOR OTHER ELEMENTS =====      .stTabs [role="tabpanel"], */
    
    .stContainer, 
    .stAlert, 
    .stDataFrame {{
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(12px);
        border-radius: 16px;
        border: var(--glass-border);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}

    /* Input Fields */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select {{
        background: rgba(255,255,255,0.1) !important;
        border: var(--glass-border) !important;
        backdrop-filter: blur(8px);
    }}
    </style>
    """, unsafe_allow_html=True)
    
# Database Connection - Updated for Neon Postgres
def get_connection():
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

def initialize_database():
    try:
        connection = get_connection()
        if not connection:
            return False
            
        cursor = connection.cursor()
        
        # Check if tables exist, if not create them
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Crops (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                season VARCHAR(50),
                yield_per_acre DECIMAL(10,2),
                added_by INTEGER,
                FOREIGN KEY (added_by) REFERENCES Users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        return True
        
    except psycopg2.Error as err:
        st.error(f"Database initialization error: {err}")
        return False


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

        connection = get_connection()
        if not connection:
            return False
            
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM Users WHERE username = %s", (username,))
        if cursor.fetchone():
            if st.session_state.get("language") == "اردو":
                st.error("صارف کا نام پہلے سے موجود ہے")
            else:
                st.error("Username already exists")
            cursor.close()
            connection.close()
            return False

        cursor.execute("INSERT INTO Users (username, password) VALUES (%s, %s) RETURNING id", (username, password))
        user_id = cursor.fetchone()[0]
        connection.commit()
        
        if st.session_state.get("language") == "اردو":
            st.success("کھاتہ کامیابی سے بن گیا ہے! لاگ ان کرنے کے لیے تیار ہے۔")
        else:
            st.success("Account created successfully! Ready to login.")
            
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
        connection = get_connection()
        if not connection:
            return None
            
        cursor = connection.cursor(cursor_factory=DictCursor)
        cursor.execute("SELECT * FROM Users WHERE username = %s AND password = %s", (username, password))
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
        connection = get_connection()
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
        connection = get_connection()
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
        connection = get_connection()
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
        connection = get_connection()
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
        connection = get_connection()
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

def add_crops_bulk(data):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        if not connection:
            return False
            
        cursor = connection.cursor()
        cursor.executemany(
            "INSERT INTO Crops (name, season, yield_per_acre, added_by) VALUES (%s, %s, %s, %s)", 
            data
        )
        connection.commit()
        
        if st.session_state.get("language") == "اردو":
            st.success("متعدد فصلیں کامیابی سے شامل کر دی گئیں")
        else:
            st.success("Multiple crops added successfully")
            
        return True
        
    except psycopg2.Error as err:
        st.error(f"Database error: {err}")
        return False
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
        st.header("Analytics Dashboard")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Filter by Season")
            season = st.selectbox("", ["All", "Rabi", "Kharif"], key="season_filter_en")
        with col2:
            st.subheader("Filter by Crop Name")
            crop_name = st.selectbox("", ["All"] + list(df['Name'].unique()), key="crop_filter_en")

        if season != "All":
            df = df[df["Season"] == season]
        if crop_name != "All":
            df = df[df["Name"] == crop_name]

        st.subheader("Key Metrics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div style="
                background: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.2);
            ">
                <p style="color: white; font-size: 1rem; margin: 0;">Total Crops</p>
                <p style="color: white; font-size: 1.8rem; font-weight: bold; margin: 0;">{}</p>
            </div>
            """.format(len(df)), unsafe_allow_html=True)
    
        with col2:
            st.markdown("""
            <div style="
                background: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.2);
            ">
                <p style="color: white; font-size: 1rem; margin: 0;">Average Yield</p>
                <p style="color: white; font-size: 1.8rem; font-weight: bold; margin: 0;">{:.2f}</p>
            </div>
            """.format(df['Yield (kg/acre)'].mean()), unsafe_allow_html=True)
    
        with col3:
            st.markdown("""
            <div style="
                background: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.2);
            ">
                <p style="color: white; font-size: 1rem; margin: 0;">Total Yield</p>
                <p style="color: white; font-size: 1.8rem; font-weight: bold; margin: 0;">{:.2f}</p>
            </div>
            """.format(df['Yield (kg/acre)'].sum()), unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Bar Chart", "Pie Chart"])
        
        with tab1:
            # Bar Chart with Irrigation App Styling
            fig = px.bar(
                df, 
                x='Name', 
                y='Yield (kg/acre)',
                title="Yield per Acre",
                color='Season',
                color_discrete_sequence=["#A3B9C5", "#C3764D", "#ADDAB0", '#FFD700']  # Same colors as irrigation app
            )
            
            # Update layout to match irrigation app
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0.4)',  # Dark green background
                paper_bgcolor='rgba(0,80,32,0.8)',
                font=dict(color="white", family="Arial"),
                title_font=dict(size=18, color="#FFD700"),  # Gold title
                
                # X-axis customization
                xaxis=dict(
                    title=dict(text="Crop Name", font=dict(color="white")),
                    tickfont=dict(color="white"),
                    gridcolor='rgba(255,255,255,0.2)',
                    linecolor='rgba(255,215,0,0.5)',
                    showgrid=True
                ),
                
                # Y-axis customization
                yaxis=dict(
                    title=dict(text="Yield (kg/acre)", font=dict(color="white")),
                    tickfont=dict(color="white"),
                    gridcolor='rgba(255,255,255,0.2)',
                    linecolor='rgba(255,215,0,0.5)',
                    showgrid=True
                ),
                
                # Legend customization
                legend=dict(
                    title=dict(text="Season", font=dict(color="#FFD700")),
                    font=dict(color="white"),
                    bgcolor='rgba(0,100,40,0.7)',
                    bordercolor='rgba(255,215,0,0.3)',
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5
                ),
                
                margin=dict(l=20, r=20, t=60, b=20)
            )
            
            # Line styling
            fig.update_traces(
                marker=dict(line=dict(width=1, color='white')),
                opacity=0.8
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            # Pie Chart with Irrigation App Styling
            fig2 = px.pie(
                df,
                names='Season',
                values='Yield (kg/acre)',
                title="Seasonal Distribution",
                color_discrete_sequence=["#A3B9C5", "#C3764D", "#ADDAB0", '#FFD700'] ,
                hole=0.3  # Donut style
            )
            
            # Update layout to match irrigation app
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0.4)',
                paper_bgcolor='rgba(0,0,0,0.4)',
                font=dict(color="white"),
                title_font=dict(size=18, color="#FFD700"),
                
                # Legend customization
                legend=dict(
                    font=dict(color="white"),
                    bgcolor='rgba(0,100,40,0.7)',
                    bordercolor='rgba(255,215,0,0.3)',
                    orientation="v",
                    yanchor="middle",
                    xanchor="right",
                    x=1.2
                )
            )
            
            # Labels and text styling
            fig2.update_traces(
                textfont=dict(color='white', size=14),
                insidetextfont=dict(color='white', size=12),
                textposition='inside',
                marker=dict(line=dict(color='white', width=1)),
                hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>"
            )
            
            st.plotly_chart(fig2, use_container_width=True)

def display_dashboard_urdu():
    df = get_analytics_data_urdu()
    
    with st.container():
        st.markdown('<h2 class="urdu-text">تجزئیاتی ڈیش بورڈ</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<p class="urdu-text">موسم کے اعتبار سے فلٹر کریں</p>', unsafe_allow_html=True)
            season = st.selectbox("", ["تمام", "ربی", "خریف"], key="season_filter_urdu")
        with col2:
            st.markdown('<p class="urdu-text">فصل کے اعتبار سے فلٹر کریں</p>', unsafe_allow_html=True)
            crop_name = st.selectbox("", ["تمام"] + list(df['نام'].unique()), key="crop_filter_urdu")

        if season != "تمام":
            df = df[df["موسم"] == season]
        if crop_name != "تمام":
            df = df[df["نام"] == crop_name]

        st.markdown('<h3 class="urdu-text">اہم اعداد و شمار</h3>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div style="
                background: rgba(0, 80, 32, 0.7);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.2);
            ">
                <p style="color: white; font-size: 1rem; margin: 0;">کل فصلیں</p>
                <p style="color: white; font-size: 1.8rem; font-weight: bold; margin: 0;">{}</p>
            </div>
            """.format(len(df)), unsafe_allow_html=True)
    
        with col2:
            st.markdown("""
            <div style="
                background: rgba(0, 80, 32, 0.7);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.2);
            ">
                <p style="color: white; font-size: 1rem; margin: 0;">اوسط پیداوار</p>
                <p style="color: white; font-size: 1.8rem; font-weight: bold; margin: 0;">{:.2f}</p>
            </div>
            """.format(df['پیداوار (کلوگرام/ایکڑ)'].mean()), unsafe_allow_html=True)
    
        with col3:
            st.markdown("""
            <div style="
                background: rgba(0, 80, 32, 0.7);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.2);
            ">
                <p style="color: white; font-size: 1rem; margin: 0;">کل پیداوار</p>
                <p style="color: white; font-size: 1.8rem; font-weight: bold; margin: 0;">{:.2f}</p>
            </div>
            """.format(df['پیداوار (کلوگرام/ایکڑ)'].sum()), unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["بار چارٹ", "پائی چارٹ"])
        
        with tab1:
            # Bar Chart with Irrigation App Styling (Urdu)
            fig = px.bar(
                df, 
                x='نام', 
                y='پیداوار (کلوگرام/ایکڑ)',
                title="فی ایکڑ پیداوار",
                color='موسم',
                color_discrete_sequence=["#F3C56A", "#3EC3CF", "#9E5497", '#FFD700']
            )
            
            # Update layout to match irrigation app
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0.4)',
                paper_bgcolor='rgba(0,0,0,0.4)',
                font=dict(color="white", family="Arial"),
                title_font=dict(size=18, color="#FFD700"),
                
                xaxis=dict(
                    title=dict(text="فصل کا نام", font=dict(color="white")),
                    tickfont=dict(color="white"),
                    gridcolor='rgba(255,255,255,0.2)',
                    linecolor='rgba(255,215,0,0.5)',
                    showgrid=True
                ),
                
                yaxis=dict(
                    title=dict(text="پیداوار (کلوگرام/ایکڑ)", font=dict(color="white")),
                    tickfont=dict(color="white"),
                    gridcolor='rgba(255,255,255,0.2)',
                    linecolor='rgba(255,215,0,0.5)',
                    showgrid=True
                ),
                
                legend=dict(
                    title=dict(text="موسم", font=dict(color="#FFD700")),
                    font=dict(color="white"),
                    bgcolor='rgba(0,100,40,0.7)',
                    bordercolor='rgba(255,215,0,0.3)',
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5
                ),
                
                margin=dict(l=20, r=20, t=60, b=20)
            )
            
            fig.update_traces(
                marker=dict(line=dict(width=1, color='white')),
                opacity=0.8
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            # Pie Chart with Irrigation App Styling (Urdu)
            fig2 = px.pie(
                df,
                names='موسم',
                values='پیداوار (کلوگرام/ایکڑ)',
                title="موسم کے لحاظ سے تقسیم",
                color_discrete_sequence=["#F3C56A", "#4A67D2", "#9E5497", '#FFD700'],
                hole=0.3
            )
            
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0.4)',
                paper_bgcolor='rgba(0,0,0,0.3)',
                font=dict(color="white"),
                title_font=dict(size=18, color="#FFD700"),
                
                legend=dict(
                    font=dict(color="white"),
                    bgcolor='rgba(0,100,40,0.7)',
                    bordercolor='rgba(255,215,0,0.3)',
                    orientation="v",
                    yanchor="middle",
                    xanchor="right",
                    x=1.2
                )
            )
            
            fig2.update_traces(
                textfont=dict(color='white', size=14),
                insidetextfont=dict(color='white', size=12),
                textposition='inside',
                marker=dict(line=dict(color='white', width=1)),
                hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>"
            )
            
            st.plotly_chart(fig2, use_container_width=True)
            
            
def display_crop_management_urdu():
    with st.container():
        st.markdown('<h2 class="urdu-text">فصلوں کا انتظام</h2>', unsafe_allow_html=True)
        
        action = st.selectbox(
            "عمل منتخب کریں",
            ["شامل کریں", "متعدد شامل کریں", "دیکھیں", "حذف کریں", "تلاش کریں", "اپ ڈیٹ کریں"],
            key="crop_action_urdu"
        )
        
        if action == "شامل کریں":
            with st.form("add_crop_form_urdu"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("فصل کا نام")
                with col2:
                    season = st.text_input("موسم (مثال: ربی، خریف)")
                yield_per_acre = st.number_input("پیداوار فی ایکڑ (کلوگرام)", min_value=0.0, step=0.1)
                
                if st.form_submit_button("فصل شامل کریں"):
                    if add_crop(name, season, yield_per_acre):
                        st.success(f"{name} کامیابی سے شامل ہو گئی!")
        
        elif action == "متعدد شامل کریں":
            st.markdown('<p class="urdu-text">فصلیں درج کریں (ہر لائن پر ایک فصل):<br>فارمیٹ: نام، موسم، پیداوار</p>', unsafe_allow_html=True)
            crops_input = st.text_area("", value="گندم، ربی، 3000\nچاول، خریف، 3500")
            
            if st.button("متعدد فصلیں شامل کریں"):
                try:
                    data = []
                    for line in crops_input.split("\n"):
                        if line.strip():
                            parts = [x.strip() for x in line.split("،")]
                            if len(parts) == 3:
                                data.append((parts[0], parts[1], float(parts[2]), st.session_state.user_id))
                    if add_crops_bulk(data):
                        st.success(f"{len(data)} فصلیں کامیابی سے شامل ہو گئیں!")
                except Exception as e:
                    st.error(f"خرابی: {str(e)}")
        
        elif action == "دیکھیں":
            crops = get_crops()
            if crops:
                df = pd.DataFrame(crops, columns=["شناخت", "نام", "موسم", "پیداوار (کلوگرام/ایکڑ)"])
                st.dataframe(df)
            else:
                st.warning("کوئی فصل دستیاب نہیں")
        
        elif action == "حذف کریں":
            crop_id = st.number_input("حذف کرنے کے لیے فصل کی شناخت درج کریں", min_value=1)
            if st.button("حذف کریں"):
                delete_crop(crop_id)
        
        elif action == "تلاش کریں":
            keyword = st.text_input("نام یا موسم سے تلاش کریں")
            if st.button("تلاش کریں"):
                results = search_crops(keyword)
                if results:
                    df = pd.DataFrame(results, columns=["شناخت", "نام", "موسم", "پیداوار (کلوگرام/ایکڑ)"])
                    st.dataframe(df)
                else:
                    st.warning("کوئی مماثل فصل نہیں ملی")
        
        elif action == "اپ ڈیٹ کریں":
            crop_id = st.number_input("اپ ڈیٹ کے لیے فصل کی شناخت", min_value=1)
            name = st.text_input("نیا نام (خالی چھوڑیں تو موجودہ رہے گا)")
            season = st.text_input("نیا موسم (خالی چھوڑیں تو موجودہ رہے گا)")
            yield_per_acre = st.number_input("نئی پیداوار (خالی چھوڑیں تو موجودہ رہے گی)", min_value=0.0, step=0.1)
            
            if st.button("فصل اپ ڈیٹ کریں"):
                update_crop(crop_id, name or None, season or None, yield_per_acre or None)

def display_export_english():
    with st.container():
        st.header("Export Data")
        
        crops = get_crops()
        if crops:
            # Create DataFrame with the exact columns we have
            df = pd.DataFrame(crops, columns=["id", "name", "season", "yield_per_acre"])
            # Rename columns for display
            df.columns = ["ID", "Name", "Season", "Yield (kg/acre)"]
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Current Data:")
                st.dataframe(df)
            
            with col2:
                st.subheader("Export Options:")
                
                csv = df.to_csv(index=False).encode('utf-8')
                excel_buffer = io.BytesIO()
                df.to_excel(excel_buffer, index=False)
                
                st.download_button(
                    "Download CSV",
                    data=csv,
                    file_name="crops_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                st.download_button(
                    "Download Excel",
                    data=excel_buffer,
                    file_name="crops_data.xlsx",
                    mime="application/vnd.ms-excel",
                    use_container_width=True
                )
        else:
            st.warning("No data available for export")

def display_export_urdu():
    with st.container():
        st.markdown('<h2 class="urdu-text">ڈیٹا برآمد کریں</h2>', unsafe_allow_html=True)
        
        crops = get_crops()
        if crops:
            df = pd.DataFrame(crops, columns=["id", "name", "season", "yield_per_acre"])
            df.columns = ["شناخت", "نام", "موسم", "پیداوار (کلوگرام/ایکڑ)"]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<p class="urdu-text">موجودہ ڈیٹا:</p>', unsafe_allow_html=True)
                st.dataframe(df)
            
            with col2:
                st.markdown('<p class="urdu-text">برآمد کے اختیارات:</p>', unsafe_allow_html=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                excel_buffer = io.BytesIO()
                df.to_excel(excel_buffer, index=False)
                
                st.download_button(
                    "CSV ڈاؤن لوڈ کریں",
                    data=csv,
                    file_name="فصلیں_ڈیٹا.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                st.download_button(
                    "ایکسل ڈاؤن لوڈ کریں",
                    data=excel_buffer,
                    file_name="فصلیں_ڈیٹا.xlsx",
                    mime="application/vnd.ms-excel",
                    use_container_width=True
                )
        else:
            st.warning("برآمد کے لیے کوئی ڈیٹا دستیاب نہیں")
            
            
def display_crop_management_english():
    with st.container():
        st.header("Crop Management")
        
        action = st.selectbox(
            "Select Action",
            ["Add", "Add Multiple", "View", "Delete", "Search", "Update"],
            key="crop_action_en"
        )
        
        if action == "Add":
            with st.form("add_crop_form_en"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Crop Name")
                with col2:
                    season = st.text_input("Season (e.g., Rabi, Kharif)")
                yield_per_acre = st.number_input("Yield per Acre (kg)", min_value=0.0, step=0.1)
                
                if st.form_submit_button("Add Crop"):
                    if add_crop(name, season, yield_per_acre):
                        st.success(f"{name} added successfully!")
        
        elif action == "Add Multiple":
            st.markdown("Enter crops (one per line):<br>Format: name, season, yield", unsafe_allow_html=True)
            crops_input = st.text_area("", value="Wheat, Rabi, 3000\nRice, Kharif, 3500")
            
            if st.button("Add Multiple Crops"):
                try:
                    data = []
                    for line in crops_input.split("\n"):
                        if line.strip():
                            parts = [x.strip() for x in line.split(",")]
                            if len(parts) == 3:
                                data.append((parts[0], parts[1], float(parts[2]), st.session_state.user_id))
                    if add_crops_bulk(data):
                        st.success(f"{len(data)} crops added successfully!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        elif action == "View":
            crops = get_crops()
            if crops:
                df = pd.DataFrame(crops, columns=["ID", "Name", "Season", "Yield (kg/acre)"])
                st.dataframe(df)
            else:
                st.warning("No crops available")
        
        elif action == "Delete":
            crop_id = st.number_input("Enter Crop ID to Delete", min_value=1)
            if st.button("Delete"):
                delete_crop(crop_id)
        
        elif action == "Search":
            keyword = st.text_input("Search by name or season")
            if st.button("Search"):
                results = search_crops(keyword)
                if results:
                    df = pd.DataFrame(results, columns=["ID", "Name", "Season", "Yield (kg/acre)"])
                    st.dataframe(df)
                else:
                    st.warning("No matching crops found")
        
        elif action == "Update":
            crop_id = st.number_input("Crop ID to Update", min_value=1)
            name = st.text_input("New Name (leave blank to keep current)")
            season = st.text_input("New Season (leave blank to keep current)")
            yield_per_acre = st.number_input("New Yield (leave blank to keep current)", min_value=0.0, step=0.1)
            
            if st.button("Update Crop"):
                update_crop(crop_id, name or None, season or None, yield_per_acre or None)


            
def main():
    set_premium_ui()
    set_background_and_styles("ap9.jpg")
    
    
    # Initialize session state
    if 'logged_in_user' not in st.session_state:
        st.session_state.logged_in_user = None
    if 'language' not in st.session_state:
        st.session_state.language = "English"
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

    # Initialize database
    if not initialize_database():
        st.error("Failed to initialize database. Some features may not work.")
        return

    # Language selection in sidebar
    with st.sidebar:
        st.session_state.language = st.radio(
            "Language / زبان", 
            ["English", "اردو"],
            key="lang_select"
        )
        
        if st.session_state.logged_in_user:
            st.markdown(f"### {st.session_state.logged_in_user['username']}")
            if st.button("Logout / لاگ آؤٹ"):
                st.session_state.logged_in_user = None
                st.rerun()

    # Main App Logic
    if st.session_state.language == "English":
        if not st.session_state.logged_in_user:
            auth_tab, reg_tab = st.tabs(["Login", "Register"])
            
            with auth_tab:
                with st.form("login_form"):
                    st.header("Login")
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    if st.form_submit_button("Login"):
                        user = login_user(username, password)
                        if user:
                            st.rerun()
                            
            with reg_tab:
                with st.form("register_form"):
                    st.header("Register")
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    if st.form_submit_button("Register"):
                        if register_user(username, password):
                            st.rerun()
        else:
            tab1, tab2, tab3 = st.tabs(["Crop Management", "Dashboard", "Export Data"])

            with tab1:
                
                display_crop_management_english()
                set_background_and_styles("farm58.jpg")

            with tab2:
                display_dashboard_english()
                set_background_and_styles("dash2.jpg")

            with tab3:
                display_export_english()
                set_background_and_styles("export1.jpg")
                
    elif st.session_state.language == "اردو":
        if not st.session_state.logged_in_user:
            auth_tab, reg_tab = st.tabs(["لاگ ان", "رجسٹر"])
            
            with auth_tab:
                with st.form("login_form_urdu"):
                    st.markdown('<h2 class="urdu-text">لاگ ان</h2>', unsafe_allow_html=True)
                    username = st.text_input("صارف نام")
                    password = st.text_input("پاس ورڈ", type="password")
                    if st.form_submit_button("لاگ ان کریں"):
                        user = login_user(username, password)
                        if user:
                            st.rerun()
                            
            with reg_tab:
                with st.form("register_form_urdu"):
                    st.markdown('<h2 class="urdu-text">رجسٹر</h2>', unsafe_allow_html=True)
                    username = st.text_input("صارف نام")
                    password = st.text_input("پاس ورڈ", type="password")
                    if st.form_submit_button("رجسٹر کریں"):
                        if register_user(username, password):
                            st.rerun()
        else:
            tab1, tab2, tab3 = st.tabs(["فصلوں کا انتظام", "ڈیش بورڈ", "ڈیٹا برآمد"])
            
            with tab1:
                display_crop_management_urdu()
                set_background_and_styles("farm58.jpg")
                
            with tab2:
                display_dashboard_urdu()
                set_background_and_styles("dash2.jpg")
                
                
            with tab3:
                display_export_urdu()
                set_background_and_styles("export1.jpg")

if __name__ == "__main__":
    main()
