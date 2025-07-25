# Convite Interativo de Casamento

Um convite de casamento interativo e elegante desenvolvido com Flask, que proporciona uma experiência única aos convidados.

## 🌟 Características

- **Convite em formato de carta interativa** - Os convidados clicam e navegam através do convite
- **Integração com Google Maps** - Localização da cerimônia e recepção
- **Lista de presentes da Amazon** - Links diretos para produtos
- **Confirmação de presença** - Sistema completo de RSVP
- **Painel administrativo** - Gerenciamento de presentes e confirmações
- **Design responsivo** - Funciona perfeitamente em dispositivos móveis
- **Banco de dados PostgreSQL** - Armazenamento seguro dos dados

## 🚀 Tecnologias Utilizadas

- **Backend**: Python/Flask
- **Banco de dados**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript
- **Deploy**: Railway
- **Mapas**: Google Maps API
- **Presentes**: Links da Amazon

## 📋 Funcionalidades

### Para os Convidados:
- Visualização do convite em formato de carta interativa
- Confirmação de presença online
- Visualização da localização no Google Maps
- Acesso à lista de presentes da Amazon
- Interface intuitiva e elegante

### Para os Noivos (Painel Admin):
- Gerenciamento da lista de presentes
- Visualização das confirmações de presença
- Adição/remoção de itens da lista
- Estatísticas dos convidados

## 🛠️ Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- PostgreSQL
- Conta no Google Cloud (para Maps API)
- Conta na Railway (para deploy)

### Instalação Local

1. Clone o repositório:
```bash
git clone https://github.com/sandrim01/convite_interativo.git
cd convite_interativo
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente no arquivo `.env`:
```env
DATABASE_URL=postgresql://postgres:pmQzCzKBhjuLMJvLBUGZkuYwkVoCOtCq@crossover.proxy.rlwy.net:14871/railway
SECRET_KEY=sua-chave-secreta-aqui
FLASK_ENV=development
GOOGLE_MAPS_API_KEY=sua-chave-do-google-maps-aqui
```

5. Execute a aplicação:
```bash
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

## 🌐 Deploy na Railway

1. Conecte seu repositório GitHub à Railway
2. Configure as variáveis de ambiente na Railway
3. O deploy será feito automaticamente

## 📱 Como Usar

### Configuração Inicial:
1. Acesse `/admin` para gerenciar presentes e confirmações
2. Adicione presentes com links da Amazon
3. Configure as coordenadas dos locais no código
4. Obtenha uma chave do Google Maps API

### Personalizações:
- Altere os nomes dos noivos no arquivo `convite.html`
- Modifique as datas e locais conforme necessário
- Adicione sua chave do Google Maps
- Personalize cores e estilos no arquivo CSS

## 🎨 Estrutura do Projeto

```
convite_interativo/
├── app.py                 # Aplicação Flask principal
├── requirements.txt       # Dependências Python
├── Procfile              # Configuração Railway
├── .env                  # Variáveis de ambiente
├── templates/            # Templates HTML
│   ├── base.html
│   ├── convite.html
│   ├── lista_presentes.html
│   └── admin.html
└── static/               # Arquivos estáticos
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

## 🔧 Customização

### Alterando Informações do Casamento:
1. Edite `templates/convite.html` para alterar nomes, datas e locais
2. Atualize as coordenadas no JavaScript para os locais corretos
3. Modifique as cores e estilos em `static/css/style.css`

### Adicionando Presentes:
1. Acesse `/admin` 
2. Use o formulário para adicionar novos presentes
3. Insira links válidos da Amazon

## 🔐 Segurança

- Variáveis sensíveis em arquivo `.env`
- Validação de formulários no frontend e backend
- Sanitização de dados de entrada
- HTTPS em produção (Railway)

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no GitHub.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

Feito com ❤️ para Alessandro & [Nome da Noiva]
