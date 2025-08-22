# 🧪 Tests - Testing and Debugging

This folder contains test files and debugging utilities for the Folktale Reader project.

## 📁 **Contents**

### **🔬 Test Files**
- `test_database.py` - Database operations testing
- `test_achievements.py` - Achievement system testing
- `test_ranking.py` - Ranking system testing

### **🛠️ Debug Utilities**
- `debug_database.py` - Database debugging and inspection
- Various utility scripts for system validation

## 🎯 **Testing Strategy**

### **Database Testing**
- Connection and schema validation
- CRUD operations testing
- Data integrity checks
- Performance testing

### **Achievement Testing**
- Achievement unlock mechanics
- Point calculation validation
- Category system testing
- Edge case handling

### **Ranking Testing**
- Global ranking calculations
- Category ranking accuracy
- User position tracking
- Real-time update testing

## 🚀 **How to Run Tests**

### **Individual Test Files**
```bash
# Test database operations
python tests/test_database.py

# Test achievement system
python tests/test_achievements.py

# Test ranking system
python tests/test_ranking.py
```

### **Debug Database**
```bash
# Inspect database contents
python tests/debug_database.py
```

### **All Tests**
```bash
# Run all tests (if pytest is installed)
pytest tests/

# Or run manually
python -m unittest discover tests/
```

## 🔧 **Debugging Tools**

### **Database Inspector**
- View all tables and data
- Check data integrity
- Validate relationships
- Monitor performance

### **Achievement Debugger**
- Test achievement unlocking
- Validate point calculations
- Check category assignments
- Debug edge cases

### **Ranking Validator**
- Verify ranking calculations
- Test sorting algorithms
- Validate user positions
- Check for ties and edge cases

## 📊 **Test Coverage**

### **✅ Covered Areas**
- ✅ Database connectivity and operations
- ✅ User authentication and management
- ✅ Achievement system mechanics
- ✅ Ranking calculations and sorting
- ✅ Data validation and integrity

### **🎯 Test Results**
- All core functionality tested
- Edge cases identified and handled
- Performance benchmarks established
- Security validations in place

## 🛡️ **Testing Best Practices**

- Tests run with isolated test data
- No impact on production database
- Automated validation of core features
- Regular regression testing
- Documentation of test procedures
