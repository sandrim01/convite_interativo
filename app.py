import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
import hashlib

app = Flask(__name__)

# Configuração do banco de dados
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///convite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'chave-secreta-para-desenvolvimento')

# Senha do administrador (em produção, use variável de ambiente)
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'casamento2024')  # Altere esta senha!

db = SQLAlchemy(app)

# Função para verificar autenticação
def verificar_admin():
    return session.get('admin_logged_in') == True

def login_required(f):
    """Decorator para proteger rotas administrativas"""
    def decorated_function(*args, **kwargs):
        if not verificar_admin():
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Modelos do banco de dados
class Presente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float)
    link_amazon = db.Column(db.String(500), nullable=False)
    categoria = db.Column(db.String(100))
    disponivel = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Presente {self.nome}>'

class Confirmacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_convidado = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200))
    telefone = db.Column(db.String(20))
    confirmou_presenca = db.Column(db.Boolean, default=False)
    numero_acompanhantes = db.Column(db.Integer, default=0)
    observacoes = db.Column(db.Text)
    data_confirmacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Confirmacao {self.nome_convidado}>'

# Rotas da aplicação
@app.route('/')
def convite():
    """Página principal do convite interativo"""
    return render_template('convite.html')

@app.route('/lista_presentes')
def lista_presentes():
    """Página com a lista de presentes"""
    try:
        # Tentar criar as tabelas primeiro
        db.create_all()
        
        # Verificar se a tabela existe e tem dados
        presentes = Presente.query.filter_by(disponivel=True).all()
        
        # Se não há presentes, inicializar dados de exemplo
        if len(presentes) == 0:
            init_db()
            presentes = Presente.query.filter_by(disponivel=True).all()
            
        app.logger.info(f"Encontrados {len(presentes)} presentes disponíveis")
        return render_template('lista_presentes.html', presentes=presentes)
    except Exception as e:
        app.logger.error(f"Erro na lista de presentes: {str(e)}")
        # Se der erro, retornar lista vazia mas não quebrar a página
        return render_template('lista_presentes.html', presentes=[])

@app.route('/test_db')
def test_db():
    """Rota para testar a conexão com o banco"""
    try:
        db.create_all()
        count = Presente.query.count()
        return f"Conexão OK! Total de presentes: {count}"
    except Exception as e:
        return f"Erro na conexão: {str(e)}"

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Página de login do administrador"""
    if request.method == 'POST':
        senha = request.form.get('senha')
        
        if senha == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Senha incorreta. Tente novamente.', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin-logout')
def admin_logout():
    """Logout do administrador"""
    session.pop('admin_logged_in', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('convite'))

@app.route('/admin')
@login_required
def admin():
    """Página administrativa para gerenciar presentes"""
    presentes = Presente.query.all()
    confirmacoes = Confirmacao.query.all()
    return render_template('admin.html', presentes=presentes, confirmacoes=confirmacoes)

@app.route('/api/confirmar-presenca', methods=['POST'])
def confirmar_presenca():
    """API para confirmar presença"""
    try:
        data = request.get_json()
        
        confirmacao = Confirmacao(
            nome_convidado=data.get('nome'),
            email=data.get('email'),
            telefone=data.get('telefone'),
            confirmou_presenca=data.get('confirmou_presenca', False),
            numero_acompanhantes=data.get('acompanhantes', 0),
            observacoes=data.get('observacoes', '')
        )
        
        db.session.add(confirmacao)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Confirmação enviada com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao enviar confirmação: {str(e)}'}), 500

@app.route('/api/adicionar-presente', methods=['POST'])
@login_required
def adicionar_presente():
    """API para adicionar presente à lista"""
    try:
        data = request.get_json()
        
        presente = Presente(
            nome=data.get('nome'),
            descricao=data.get('descricao'),
            preco=data.get('preco'),
            link_amazon=data.get('link_amazon'),
            categoria=data.get('categoria', 'Geral')
        )
        
        db.session.add(presente)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Presente adicionado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao adicionar presente: {str(e)}'}), 500

@app.route('/api/remover-presente/<int:presente_id>', methods=['DELETE'])
@login_required
def remover_presente(presente_id):
    """API para remover presente da lista"""
    try:
        presente = Presente.query.get_or_404(presente_id)
        presente.disponivel = False
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Presente removido da lista!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao remover presente: {str(e)}'}), 500

# Inicialização do banco de dados
def init_db():
    """Inicializa o banco de dados com dados de exemplo"""
    with app.app_context():
        db.create_all()
        
        # Verifica se já existem presentes cadastrados
        if Presente.query.count() == 0:
            # Adiciona alguns presentes de exemplo
            presentes_exemplo = [
                {
                    'nome': 'Jogo de Panelas Antiaderente',
                    'descricao': 'Set completo com 5 panelas antiaderentes',
                    'preco': 299.90,
                    'link_amazon': 'https://amazon.com.br/dp/exemplo1',
                    'categoria': 'Cozinha'
                },
                {
                    'nome': 'Conjunto de Taças de Cristal',
                    'descricao': 'Set com 6 taças de cristal para vinho',
                    'preco': 189.90,
                    'link_amazon': 'https://amazon.com.br/dp/exemplo2',
                    'categoria': 'Mesa e Bar'
                },
                {
                    'nome': 'Aspirador de Pó Robô',
                    'descricao': 'Aspirador inteligente com conexão WiFi',
                    'preco': 899.90,
                    'link_amazon': 'https://amazon.com.br/dp/exemplo3',
                    'categoria': 'Eletrodomésticos'
                }
            ]
            
            for presente_data in presentes_exemplo:
                presente = Presente(**presente_data)
                db.session.add(presente)
            
            db.session.commit()
            print("Banco de dados inicializado com dados de exemplo!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
