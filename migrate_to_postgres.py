#!/usr/bin/env python3
"""
Script para migrar e criar as tabelas no PostgreSQL da Railway
"""

import os
from app import app, db, Presente, Confirmacao, init_db

def migrate_database():
    """Cria todas as tabelas no PostgreSQL e popula com dados de exemplo"""
    print("🔄 Iniciando migração para PostgreSQL...")
    
    with app.app_context():
        try:
            # Dropar todas as tabelas (cuidado em produção!)
            print("🗑️  Dropando tabelas existentes...")
            db.drop_all()
            
            # Criar todas as tabelas com a nova estrutura
            print("🏗️  Criando tabelas...")
            db.create_all()
            
            # Verificar se já existem dados
            if Presente.query.count() == 0:
                print("📦 Populando com dados de exemplo...")
                init_db_data()
            
            print("✅ Migração concluída com sucesso!")
            print(f"📊 Total de presentes: {Presente.query.count()}")
            print(f"📋 Total de confirmações: {Confirmacao.query.count()}")
            
        except Exception as e:
            print(f"❌ Erro durante a migração: {str(e)}")
            raise

def init_db_data():
    """Inicializa dados de exemplo no PostgreSQL"""
    presentes_exemplo = [
        {
            'nome': 'Jogo de Panelas Antiaderente',
            'descricao': 'Set completo com 5 panelas antiaderentes de alta qualidade',
            'preco': 299.90,
            'link_amazon': 'https://amazon.com.br/dp/exemplo1',
            'categoria': 'Cozinha'
        },
        {
            'nome': 'Conjunto de Taças de Cristal',
            'descricao': 'Set com 6 taças de cristal para vinho tinto e branco',
            'preco': 189.90,
            'link_amazon': 'https://amazon.com.br/dp/exemplo2',
            'categoria': 'Mesa e Bar'
        },
        {
            'nome': 'Aspirador de Pó Robô',
            'descricao': 'Aspirador inteligente com conexão WiFi e mapeamento',
            'preco': 899.90,
            'link_amazon': 'https://amazon.com.br/dp/exemplo3',
            'categoria': 'Eletrodomésticos'
        },
        {
            'nome': 'Jogo de Cama King Size',
            'descricao': 'Jogo de cama 100% algodão egípcio com 4 peças',
            'preco': 249.90,
            'link_amazon': 'https://amazon.com.br/dp/exemplo4',
            'categoria': 'Casa'
        },
        {
            'nome': 'Liquidificador de Alta Potência',
            'descricao': 'Liquidificador profissional 1200W com jarra de vidro',
            'preco': 329.90,
            'link_amazon': 'https://amazon.com.br/dp/exemplo5',
            'categoria': 'Eletrodomésticos'
        },
        {
            'nome': 'Conjunto de Pratos Porcelana',
            'descricao': 'Aparelho de jantar em porcelana para 6 pessoas',
            'preco': 399.90,
            'link_amazon': 'https://amazon.com.br/dp/exemplo6',
            'categoria': 'Mesa e Bar'
        }
    ]
    
    for presente_data in presentes_exemplo:
        presente = Presente(**presente_data)
        db.session.add(presente)
    
    try:
        db.session.commit()
        print("📦 Dados de exemplo criados com sucesso!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao criar dados de exemplo: {str(e)}")
        raise

if __name__ == '__main__':
    migrate_database()
