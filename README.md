# 🌱 Prosperous Farmer | Data-Driven Agri-Analytics & Smart Irrigation with Bilingual(Urdu/Eng) Support

A comprehensive bilingual agricultural management web application built using Streamlit and PostgreSQL, designed to help farmers with smart irrigation control, crop management, yield analytics, water conservation tips, and data export functionality. Supports both English and Urdu interfaces.

## 📌 Table of Contents
- Features
- 🧑‍🌾 Use Case
- 🛠 Tech Stack
- 🗃 Database Design
- ⚙️ Installation Guide
- 🔁 App Flow
- 🔐 Security & Environment

## 🚀 Features

### 🌐 Bilingual Support
- Toggle between English and Urdu interfaces throughout the application
- All UI elements, buttons, labels, and messages support both languages

### 💧 Smart Irrigation Control
- Real-time soil moisture monitoring (0-100%)
- Crop-specific and soil-type specific moisture thresholds
- Visual progress bar during irrigation
- Start/Stop/Reset irrigation functionality
- Prevents duplicate irrigation of same crop-soil combination

### 💡 Water Saving Tips
- Crop and soil specific water conservation recommendations
- Supports 6 crops: Wheat, Cotton, Rice, Sugarcane, Maize, Grams
- Supports 4 soil types: Clay, Silt, Sand, Loam
- Expected water savings of 30-50% with implementation tips

### 📋 Crop Management
| Feature | Description |
|---------|-------------|
| Crop CRUD | Add, view, delete, update, and search crops |
| Smart Search | Filter crops by name or season |
| Crop Fields | Name, Season (Rabi/Kharif), Yield per acre (kg) |

### 📈 Analytics Dashboard
- Interactive bar charts and pie charts using Plotly
- Season-based filtering (Rabi/Kharif)
- Crop name filtering
- Key metrics: Total crops, Average yield, Total yield

### 📊 Irrigation History
- Complete history of all irrigation events
- Tracks: crop type, soil type, moisture level, timestamp
- Line chart showing moisture level trends over time
- Pie chart showing irrigation distribution by crop type

### 📥 Data Export
- Export irrigation history as CSV or Excel
- Export crops data as CSV or Excel
- Separate tabs for Irrigation Data and Crops Data

### 🎨 Custom UI Styling
- Neon gradient animated borders on tabs
- Custom button animations with gradient backgrounds
- Background images for each tab
- Semi-transparent cards with shadow effects
- Responsive dashboard cards with hover effects

## 🧑‍🌾 Use Case

A farmer can:
1. Register or login to the platform
2. Select crop type and soil type for irrigation advice
3. Start automated irrigation with visual progress tracking
4. Get water saving tips specific to their crop and soil
5. Add, view, update, or delete crop records
6. Track crop performance through interactive charts
7. View complete irrigation history with visual trends
8. Export all data (crops and irrigation) for offline use

## 🛠 Tech Stack

**Frontend:**
- Streamlit (UI framework)
- Plotly Express (Interactive charts)
- Custom CSS (Neon animations, gradients, responsive design)

**Backend:**
- PostgreSQL (Database)
- Neon.tech (Cloud PostgreSQL hosting)
- Psycopg2 (Python database adapter)

**Data Layer:**
- Pandas (Data manipulation)
- NumPy (Numerical operations)
- Base64 (Image encoding for backgrounds)
- IO (Excel file handling with openpyxl)

## 🗃 Database Design

### Users Table
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique user identifier |
| username | VARCHAR(50) UNIQUE | User's login name |
| password | VARCHAR(50) | User's password |

### irrigation_history Table
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique record identifier |
| username | VARCHAR(50) | User who performed irrigation |
| crop_type | VARCHAR(50) | Type of crop (Wheat, Cotton, etc.) |
| soil_type | VARCHAR(50) | Type of soil (Clay, Silt, Sand, Loam) |
| moisture_level | INT | Soil moisture percentage at irrigation |
| timestamp | TIMESTAMP | Date and time of irrigation |

### Crops Table
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique crop identifier |
| name | VARCHAR(255) | Name of the crop |
| season | VARCHAR(50) | Growing season (Rabi/Kharif) |
| yield_per_acre | DECIMAL(10,2) | Yield in kg per acre |
| added_by | INTEGER | Foreign key referencing users.id |
| created_at | TIMESTAMP | Record creation timestamp |

## ⚙️ Installation Guide

**Requirements:**
- Python 3.8 or higher
- PostgreSQL 14 or higher (or Neon.tech account)
- Git

**Steps:**

1. Clone the repository:
```bash
git clone https://github.com/yourusername/prosperous-farmer.git
cd prosperous-farmer

2. Install required Python packages:
```bash
pip install streamlit psycopg2-binary pandas numpy plotly openpyxl
```

3. Set up PostgreSQL database (using Neon.tech or local):
   - Create a new PostgreSQL database
   - Update database credentials in the `connect_db()` function

4. Database credentials (currently hardcoded - update these):
```python
host="ep-falling-pond-addqml8d-pooler.c-2.us-east-1.aws.neon.tech"
database="neondb"
user="neondb_owner"
password="npg_emHPU1b7qSOL"
port="5432"
```

5. Place background images in the project directory:
   - w12.jpg (login background)
   - w17.jpg (irrigation background)
   - w19.jpg (tips background)
   - pc1.jpg (history background)
   - farm58.jpg (crop management background)
   - dash2.jpg (dashboard and export backgrounds)

6. Run the application:
```bash
streamlit run app.py
```

## 🔁 App Flow

1. **Landing Page** → Login / Signup with language selection
2. **After Login** → Sidebar navigation with 6 tabs:
   - **Irrigation**: Soil moisture monitoring and irrigation control
   - **Water Saving Tips**: Crop and soil specific recommendations
   - **Crop Management**: Add, view, delete, search, update crops
   - **Dashboard**: Analytics with charts and filters
   - **Export Data**: Download irrigation and crops data
   - **Irrigation History**: View history with visual trends
3. **Logout** → Returns to login page

## 🔐 Security & Environment

**Current State:**
- Basic password validation (minimum 6 characters, not entirely numeric)
- Username validation (alphanumeric only, not empty)
- Database credentials hardcoded in the application

**Recommended Improvements:**
- Move database credentials to `.env` file
- Use `python-dotenv` to load environment variables
- Implement password hashing (bcrypt)
- Add session timeout functionality

## 🤝 Contribution Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Notes

- The application automatically creates all required database tables on first run
- Background images are optional - app works without them
- Urdu language support uses inline text, no external translation APIs
- All charts use dark theme with yellow/gold text for better visibility

## Future Improvements

- Password hashing and better authentication
- Environment variables for database credentials
- Admin dashboard with user management
- SMS/Email alerts for low moisture levels
- Mobile-responsive design enhancements
- Bulk crop import via CSV/Excel
```
