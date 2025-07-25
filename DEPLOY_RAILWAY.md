# 🚂 Deploy na Railway - Guia Completo

## 📋 Pré-requisitos

1. ✅ Código no GitHub
2. ✅ Conta na Railway (https://railway.app)
3. ✅ Variáveis de ambiente configuradas

## 🚀 Passos para Deploy

### 1. Preparação do Repositório GitHub

```bash
# Se ainda não fez:
git init
git add .
git commit -m "Initial commit: Convite Interativo"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git push -u origin main
```

### 2. Configuração na Railway

1. **Acesse Railway**: https://railway.app
2. **Login/Cadastro**: Use sua conta GitHub
3. **Novo Projeto**: 
   - Clique em "New Project"
   - Selecione "Deploy from GitHub repo"
   - Escolha o repositório do convite

### 3. Configuração das Variáveis de Ambiente

Na Railway, vá em **Variables** e adicione:

```env
SECRET_KEY=sua_chave_secreta_muito_longa_aqui
ADMIN_PASSWORD=sua_senha_admin_segura
```

**⚠️ IMPORTANTE**: A Railway criará automaticamente o `DATABASE_URL` para PostgreSQL!

### 4. Configuração do Banco de Dados

1. **Adicionar PostgreSQL**:
   - No dashboard do projeto
   - Clique em "Add Service"
   - Selecione "PostgreSQL"
   - A Railway conectará automaticamente

2. **Inicialização Automática**:
   - As tabelas serão criadas automaticamente na primeira execução
   - O Flask-SQLAlchemy detectará o PostgreSQL via `DATABASE_URL`

### 5. Deploy Automático

1. **Commit & Push**:
   ```bash
   git add .
   git commit -m "Preparação para Railway"
   git push
   ```

2. **Railway Deploy**:
   - Deploy acontece automaticamente
   - Acompanhe os logs na Railway
   - URL será gerada automaticamente

## 🔧 Arquivos de Configuração

### `Procfile`
```
web: gunicorn app:app
```

### `railway.json`
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### `requirements.txt`
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
python-dotenv==1.0.0
gunicorn==21.2.0
psycopg2-binary==2.9.7
```

## 🌐 Acesso ao Site

1. **URL Automática**: Railway gerará uma URL como `https://seu-projeto.railway.app`
2. **Domínio Personalizado**: Configure nas configurações do projeto
3. **HTTPS**: Automaticamente habilitado

## 🔐 Acesso Administrativo

- **URL**: `https://seu-site.railway.app/admin`
- **Senha**: A que você definiu em `ADMIN_PASSWORD`

## 📊 Monitoramento

1. **Logs**: Na Railway, aba "Logs"
2. **Métricas**: CPU, RAM, requisições
3. **Database**: Monitoring automático PostgreSQL

## 🐛 Troubleshooting

### Erro de Dependências
```bash
# Certifique-se que requirements.txt está correto
pip freeze > requirements.txt
```

### Erro de Banco
```bash
# Verifique se DATABASE_URL está configurado
# Railway configura automaticamente para PostgreSQL
```

### Erro 500
```bash
# Verifique logs na Railway
# Confirme SECRET_KEY e ADMIN_PASSWORD
```

## 🔄 Atualizações

```bash
# Para atualizar o site:
git add .
git commit -m "Atualização: descrição da mudança"
git push

# Railway fará redeploy automaticamente!
```

## 🎯 Checklist Final

- [ ] Código no GitHub
- [ ] Projeto criado na Railway
- [ ] PostgreSQL adicionado
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy realizado com sucesso
- [ ] Site acessível na URL gerada
- [ ] Admin funcionando
- [ ] Banco de dados operacional

## 📞 Suporte

- Railway Docs: https://docs.railway.app
- GitHub Issues: Para problemas específicos do código

---

🎉 **Parabéns! Seu convite está no ar!** 🎉
