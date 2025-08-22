# Folktale Reader - Brazilian Folktales App

> **Complete Brazilian folklore reading system with achievements and ranking**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## **About the Project**

Interactive web application for reading Brazilian folk tales with complete gamification system through achievements and rankings. Built with Flask featuring responsive interface and SQLite database.

This project was developed as part of an extension scholarship from PREX (Pro-Reitoria de Extensão da Universidade Federal do Ceará) at Casa de Cultura Britânica. Its main goal is to help users learn English through interactive reading of Brazilian folktales, using gamification and ranking systems.

## **Main Features**

### **Reading System**
- Responsive interface for reading tales
- Automatic DOCX to JSON conversion
- Story navigation system
- Audio support (Text-to-Speech)

### **Achievement System**
- **24 unique achievements** across 5 categories:
   - **Reading** (6): First reads, streaks, completions
   - **Quiz** (6): Quiz performance and mastery
   - **Discovery** (4): Content exploration
   - **Social** (4): Community interactions
   - **Milestone** (4): Progress landmarks

### **Ranking System**
- **Global Ranking**: Overall leaderboard by points
- **Category Rankings**: Specific classifications
- **Individual Positioning**: Personal tracking
- **Real-time Updates**: Dynamic interface

### **User System**
- Secure authentication with password hashing
- Personalized profiles
- Activity history
- Individual progress

## **Technologies Used**

- **Backend**: Python 3.8+ | Flask 2.0+
- **Database**: SQLite with optimized schema
- **Frontend**: HTML5 | CSS3 | JavaScript ES6+ | Bootstrap 5
- **Security**: Werkzeug password hashing | CSRF protection
- **APIs**: RESTful endpoints for all functionalities

## **Project Structure**

```
folktale-reader/
├── app.py                    # Main Flask application
├── database.py               # Database operations and ranking
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignored files
├── README.md                # This file
├── PROJECT_OVERVIEW.md      # Detailed overview
│
├── templates/               # HTML templates
│   └── index.html              # Main interface with ranking
│
├── static/                  # Static files
│   ├── css/                    # CSS styles
│   ├── js/                     # JavaScript scripts
│   └── images/                 # Images and icons
│
├── config/                  # Configurations
│   ├── settings.py             # Flask configurations
│   ├── SECURITY.md             # Security guide
│   └── __init__.py
│
├── data/                    # Application data
│   ├── stories_data.json       # Story data
│   └── folktale_users.db       # Database (not committed)
│
├── assets/                  # Source files
│   ├── BrazilianFolktales.docx # Source document
│   ├── Apresentacao*.pdf       # Presentations
│   └── *.pdf                   # Additional documentation
│
├── docs/                    # Documentation
│   ├── API_DOCUMENTATION.md    # API guide
│   ├── ACHIEVEMENT_SYSTEM.md   # Achievement system
│   ├── DATABASE_SCHEMA.md      # Database schema
│   └── USER_GUIDE.md           # User manual
│
├── tests/                   # Tests and debug
│   ├── test_database.py        # Database tests
│   ├── test_achievements.py    # Achievement tests
│   ├── test_ranking.py         # Ranking tests
│   └── debug_database.py       # Debug utilities
│
└── demo/                    # Demo scripts
    ├── create_demo_users.py    # Create demo users
    ├── manual_achievements.py  # Award achievements
    └── show_ranking.py         # Show current ranking
```

## **How to Run**

### **Prerequisites**
- Python 3.8 or higher
- pip (Python package manager)

### **Installation**

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/folktale-reader.git
   cd folktale-reader
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment** (optional for development)
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access in browser**
   ```
   http://localhost:5000
   ```

### **Creating Demo Data**

```bash
# Create demonstration users
python demo/create_demo_users.py

# Manually award achievements
python demo/manual_achievements.py

# View current ranking
python demo/show_ranking.py
```

## **Security**

### **Secure Configuration**
- ✅ Passwords hashed with Werkzeug
- ✅ Secret key via environment variable
- ✅ Sensitive files in .gitignore
- ✅ Input validation in all APIs
- ✅ Separate dev/prod configurations

### **For Production**
```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export FLASK_ENV=production
```

## **Current Status**

### **Database**
- ✅ **5 demo users** with varied achievements
- ✅ **24 achievements** implemented and functional
- ✅ **Ranking system** active and operational

### **Current Ranking**
```
#1 - bob: 350 pts (2 achievements)
#2 - carol: 300 pts (4 achievements)
#3 - alice: 200 pts (3 achievements)
#4 - demo: 100 pts (1 achievement)
#5 - david: 50 pts (1 achievement)
```

## **Available APIs**

### **Authentication**
- `POST /api/login` - User login
- `POST /api/register` - User registration
- `POST /api/logout` - Logout

### **Achievements**
- `GET /api/achievements` - List achievements
- `GET /api/user/achievements` - User achievements
- `POST /api/achievements/unlock` - Unlock achievement

### **Ranking**
- `GET /api/ranking/global` - Global ranking
- `GET /api/ranking/user/<id>` - Specific position
- `GET /api/ranking/categories` - Category rankings

### **Stories**
- `GET /api/stories` - List stories
- `GET /api/stories/<id>` - Specific story
- `POST /api/stories/progress` - Update progress

## **Contributing**

1. Fork the project
2. Create a branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request