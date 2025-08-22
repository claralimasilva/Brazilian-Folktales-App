# 🎮 Demo - Demonstration and Utility Scripts

This folder contains demonstration scripts and utilities for the Folktale Reader project.

## 📁 **Contents**

### **👥 User Management**
- `create_demo_users.py` - Create demonstration users with varied achievement levels
- `add_carol.py` - Add specific user with predefined achievements

### **🏆 Achievement Management**
- `create_demo_achievements.py` - Initialize all 24 achievements in the database
- `manual_achievements.py` - Manually award achievements to users for testing
- `list_achievements.py` - Display all available achievements and their details

### **📊 Ranking and Display**
- `show_ranking.py` - Display current global and category rankings

## 🚀 **How to Use Demo Scripts**

### **Initial Setup**
```bash
# 1. Create all achievements in database
python demo/create_demo_achievements.py

# 2. Create demo users
python demo/create_demo_users.py

# 3. Award some achievements manually
python demo/manual_achievements.py
```

### **View Results**
```bash
# Show current rankings
python demo/show_ranking.py

# List all achievements
python demo/list_achievements.py
```

### **Add More Users**
```bash
# Add specific users
python demo/add_carol.py
```

## 🎯 **Demo Users Created**

### **Current Demo Users**
- **alice**: Beginner user with reading achievements
- **bob**: Advanced user with quiz mastery
- **carol**: Well-rounded user with multiple achievements
- **demo**: Basic user with one achievement
- **david**: New user with first achievement

### **Achievement Distribution**
- Total points range: 50-350 points
- Achievement count: 1-4 achievements per user
- Categories covered: Reading, Quiz, Discovery, Milestone

## 📊 **Current Ranking Status**

```
#1 - bob: 350 pts (2 achievements)
#2 - carol: 300 pts (4 achievements)
#3 - alice: 200 pts (3 achievements)
#4 - demo: 100 pts (1 achievement)
#5 - david: 50 pts (1 achievement)
```

## 🔧 **Script Features**

### **Safe Execution**
- All scripts check for existing data before creating
- No duplicate achievements or users
- Graceful error handling
- Informative output messages

### **Customizable**
- Easy to modify user data
- Adjustable achievement awards
- Flexible point values
- Expandable user base

## 🛠️ **Development Usage**

### **Testing New Features**
```bash
# Reset and recreate demo data
python demo/create_demo_users.py
python demo/manual_achievements.py

# Test ranking calculations
python demo/show_ranking.py
```

### **Performance Testing**
- Create multiple users for load testing
- Award many achievements for ranking stress tests
- Validate database performance with demo data

## 📋 **Maintenance**

- Scripts are updated with code changes
- Demo data reflects current achievement system
- Regular validation of script functionality
- Documentation kept in sync with features
