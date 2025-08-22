# 📚 Documentation - Complete Project Guide

This folder contains comprehensive documentation for the Folktale Reader project.

## 📁 **Available Documentation**

### **📖 Core Documentation**
- `API_DOCUMENTATION.md` - Complete API endpoint guide
- `DATABASE_SCHEMA.md` - Database structure and relationships
- `USER_GUIDE.md` - End-user manual and tutorials

### **🏆 System Documentation**
- `ACHIEVEMENT_SYSTEM.md` - Achievement mechanics and categories
- `PROJECT_STRUCTURE.md` - Project organization and architecture

## 🎯 **Documentation Overview**

### **For Developers**
- **API Documentation**: All endpoints, parameters, responses
- **Database Schema**: Tables, relationships, queries
- **Project Structure**: Code organization and dependencies

### **For Users**
- **User Guide**: How to use the application
- **Achievement System**: How to earn points and unlock achievements

### **For Contributors**
- **Project Structure**: Understanding the codebase
- **API Documentation**: Integration guidelines
- **Database Schema**: Data model understanding

## � **Current System Status**

### **✅ Fully Documented Features**
- 🏆 **24 Achievement System** across 5 categories
- 📊 **Ranking System** with global and category rankings  
- 🔐 **Authentication System** with secure password handling
- 📚 **Story Reading System** with progress tracking
- 🎯 **Quiz System** with performance tracking

### **📈 Statistics**
- **5 Documentation Files**: Comprehensive coverage
- **24 Achievements**: All documented with requirements
- **15+ API Endpoints**: Fully documented with examples
- **5 Database Tables**: Complete schema documentation

## 📖 **How to Use This Documentation**

1. **Start Here**: Read `USER_GUIDE.md` for basic usage
2. **For Development**: Check `API_DOCUMENTATION.md` and `DATABASE_SCHEMA.md`
3. **Understanding Features**: See `ACHIEVEMENT_SYSTEM.md`
4. **Project Overview**: Read `PROJECT_STRUCTURE.md`

## 🔄 **Documentation Maintenance**

- Documentation is kept up-to-date with code changes
- All new features require documentation updates
- Examples and code snippets are tested and verified
- User feedback is incorporated into documentation improvements

### � **Sistema de Progresso**
- Estatísticas detalhadas de aprendizado
- Sistema de badges/conquistas
- Histórico de pontuações
- Progresso visual por história e capítulo

### 🎨 **Interface Renovada**
- Design com tema de floresta brasileira
- Navegação por capítulos
- Indicadores visuais de progresso
- Responsivo para todos os dispositivos

## 🎮 **Como Funciona**

1. **Seleção da História**: Escolha uma das histórias folclóricas
2. **Leitura por Capítulos**: Leia cada capítulo sequencialmente
3. **Áudio**: Ouça a narração enquanto lê
4. **Quiz**: Teste sua compreensão (necessário 70%+ para avançar)
5. **Progresso**: Desbloqueie o próximo capítulo ao passar no quiz
6. **Estatísticas**: Acompanhe seu progresso e conquistas

## 📱 **Como Usar**

### 1. Executar o Aplicativo

```bash
# Navegar para a pasta do projeto
cd "d:\UFC\app\app"

# Ativar ambiente virtual
.venv\Scripts\activate

# Executar aplicação
python app.py
```

Acesse: http://localhost:5000

### 2. Fluxo de Uso

1. **Página Inicial**: Veja todas as histórias com progresso
2. **Seleção de História**: Clique na história desejada
3. **Navegação de Capítulos**: Use os botões de capítulo (🔒 = bloqueado, ▶️ = disponível, ✓ = concluído)
4. **Leitura**: Leia o conteúdo do capítulo
5. **Áudio**: Clique "Listen" para ouvir a narração
6. **Quiz**: Clique "Take Quiz" para testar conhecimento
7. **Progressão**: 70%+ no quiz libera próximo capítulo

## 📁 **Estrutura do Projeto**

```
app/
├── app.py                    # Backend Flask completo
├── templates/index.html      # Frontend SPA
├── requirements.txt          # Dependências Python
├── Brazilian Folktales.docx # Histórias (formato específico)
├── DOCX_FORMAT_GUIDE.md     # Guia de formatação do DOCX
└── README.md                # Esta documentação
```

## 📖 **Formato do Documento DOCX**

O arquivo `Brazilian Folktales.docx` deve seguir esta estrutura:

```
TÍTULO DA HISTÓRIA (em negrito/maiúsculo)

Chapter 1: Nome do Capítulo
[conteúdo do capítulo...]

Quiz Chapter 1
Q: Pergunta aqui?
A) Opção A
B) Opção B  
C) Opção C
D) Opção D
[resposta: B]

Chapter 2: Nome do Capítulo
[conteúdo...]
```

Ver `DOCX_FORMAT_GUIDE.md` para detalhes completos.

## 🔧 **API Endpoints**

- `GET /api/stories` - Lista histórias
- `GET /api/story/<id>/chapter/<num>` - Capítulo específico
- `GET /api/audio/<story_id>/<chapter_num>` - Áudio TTS
- `GET /api/quiz/<story_id>/<chapter_num>` - Quiz do capítulo
- `POST /api/submit_quiz` - Submete respostas do quiz
- `GET /api/progress` - Progresso do usuário
- `GET /api/statistics` - Estatísticas detalhadas

## 🏆 **Sistema de Badges**

- **First Steps** 🚶: Complete primeiro capítulo
- **Story Master** 👑: Complete uma história inteira
- **Quiz Expert** 🧠: 80%+ de precisão em 10+ quizzes

## 📊 **Estatísticas Disponíveis**

- Histórias iniciadas/concluídas
- Capítulos completados por história
- Tentativas de quiz e precisão
- Pontuações recentes
- Conquistas desbloqueadas
- Progresso visual detalhado

## 🛠️ **Tecnologias**

- **Backend**: Flask, Python
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Áudio**: Google Text-to-Speech (gTTS)
- **Processamento**: python-docx
- **Sessões**: Flask sessions para progresso

## 🎨 **Personalização**

### Adicionar Histórias
1. Edite `Brazilian Folktales.docx` seguindo o formato
2. Reinicie a aplicação

### Modificar Sistema de Quiz
- Edite função `parse_quiz_question()` em `app.py`
- Ajuste critério de aprovação (atualmente 70%)

### Customizar Badges
- Modifique `check_and_award_badges()` em `app.py`
- Adicione novos critérios de conquista

## 🔮 **Próximas Funcionalidades**

- [ ] Sistema de usuários múltiplos
- [ ] Exportação de progresso
- [ ] Mais tipos de exercícios
- [ ] Integração com dicionários
- [ ] Modo offline
- [ ] Gamificação avançada

## 🐛 **Solução de Problemas**

**Histórias não aparecem**: Verifique o formato do arquivo DOCX
**Áudio não funciona**: Verifique conexão internet (usa Google TTS)
**Quiz vazio**: Verifique formatação das perguntas no DOCX
**Progresso perdido**: Progresso é salvo por sessão do navegador

## 🤝 **Contribuindo**

Contribuições são bem-vindas! Este projeto foi desenvolvido para aprendizado interativo de inglês através da rica cultura folclórica brasileira.
