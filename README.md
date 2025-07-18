# 🌱 Prosperous Farmer ' An Agricultural Management System '


A bilingual agricultural management web app built using Streamlit and PostgreSQL, designed to support farmers in managing crop records, analyzing yields and exporting data with ease. It Supports both English and Urdu interfaces.


##  Table of Contents
- Features
- 🧑‍🌾 Use Case
- 🛠 Tech Stack
- 🗃 Database Design
- ⚙️ Installation Guide
- 🔁 App Flow
- 🔐 Security & Environment
- 🤝 Contribution Guidelines


## 🚀 Features

### 🌐 Bilingual Support
- Toggle between English and Urdu interfaces
- UI is designed with local cultural considerations

### 📋 Crop Management

| Feature         | Description                           |
|-----------------|---------------------------------------|
| Crop CRUD       | Add, view, edit, delete crops         |
| Bulk Import     | ADd multiple crops                    |
| Smart Search    | Filter by crop name or season         |
| Data Export     | Download as CSV or Excel              |

### 📈 Data Analytics
- Interactive visualizations (bar/pie charts)
- Season based performance tracking
- Responsive dashboard using Plotly

---

## 🧑‍🌾 Use Case

A farmer can:
1. Log in or register on the platform  
2. Add new crop records (name, season, yield)  
3. Track performance over time via charts  
4. Export data for offline use or reporting

---

## 🛠 Tech Stack

**Frontend:**
- Streamlit (UI)
- Plotly Express (Charts)
- Custom CSS (enhanced styling)

**Backend:**
- PostgreSQL (Database)
- Neon.tech (Cloud DB hosting)
- Psycopg2 (Python PostgreSQL adapter)

**Data Layer:**
- Pandas (data handling)
- Base64 (image processing)

---


## Installation Guide

**Requirements:**
- Python 3.8 or higher
- PostgreSQL 14 or higher
- Git

**Steps:**
1. Clone the repository:  
   `git clone https://github.com/yourusername/prosperous-farmer.git`  

2. Navigate into the folder:  
   `cd prosperous-farmer`  

3. Install Python libraries:  
   `pip install -r requirements.txt`

4. Create a `.env` file and add:
   - DB_USER = your_db_user  
   - DB_PASSWORD = your_password  
   - DB_HOST = your_host_url  
   - DB_NAME = your_database_name

5. Run the app:  
   `streamlit run main.py`

---

## 🔁 App Flow

- Landing Page → Login/Register  
- If logged in → Dashboard  
- Dashboard options:  
  - Crop Management  
  - Data Analytics  
  - Export Data

---

## 🔐 Security & Environment

**Current State:**
- Passwords stored with basic validation
- Database credentials hardcoded (needs improvement)

**Suggested Fix:**
- Move all sensitive data to a `.env` file  
- Use `python-dotenv` to load environment variables in code

---



## Future Improvements

- Add Admin Dashboard  
- Implement role-based login  
- Add SMS alerts for harvest season  and much more
