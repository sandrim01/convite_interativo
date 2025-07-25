<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Convite Interativo de Casamento - Instruções para Copilot

Este é um projeto Flask para um convite de casamento interativo. Siga estas diretrizes ao trabalhar neste projeto:

## Contexto do Projeto
- Aplicação web Flask para convite de casamento
- Interface de carta interativa onde convidados clicam para navegar
- Integração com Google Maps para localização
- Lista de presentes com links da Amazon
- Banco PostgreSQL para armazenamento
- Deploy na plataforma Railway

## Padrões de Código
- Use Python 3.8+ com Flask
- Siga PEP 8 para formatação Python
- Use template Jinja2 para HTML
- CSS com classes BEM quando possível
- JavaScript ES6+ com funções assíncronas

## Estrutura de Arquivos
- `app.py`: Aplicação principal Flask
- `templates/`: Templates Jinja2
- `static/css/`: Estilos CSS
- `static/js/`: Scripts JavaScript
- `requirements.txt`: Dependências Python

## Considerações de Design
- Design responsivo mobile-first
- Paleta de cores romântica (rosa, bege, marrom)
- Fontes: Dancing Script, Playfair Display, Open Sans
- Animações suaves e transições CSS
- Interface intuitiva e elegante

## APIs e Integrações
- Google Maps API para localização
- PostgreSQL para banco de dados
- Links diretos para Amazon
- Sistema de confirmação RSVP

## Deployment
- Configure variáveis de ambiente no .env
- Use gunicorn para produção
- Deploy na Railway com Procfile
- Banco PostgreSQL em produção

## Funcionalidades Principais
1. Convite interativo tipo carta
2. Confirmação de presença
3. Lista de presentes da Amazon
4. Painel administrativo
5. Integração com mapas
6. Design responsivo
