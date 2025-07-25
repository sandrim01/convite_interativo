# Configuração para Produção

## 🔑 Chave do Google Maps API

Para que os mapas funcionem corretamente, você precisa:

1. **Criar uma conta no Google Cloud Console:**
   - Acesse: https://console.cloud.google.com/
   - Crie um novo projeto

2. **Ativar a API do Google Maps:**
   - No console, vá para "APIs & Services" > "Library"
   - Procure por "Maps JavaScript API" e ative
   - Procure por "Places API" e ative (se necessário)

3. **Criar uma chave de API:**
   - Vá para "APIs & Services" > "Credentials"
   - Clique em "Create Credentials" > "API Key"
   - Copie a chave gerada

4. **Configurar restrições (Recomendado):**
   - Clique na chave criada
   - Em "Application restrictions", selecione "HTTP referrers"
   - Adicione seu domínio: `https://seudominio.railway.app/*`

5. **Adicionar a chave no projeto:**
   - No arquivo `.env`: `GOOGLE_MAPS_API_KEY=sua_chave_aqui`
   - Na Railway: adicione como variável de ambiente

## 🚂 Deploy na Railway

### 1. Preparar o Repositório
```bash
# Inicializar Git (se ainda não fez)
git init
git add .
git commit -m "Initial commit"

# Conectar ao GitHub
git remote add origin https://github.com/sandrim01/convite_interativo.git
git branch -M main
git push -u origin main
```

### 2. Configurar na Railway
1. Acesse: https://railway.app/
2. Faça login com GitHub
3. Clique em "New Project" > "Deploy from GitHub repo"
4. Selecione o repositório `convite_interativo`

### 3. Adicionar Banco PostgreSQL
1. No projeto Railway, clique em "New Service"
2. Selecione "Database" > "PostgreSQL"
3. Copie a URL de conexão gerada

### 4. Configurar Variáveis de Ambiente
No Railway, adicione estas variáveis:
```
DATABASE_URL=postgresql://... (URL do banco PostgreSQL)
SECRET_KEY=uma-chave-secreta-forte
GOOGLE_MAPS_API_KEY=sua-chave-do-google-maps
ADMIN_PASSWORD=sua-senha-admin-segura
FLASK_ENV=production
```

⚠️ **IMPORTANTE:** Altere a senha padrão `casamento2024` por uma senha forte!

### 5. Adicionar psycopg2 para Produção
Crie um arquivo `requirements-prod.txt`:
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
psycopg2-binary==2.9.7
python-dotenv==1.0.0
gunicorn==21.2.0
```

E atualize o `Procfile`:
```
web: pip install psycopg2-binary==2.9.7 && gunicorn app:app
```

## 🎨 Personalização

### Alterar Nomes dos Noivos
No arquivo `templates/convite.html`, substitua:
- `Alessandro` pelo nome do noivo
- `[Nome da Noiva]` pelo nome da noiva

### Alterar Datas e Locais
1. **Data:** Linha ~45 em `convite.html`
2. **Horário:** Linha ~46 em `convite.html`
3. **Local da Cerimônia:** Linha ~55-57 em `convite.html`
4. **Local da Recepção:** Linha ~75-78 em `convite.html`

### Alterar Coordenadas dos Mapas
No arquivo `templates/convite.html`, linha ~200:
```javascript
const coordenadas = {
    cerimonia: { lat: -23.5505, lng: -46.6333 }, // Suas coordenadas
    recepcao: { lat: -23.5489, lng: -46.6388 }   // Suas coordenadas
};
```

### Cores e Estilo
Edite o arquivo `static/css/style.css` para personalizar:
- Cores principais: `#FFB6C1`, `#8B4513`
- Fontes: `Dancing Script`, `Playfair Display`

## 📱 Funcionalidades

### Para os Convidados:
- ✅ Convite interativo tipo carta
- ✅ Visualização no Google Maps
- ✅ Confirmação de presença
- ✅ Lista de presentes da Amazon
- ✅ Design responsivo

### Para os Administradores:
- ✅ **Login protegido por senha** - Acesso seguro ao painel
- ✅ **Acesse `/admin-login`** para entrar no sistema
- ✅ Adicionar/remover presentes
- ✅ Ver confirmações de presença
- ✅ Links diretos para Amazon
- ✅ **Logout seguro** quando terminar

## 🔐 Sistema de Autenticação

### Acesso Administrativo:
1. **URL de login:** `https://seusite.com/admin-login`
2. **Senha padrão:** `casamento2024` (ALTERE ESTA SENHA!)
3. **Link discreto:** Ícone ⚙️ no final do convite
4. **Logout automático:** Feche o navegador ou clique em "Sair"

### Segurança:
- ✅ Todas as rotas administrativas protegidas
- ✅ Sessão segura com timeout
- ✅ Senha configurável via variável de ambiente
- ✅ Interface de login elegante
- ✅ Redirecionamento automático se não logado

## 🔧 Manutenção

### Backup do Banco
Use o comando Railway CLI:
```bash
railway run pg_dump $DATABASE_URL > backup.sql
```

### Logs da Aplicação
```bash
railway logs
```

### Atualizar Aplicação
```bash
git add .
git commit -m "Atualização"
git push origin main
```

O Railway fará o deploy automaticamente!

## 📞 Suporte

Se houver problemas:
1. Verifique os logs no Railway
2. Confirme as variáveis de ambiente
3. Teste localmente primeiro
4. Verifique se a chave do Google Maps está ativa

---

**Nota:** Este convite foi desenvolvido especialmente para Alessandro. Para usar em outro casamento, personalize os nomes, datas e locais conforme necessário.
