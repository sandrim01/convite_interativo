# 💕 Convite Interativo de Casamento

Um convite de casamento interativo e elegante desenvolvido com Flask, que proporciona uma experiência única aos convidados.

## 🌟 Características

- **Convites personalizados** - Links únicos para cada convidado
- **Confirmação de presença** - Sistema completo de RSVP
- **Lista de presentes** - Links diretos para produtos da Amazon
- **Envio por WhatsApp** - Sistema de envio em massa
- **Painel administrativo** - Gerenciamento completo
- **Design responsivo** - Funciona em todos os dispositivos
- **Banco PostgreSQL** - Dados seguros na nuvem

## 🚀 Tecnologias

- **Backend**: Python/Flask
- **Banco**: PostgreSQL (Railway)
- **Frontend**: HTML5, CSS3, JavaScript
- **Deploy**: Railway Platform

## � Funcionalidades

### Para os Convidados:
- Convite personalizado com nome pré-preenchido
- Confirmação de presença simples
- Lista de presentes interativa
- Interface elegante e intuitiva

### Para os Noivos:
- Cadastro de convidados
- Envio automático por WhatsApp
- Gerenciamento de confirmações
- Controle da lista de presentes
- Relatórios em tempo real

## 🛠️ Como Usar

### 1. Acesso ao Sistema
- **URL Principal**: Seu domínio na Railway
- **Painel Admin**: `/admin` (senha: configurada no .env)

### 2. Cadastrar Convidados
1. Acesse o painel administrativo
2. Vá para "Cadastro de Convidados"
3. Adicione nome e WhatsApp
4. O sistema gera link único automaticamente

### 3. Enviar Convites
1. Na seção "WhatsApp" do painel admin
2. Clique em "Gerar Links para WhatsApp"
3. Envie as mensagens personalizadas
4. Marque como enviado conforme necessário

### 4. Acompanhar Respostas
- Todas as confirmações aparecem no painel
- Status automático: pendente → enviado → confirmado/recusado
- Relatórios em tempo real

## ⚙️ Configuração (.env)
```env
DATABASE_URL=postgresql://seu-banco-postgresql
SECRET_KEY=sua-chave-secreta
ADMIN_PASSWORD=sua-senha-admin
```

## 🚀 Deploy na Railway

1. Conecte seu repositório GitHub à Railway
2. Configure as variáveis de ambiente
3. Deploy automático via Git push

## 📂 Estrutura do Projeto

```
convite_interativo/
├── app.py              # Aplicação Flask principal
├── requirements.txt    # Dependências Python
├── Procfile           # Configuração Railway
├── .env               # Variáveis de ambiente
├── templates/         # Templates HTML
│   ├── convite.html   # Página principal do convite
│   ├── admin.html     # Painel administrativo
│   └── ...
└── static/            # CSS e JavaScript
    ├── css/
    └── js/
```

## 🎯 Status do Projeto

✅ **Funcional e em Produção**
- Sistema completo de convites personalizados
- Envio automático por WhatsApp
- Confirmações em tempo real
- Painel administrativo completo
- Deploy na Railway configurado

## 📋 Próximos Passos (Opcional)

- [ ] Integração com Google Maps
- [ ] Galeria de fotos
- [ ] Sistema de presentes com pagamento
- [ ] Notificações por email
- [ ] App mobile

---

💕 **Desenvolvido com amor para tornar seu casamento ainda mais especial!** �

Para dúvidas ou problemas, abra uma issue no GitHub.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

Feito com ❤️ para Alessandro & [Nome da Noiva]
