# 💾 Data - Application Data

This folder contains the application's runtime data and database files.

## 📁 **Contents**

### **Database**
- `folktale_users.db` - Main SQLite database
  - User, achievement, and ranking tables
  - Progress and activity data
  - **🚨 NEVER committed to Git** (security)

### **JSON Data**
- `stories_data.json` - Processed story data
  - Automatically generated from DOCX
  - Web-optimized structure
  - Contains conversion metadata

## 🔒 **Security**

### **Protected Files**
- `*.db` - Databases **NEVER** go to Git
- Contains sensitive user data
- Passwords securely hashed

### **In .gitignore**
```
data/*.db
data/*.sqlite
data/*.sqlite3
```

## 🛠️ **Management**

### **Database Backup**
```bash
# Create backup
cp data/folktale_users.db backup/folktale_backup_$(date +%Y%m%d).db

# Restore backup
cp backup/folktale_backup_20250821.db data/folktale_users.db
```

### **Recreate Database**
```bash
# Delete existing database
rm data/folktale_users.db

# Run app - database will be recreated automatically
python app.py
```

### **Demo Data**
```bash
# Create demonstration data
python demo/create_demo_users.py
python demo/manual_achievements.py
```

## 📊 **Current Status**

### **Database**
- ✅ 5 active demo users
- ✅ 24 implemented achievements
- ✅ Functional ranking system
- ✅ Active activity logs

### **Stories Data**
- ✅ Updated and optimized JSON
- ✅ Conversion metadata included
- ✅ Structure version 2.0
