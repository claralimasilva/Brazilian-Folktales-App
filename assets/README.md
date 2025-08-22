# 📋 Assets - Source Files and Resources

This folder contains the original source files and project resources.

## 📁 **Contents**

### **Source Documents**
- `BrazilianFolktales.docx` - Original document with folk tales
- `Apresentacao Folktale App.pdf` - Project presentation
- `Folktale-Reader-Descubra-Historias-Desbloqueie-Conhecimento.pdf` - Project documentation

### **Characteristics**
- ✅ Unprocessed source files
- ✅ Original project documentation
- ✅ Presentations and support materials
- ✅ Isolated from main code for security

## 🔄 **Data Conversion**

The `BrazilianFolktales.docx` file is automatically converted to JSON when needed:
- System automatically checks modification dates
- Conversion occurs only when DOCX is newer than JSON
- Converted data is stored in `data/stories_data.json`

## 🔒 **Security**

- Files in this folder are included in the repository
- Do not contain sensitive information
- Can be accessed publicly on GitHub

## 📖 **How to Use**

1. **Add New Tales**: Edit `BrazilianFolktales.docx`
2. **Update**: Run the application - conversion is automatic
3. **Verify**: Use endpoint `/api/admin/info` to see file status
