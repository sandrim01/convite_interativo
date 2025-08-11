import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
import hashlib
from functools import wraps
from urllib.parse import quote

# Carregar variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configuração de logging para produção
if not app.debug:
    import logging
    app.logger.setLevel(logging.INFO)

# Configuração do banco de dados
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

# Debug: verificar qual banco está sendo usado
print(f"DATABASE_URL detectada: {'SIM' if database_url else 'NÃO'}")
if database_url:
    print(f"Tipo de banco: {'PostgreSQL' if 'postgresql://' in database_url else 'Outro'}")
else:
    print("Usando SQLite local")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///convite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'chave-secreta-para-desenvolvimento')

# Configurações de encoding para PostgreSQL
if database_url and 'postgresql://' in database_url:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'client_encoding': 'utf8',
        'connect_args': {
            'options': '-csearch_path=public',
            'client_encoding': 'utf8'
        },
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'echo': False
    }

# Configuração de sessão mais robusta para produção
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400

# Senha do administrador
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'casamento2024')

db = SQLAlchemy(app)

# Função para limpar encoding UTF-8
def limpar_encoding_utf8(texto):
    if not texto:
        return texto
    
    try:
        if isinstance(texto, str):
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    return texto.encode('latin-1').decode(encoding)
                except:
                    continue
            return texto
        
        elif isinstance(texto, bytes):
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    return texto.decode(encoding)
                except:
                    continue
            return texto.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Erro ao limpar encoding: {e}")
        return str(texto) if texto else ""
    
    return texto

# Função para verificar autenticação
def verificar_admin():
    return session.get('admin_logged_in') == True

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not verificar_admin():
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
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
    selecionado_por = db.Column(db.String(200))
    data_selecao = db.Column(db.DateTime)
    
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

class Convidado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    whatsapp = db.Column(db.String(20))
    email = db.Column(db.String(200))
    codigo_convite = db.Column(db.String(20), unique=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Convidado {self.nome}>'

# Rotas da aplicação
@app.route('/')
def convite():
    return render_template('convite.html')

@app.route('/presentes')
def lista_presentes():
    try:
        presentes = Presente.query.filter_by(disponivel=True).all()
        return render_template('lista_presentes.html', presentes=presentes)
    except Exception as e:
        app.logger.error(f"Erro ao carregar presentes: {str(e)}")
        return render_template('lista_presentes.html', presentes=[])

@app.route('/api/selecionar-presente', methods=['POST'])
def selecionar_presente():
    try:
        data = request.get_json()
        presente_id = data.get('presente_id')
        nome_convidado = data.get('nome_convidado')
        
        if not presente_id or not nome_convidado:
            return jsonify({'success': False, 'message': 'Dados incompletos'})
        
        presente = Presente.query.get(presente_id)
        if not presente:
            return jsonify({'success': False, 'message': 'Presente não encontrado'})
        
        if not presente.disponivel or presente.selecionado_por:
            return jsonify({'success': False, 'message': 'Presente já foi selecionado'})
        
        presente.selecionado_por = nome_convidado
        presente.data_selecao = datetime.utcnow()
        presente.disponivel = False
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Presente selecionado com sucesso!',
            'link_amazon': presente.link_amazon
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao selecionar presente: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erro interno do servidor'})

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session.permanent = True
            return redirect(url_for('admin'))
        else:
            flash('Senha incorreta!')
    
    return render_template('admin_login.html')

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('convite'))

