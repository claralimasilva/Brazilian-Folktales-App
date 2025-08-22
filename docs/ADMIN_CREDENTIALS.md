# Credenciais de Administrador - Folktale Reader

## 🔐 Contas de Administrador Padrão

### Admin Principal (Sistema de Banco de Dados)
- **Usuário:** `admin`
- **Senha:** `admin_secure_2024!`

**Nota:** Esta conta é criada automaticamente no primeiro acesso ao sistema.

## 🔒 Sistema de Segurança Atualizado

### Funcionalidades Protegidas por Login
- ✅ **Painel de Administração** (apenas admins)
- ✅ **Conversão DOCX → JSON** (apenas admins)
- ✅ **Informações do sistema** (apenas admins)
- ✅ **Download do arquivo JSON** (apenas admins)
- ✅ **Gerenciamento de usuários** (apenas admins)
- ✅ **Leitura de histórias** (usuários logados)
- ✅ **Quiz e progressão** (usuários logados)
- ✅ **Estatísticas pessoais** (usuários logados)

### Para Usuários Não-Logados
- ✅ Página de boas-vindas
- ✅ Informações sobre o app
- ❌ Acesso a histórias
- ❌ Acesso a funcionalidades

## 🛡️ Configuração de Segurança com Banco de Dados

### Como criar novos administradores:
1. Faça login como admin existente
2. Use a função `create_user()` no banco de dados
3. Defina `user_type='admin'` para privilégios administrativos

### Exemplo via código Python:
```python
from database import create_user
# Criar novo admin
result = create_user('novo_admin', 'senha_segura', 'admin')
```

### Como alterar senha do admin padrão:
1. Acesse o banco SQLite diretamente ou
2. Use a interface admin para gerenciar usuários
3. A senha é armazenada com hash SHA256

## 🗃️ Estrutura do Banco de Dados

### Tabela `users`:
- `username`: Nome do usuário (único)
- `password_hash`: Senha com hash SHA256
- `user_type`: 'admin' ou 'regular'
- `created_at`: Data de criação
- `last_login`: Último acesso
- `is_active`: Status da conta

## 🔄 Como usar o Sistema:

### Para Usuários Normais:
1. **Registro:** Crie uma conta na tela de login
2. **Login:** Use suas credenciais para acessar
3. **Funcionalidades:** Leia histórias, faça quizzes, veja progresso

### Para Administradores:
1. **Login Admin:** Use `admin` / `admin_secure_2024!`
2. **Painel Admin:** Acesse funcionalidades administrativas
3. **Gerenciamento:** Converta DOCX, gerencie usuários
4. **Logout:** Sempre faça logout após uso

## ⚠️ Importantes Considerações de Segurança:

### Em Produção:
- ✅ **MUDE A SENHA PADRÃO imediatamente**
- ✅ Use senhas complexas (12+ caracteres)
- ✅ Considere autenticação de dois fatores
- ✅ Monitore tentativas de login inválidas
- ✅ Use HTTPS em produção

### Estrutura de Segurança:
- 🔐 Senhas com hash SHA256
- 🔐 Sessões Flask seguras
- 🔐 Controle de acesso baseado em roles
- 🔐 Banco de dados SQLite com proteção
- 🔐 Validação de entrada em todos os endpoints

### Backup e Manutenção:
- 📦 Faça backup regular do `folktale_users.db`
- 📦 Monitore logs de acesso
- 📦 Atualize dependências regularmente

## 🆘 Recuperação de Acesso:

Se perder acesso admin:
1. Acesse diretamente o banco SQLite
2. Resete a senha via código Python
3. Ou delete o arquivo `folktale_users.db` (perde todos os dados!)

```python
# Recuperação de emergência
from database import hash_password, get_db_connection
conn = get_db_connection()
new_password = hash_password('nova_senha_admin')
conn.execute('UPDATE users SET password_hash = ? WHERE username = "admin"', (new_password,))
conn.commit()
```
