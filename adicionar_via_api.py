#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para adicionar convidados usando a aplicação Flask
"""

import requests
import json

# URL base da aplicação
BASE_URL = 'http://127.0.0.1:5000'

# Primeiro fazer login como admin
session = requests.Session()

# Fazer login
login_data = {'senha': 'casamento2024'}
response = session.post(f'{BASE_URL}/admin-login', data=login_data)

if response.status_code != 200:
    print("Erro ao fazer login")
    exit(1)

print("Login realizado com sucesso!")

# Convidados de exemplo
convidados_exemplo = [
    {'nome': 'Maria Silva', 'whatsapp': '11987654321', 'email': 'maria@email.com'},
    {'nome': 'João Santos', 'whatsapp': '11976543210', 'email': 'joao@email.com'},
    {'nome': 'Ana Costa', 'whatsapp': '11965432109', 'email': 'ana@email.com'},
    {'nome': 'Carlos Oliveira', 'whatsapp': '11954321098', 'email': 'carlos@email.com'},
    {'nome': 'Fernanda Lima', 'whatsapp': '11943210987', 'email': 'fernanda@email.com'}
]

print("\nAdicionando convidados...")

for convidado in convidados_exemplo:
    response = session.post(
        f'{BASE_URL}/api/cadastrar-convidado',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(convidado)
    )
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print(f"✅ {convidado['nome']} - Código: {result['codigo']}")
        else:
            print(f"❌ Erro ao cadastrar {convidado['nome']}: {result['message']}")
    else:
        print(f"❌ Erro HTTP ao cadastrar {convidado['nome']}: {response.status_code}")

print("\n🎉 Processo concluído!")
print("Acesse o painel administrativo para ver os convidados e testar o envio por WhatsApp.")
print(f"URL: {BASE_URL}/admin")
