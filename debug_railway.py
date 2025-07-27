#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para debug da aplicação na Railway
"""

import os
import sys

def check_environment():
    """Verifica as variáveis de ambiente necessárias"""
    print("=== DIAGNÓSTICO RAILWAY ===")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in directory: {os.listdir('.')}")
    
    # Verificar variáveis de ambiente importantes
    env_vars = [
        'DATABASE_URL',
        'ADMIN_PASSWORD', 
        'SECRET_KEY',
        'PORT',
        'FLASK_ENV'
    ]
    
    print("\n=== VARIÁVEIS DE AMBIENTE ===")
    for var in env_vars:
        value = os.getenv(var, 'NÃO DEFINIDA')
        if var == 'DATABASE_URL' and value != 'NÃO DEFINIDA':
            # Ocultar dados sensíveis
            value = value[:20] + "..." + value[-20:] if len(value) > 40 else value
        print(f"{var}: {value}")
    
    # Testar importação da aplicação
    print("\n=== TESTE DE IMPORTAÇÃO ===")
    try:
        from app import app, db
        print("✅ Aplicação importada com sucesso")
        print(f"✅ Database URI configurado: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
        
        # Testar conexão com banco
        with app.app_context():
            try:
                db.create_all()
                print("✅ Banco de dados conectado e tabelas criadas")
            except Exception as e:
                print(f"❌ Erro no banco de dados: {e}")
                
    except Exception as e:
        print(f"❌ Erro ao importar aplicação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_environment()
