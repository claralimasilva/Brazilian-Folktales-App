# Folktale Reader - Security Configuration

## Environment Variables (Required for Production)

Create a `.env` file (NOT included in Git) with:

```bash
SECRET_KEY=your-super-secret-key-here-min-32-chars
FLASK_ENV=production
DATABASE_URL=sqlite:///data/folktale_users.db
```

## Security Checklist

### ✅ Database Security
- Database files moved to `data/` folder
- No sensitive data in database schema
- Proper password hashing (werkzeug)

### ✅ Flask Security
- Secret key from environment variable
- Debug mode disabled in production
- Secure session configuration

### ✅ File Security
- `.gitignore` includes sensitive files
- No hardcoded secrets in code
- Proper file permissions

### ✅ GitHub Security
- No database files in repository
- No environment variables committed
- No API keys or secrets in code

## Deployment Security

### Environment Setup
```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export FLASK_ENV=production
```

### File Permissions (Linux/Mac)
```bash
chmod 600 data/*.db  # Database files
chmod 644 config/*.py  # Config files
chmod 755 app.py  # Main application
```

## Security Features Implemented

1. **Authentication**: Secure password hashing
2. **Session Management**: Secure session configuration
3. **Input Validation**: SQL injection prevention
4. **File Access**: Restricted to application directories
5. **Environment Separation**: Dev/prod configurations
