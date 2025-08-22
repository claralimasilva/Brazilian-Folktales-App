# ⚙️ Config - System Configuration

This folder contains all configuration and security settings for the application.

## 📁 **Contents**

### **Configuration Files**
- `settings.py` - Flask settings and system paths
- `SECURITY.md` - Complete security guide
- `__init__.py` - Package initialization

## 🔧 **Available Configurations**

### **Environments**
- **Development**: Debug active, flexible settings
- **Production**: Maximum security, active optimizations

### **Environment Variables**
```bash
# Development
FLASK_ENV=development
FLASK_DEBUG=true

# Production (REQUIRED)
SECRET_KEY=your-super-secret-key-min-32-chars
FLASK_ENV=production
```

## 🔒 **Implemented Security**

### **Security Features**
- ✅ Mandatory secret key in production
- ✅ Environment-separated configurations
- ✅ Secure file paths
- ✅ Configuration validation

### **Production Checklist**
- [ ] `SECRET_KEY` defined via environment variable
- [ ] `FLASK_ENV=production`
- [ ] Debug disabled
- [ ] Database in protected folder
- [ ] `.env` not committed

## 📖 **How to Use**

### **Local Development**
```python
# Automatic usage - default configuration
from config.settings import config
app.config.from_object(config['development'])
```

### **Production**
```bash
# Define mandatory variables
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export FLASK_ENV=production

# Run application
python app.py
```

### **Docker/Deploy**
```dockerfile
ENV SECRET_KEY=your-production-secret-key
ENV FLASK_ENV=production
ENV DATABASE_URL=sqlite:///data/folktale_users.db
```

## 🛡️ **Configuration Validation**

The system automatically validates:
- Presence of SECRET_KEY in production
- Appropriate security settings
- Valid file paths
- Adequate permissions
