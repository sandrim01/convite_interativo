#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aplicação Flask mínima para testar se funciona na Railway
"""

import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>✅ Aplicação Flask Funcionando!</h1>
    <p>Se você está vendo esta página, a aplicação básica está rodando.</p>
    <ul>
        <li><a href="/health">Health Check</a></li>
        <li><a href="/env">Variáveis de Ambiente</a></li>
        <li><a href="/test">Teste de Funcionalidades</a></li>
    </ul>
    """

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Aplicação funcionando na Railway',
        'port': os.getenv('PORT', 'não definida'),
        'database_url': 'configurada' if os.getenv('DATABASE_URL') else 'não configurada'
    })

@app.route('/env')
def env_vars():
    """Mostra variáveis de ambiente (sem dados sensíveis)"""
    env_info = {
        'PORT': os.getenv('PORT', 'não definida'),
        'FLASK_ENV': os.getenv('FLASK_ENV', 'não definida'),
        'SECRET_KEY': 'configurada' if os.getenv('SECRET_KEY') else 'não configurada',
        'DATABASE_URL': 'configurada' if os.getenv('DATABASE_URL') else 'não configurada',
        'ADMIN_PASSWORD': 'configurada' if os.getenv('ADMIN_PASSWORD') else 'não configurada'
    }
    return jsonify(env_info)

@app.route('/test')
def test():
    """Testa importação dos módulos principais"""
    try:
        # Testar importações
        from flask_sqlalchemy import SQLAlchemy
        from datetime import datetime
        import psycopg2
        
        return jsonify({
            'status': 'ok',
            'message': 'Todos os módulos importados com sucesso',
            'modules': ['Flask', 'SQLAlchemy', 'datetime', 'psycopg2']
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro na importação: {str(e)}'
        })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
