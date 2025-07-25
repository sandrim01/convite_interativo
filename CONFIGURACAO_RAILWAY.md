# 🚂 CONFIGURAÇÃO RAILWAY - CONVITE ALESSANDRO

## ✅ REPOSITÓRIO GITHUB CONFIGURADO
- **URL**: https://github.com/sandrim01/convite_interativo
- **Status**: ✅ Código enviado com sucesso!

## 🔧 PRÓXIMOS PASSOS NA RAILWAY

### 1. Acessar Railway
1. Vá para: https://railway.app
2. Faça login com sua conta GitHub

### 2. Criar Novo Projeto
1. Clique em **"New Project"**
2. Selecione **"Deploy from GitHub repo"**
3. Escolha o repositório: **sandrim01/convite_interativo**
4. Clique em **"Deploy"**

### 3. Configurar Variáveis de Ambiente
Na aba **"Variables"** do seu projeto, adicione:

```env
SECRET_KEY=Alessandro_Casamento_2024_Chave_Muito_Secreta_123!
ADMIN_PASSWORD=AdminAlessandro2024!
DATABASE_URL=postgresql://postgres:pmQzCzKBhjuLMJvLBUGZkuYwkVoCOtCq@crossover.proxy.rlwy.net:14871/railway
```

### 4. ⚠️ IMPORTANTE - CONFIGURAR O BANCO DE DADOS
O banco PostgreSQL já está criado! A URL é:
```
postgresql://postgres:pmQzCzKBhjuLMJvLBUGZkuYwkVoCOtCq@crossover.proxy.rlwy.net:14871/railway
```

**Esta URL já está configurada como DATABASE_URL acima.**

### 5. Aguardar Deploy
- Railway fará o build automaticamente
- Acompanhe os logs na aba "Deployments"
- Quando terminar, você receberá uma URL como:
  `https://convite-interativo-production.up.railway.app`

## 🔐 CREDENCIAIS DE ACESSO

### Para Administração:
- **URL Admin**: `https://SEU_DOMINIO_RAILWAY.app/admin`
- **Senha**: `AdminAlessandro2024!`

### Banco de Dados (já configurado):
- **Host**: crossover.proxy.rlwy.net
- **Port**: 14871
- **Database**: railway
- **Username**: postgres
- **Password**: pmQzCzKBhjuLMJvLBUGZkuYwkVoCOtCq

## 📱 FUNCIONALIDADES DO SITE

### Para Convidados:
✅ Convite interativo tipo carta
✅ Confirmação de presença
✅ Visualização de locais no Google Maps
✅ Lista de presentes da Amazon
✅ Design responsivo mobile

### Para Administrador:
✅ Painel de controle completo
✅ Gerenciar lista de presentes
✅ Ver confirmações de presença
✅ Adicionar/remover itens
✅ Autenticação segura

## 🎯 CHECKLIST DE DEPLOY

- [x] Código no GitHub
- [x] Repositório conectado
- [ ] Projeto criado na Railway
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy realizado
- [ ] Site funcionando
- [ ] Admin acessível
- [ ] Testes realizados

## 🔄 ATUALIZAÇÕES FUTURAS

Para fazer mudanças no site:
```bash
# 1. Editar arquivos
# 2. Commitar mudanças:
git add .
git commit -m "Descrição da mudança"
git push

# 3. Railway fará redeploy automático!
```

## 🆘 SOLUÇÃO DE PROBLEMAS

### Se o deploy falhar:
1. Verifique os logs na Railway
2. Confirme se todas as variáveis estão configuradas
3. Verifique se DATABASE_URL está correto

### Se o admin não funcionar:
1. Confirme ADMIN_PASSWORD nas variáveis
2. Teste a URL: `https://seu-site.railway.app/admin`
3. Use a senha: `AdminAlessandro2024!`

### Se o banco não conectar:
1. Confirme DATABASE_URL exata nas variáveis
2. Verifique se o serviço PostgreSQL está ativo

## 🎉 RESULTADO FINAL

Quando concluído, você terá:
- ✅ Site de convite online 24/7
- ✅ URL personalizada profissional
- ✅ Banco de dados seguro
- ✅ Painel administrativo funcional
- ✅ SSL/HTTPS automático
- ✅ Backup automático

---

**🚀 SEU CONVITE DE CASAMENTO ESTARÁ NO AR! 🚀**

URL GitHub: https://github.com/sandrim01/convite_interativo
Próximo: Railway Deploy!