@app.route('/admin')
@login_required
def admin():
    try:
        app.logger.info("Acessando painel admin - usuário autenticado")
        
        using_postgres = 'postgresql://' in str(db.engine.url)
        app.logger.info(f"Usando banco: {'PostgreSQL' if using_postgres else 'SQLite'}")
        
        if not using_postgres:
            try:
                db.create_all()
                app.logger.info("Tabelas SQLite verificadas/criadas")
            except Exception as table_error:
                app.logger.error(f"Erro ao criar tabelas SQLite: {table_error}")
        
        try:
            presentes_raw = db.session.execute(db.text("SELECT * FROM presente")).fetchall()
            presentes = []
            for presente_row in presentes_raw:
                presente_dict = dict(presente_row._mapping)
                for campo in ['nome', 'descricao', 'categoria', 'selecionado_por']:
                    if campo in presente_dict and presente_dict[campo]:
                        presente_dict[campo] = limpar_encoding_utf8(presente_dict[campo])
                presentes.append(type('Presente', (), presente_dict))
            
            confirmacoes_raw = db.session.execute(db.text("SELECT * FROM confirmacao")).fetchall()
            confirmacoes = []
            for conf_row in confirmacoes_raw:
                conf_dict = dict(conf_row._mapping)
                for campo in ['nome_convidado', 'email', 'telefone', 'observacoes']:
                    if campo in conf_dict and conf_dict[campo]:
                        conf_dict[campo] = limpar_encoding_utf8(conf_dict[campo])
                confirmacoes.append(type('Confirmacao', (), conf_dict))
            
            presentes_selecionados = [p for p in presentes if getattr(p, 'selecionado_por', None)]
            
        except Exception as encoding_error:
            app.logger.warning(f"Erro no tratamento de encoding, tentando método tradicional: {encoding_error}")
            presentes = Presente.query.all()
            confirmacoes = Confirmacao.query.all()
            presentes_selecionados = Presente.query.filter(Presente.selecionado_por.isnot(None)).all()
        
        app.logger.info(f"Dados carregados: {len(presentes)} presentes, {len(confirmacoes)} confirmações")
        
        return render_template('admin.html', 
                             presentes=presentes, 
                             confirmacoes=confirmacoes,
                             presentes_selecionados=presentes_selecionados)
    except Exception as e:
        app.logger.error(f"Erro no painel admin: {str(e)}")
        return f"Erro no painel admin: {str(e)}. Usando banco: {str(db.engine.url).split('@')[0]}@***"

@app.route('/admin/limpar-encoding')
@login_required
def limpar_encoding_banco():
    try:
        contador_limpeza = 0
        
        presentes = Presente.query.all()
        for presente in presentes:
            alterado = False
            if presente.nome:
                nome_limpo = limpar_encoding_utf8(presente.nome)
                if nome_limpo != presente.nome:
                    presente.nome = nome_limpo
                    alterado = True
            
            if presente.descricao:
                desc_limpa = limpar_encoding_utf8(presente.descricao)
                if desc_limpa != presente.descricao:
                    presente.descricao = desc_limpa
                    alterado = True
            
            if presente.categoria:
                cat_limpa = limpar_encoding_utf8(presente.categoria)
                if cat_limpa != presente.categoria:
                    presente.categoria = cat_limpa
                    alterado = True
            
            if presente.selecionado_por:
                sel_limpo = limpar_encoding_utf8(presente.selecionado_por)
                if sel_limpo != presente.selecionado_por:
                    presente.selecionado_por = sel_limpo
                    alterado = True
            
            if alterado:
                contador_limpeza += 1
        
        confirmacoes = Confirmacao.query.all()
        for conf in confirmacoes:
            alterado = False
            if conf.nome_convidado:
                nome_limpo = limpar_encoding_utf8(conf.nome_convidado)
                if nome_limpo != conf.nome_convidado:
                    conf.nome_convidado = nome_limpo
                    alterado = True
            
            if conf.email:
                email_limpo = limpar_encoding_utf8(conf.email)
                if email_limpo != conf.email:
                    conf.email = email_limpo
                    alterado = True
            
            if conf.observacoes:
                obs_limpa = limpar_encoding_utf8(conf.observacoes)
                if obs_limpa != conf.observacoes:
                    conf.observacoes = obs_limpa
                    alterado = True
            
            if alterado:
                contador_limpeza += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Limpeza concluída! {contador_limpeza} registros foram corrigidos.',
            'registros_corrigidos': contador_limpeza
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Erro durante limpeza: {str(e)}'
        })

@app.route('/api/confirmar-presenca', methods=['POST'])
def confirmar_presenca():
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
        
        return jsonify({
            'success': True,
            'message': 'Confirmação registrada com sucesso!'
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao confirmar presença: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erro interno do servidor'})

@app.route('/api/adicionar-presente', methods=['POST'])
@login_required
def adicionar_presente():
    try:
        data = request.get_json()
        
        presente = Presente(
            nome=data.get('nome'),
            descricao=data.get('descricao'),
            preco=float(data.get('preco', 0)),
            categoria=data.get('categoria'),
            link_amazon=data.get('link_amazon')
        )
        
        db.session.add(presente)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Presente adicionado com sucesso!'})
        
    except Exception as e:
        app.logger.error(f"Erro ao adicionar presente: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erro ao adicionar presente'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', 5000))
    
    app.run(host=host, port=port, debug=False)
