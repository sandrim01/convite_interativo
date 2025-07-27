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
    # Campos para controle de seleção
    selecionado_por = db.Column(db.String(200))  # Nome do convidado que selecionou
    data_selecao = db.Column(db.DateTime)        # Quando foi selecionado
    
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
    # Relacionamento com convidado (temporariamente comentado)
    # convidado_id = db.Column(db.Integer, db.ForeignKey('convidado.id'))
    
    def __repr__(self):
        return f'<Confirmacao {self.nome_convidado}>'

class Convidado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    whatsapp = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(200))
    codigo_convite = db.Column(db.String(50), unique=True, nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ja_confirmou = db.Column(db.Boolean, default=False)
    status_resposta = db.Column(db.String(20), default='pendente')  # 'pendente', 'convite_enviado', 'confirmado', 'nao_comparecera'
    convite_enviado = db.Column(db.Boolean, default=False)  # Se o convite foi enviado por WhatsApp
    data_envio_convite = db.Column(db.DateTime)  # Quando o convite foi enviado
    data_ultima_visita = db.Column(db.DateTime)
    
    # Relacionamentos (temporariamente comentado)
    # confirmacoes = db.relationship('Confirmacao', backref='convidado', lazy=True)
    
    def __repr__(self):
        return f'<Convidado {self.nome}>'
    
    def gerar_codigo_convite(self):
        """Gera um código único para o convite"""
        base = f"{self.nome}_{self.whatsapp or self.email}_{datetime.utcnow().isoformat()}"
        self.codigo_convite = hashlib.md5(base.encode()).hexdigest()[:12].upper()
        return self.codigo_convite

# Rotas da aplicação
@app.route('/')
def convite():
    """Página principal do convite interativo"""
    codigo = request.args.get('codigo')
    
    # Se não tem código, mostrar tela de identificação
    if not codigo:
        return render_template('convite.html', convidado=None)
    
    # Buscar convidado pelo código
    convidado = Convidado.query.filter_by(codigo_convite=codigo).first()
    
    # Se código inválido, mostrar tela de identificação
    if not convidado:
        return render_template('convite.html', convidado=None, erro_codigo=True)
    
    # Atualizar última visita
    convidado.data_ultima_visita = datetime.utcnow()
    db.session.commit()
    
    # Se já respondeu, verificar o tipo de resposta
    if convidado.ja_confirmou:
        if convidado.status_resposta == 'confirmado':
            return redirect(url_for('resumo_convite', codigo=codigo))
        elif convidado.status_resposta == 'nao_comparecera':
            return render_template('convite.html', convidado=convidado, abrir_mensagem_final=True)
    
    # Primeira visita ou ainda não confirmou - mostrar convite completo
    return render_template('convite.html', convidado=convidado)

@app.route('/resumo/<codigo>')
def resumo_convite(codigo):
    """Página de resumo para convidados que já confirmaram"""
    convidado = Convidado.query.filter_by(codigo_convite=codigo).first()
    if not convidado or not convidado.ja_confirmou:
        return redirect(url_for('convite', codigo=codigo))
    
    # Buscar confirmação por nome (temporário, enquanto não temos relacionamento)
    confirmacao = Confirmacao.query.filter_by(nome_convidado=convidado.nome).first()
    presentes_selecionados = Presente.query.filter_by(selecionado_por=convidado.nome).all()
    
    return render_template('resumo.html', 
                         convidado=convidado, 
                         confirmacao=confirmacao,
                         presentes_selecionados=presentes_selecionados)

@app.route('/identificar_convidado', methods=['POST'])
def identificar_convidado():
    """Rota para identificar convidado por nome ou WhatsApp"""
    try:
        data = request.get_json()
        identificador = data.get('identificador', '').strip()
        
        if not identificador:
            return jsonify({
                'success': False,
                'message': 'Por favor, informe seu nome ou WhatsApp'
            })
        
        # Buscar por WhatsApp (apenas números)
        whatsapp_limpo = ''.join(filter(str.isdigit, identificador))
        convidado = None
        
        if len(whatsapp_limpo) >= 10:  # Se parece com WhatsApp
            convidado = Convidado.query.filter_by(whatsapp=whatsapp_limpo).first()
        
        # Se não encontrou por WhatsApp, buscar por nome
        if not convidado:
            convidado = Convidado.query.filter(
                Convidado.nome.ilike(f'%{identificador}%')
            ).first()
        
        if convidado:
            return jsonify({
                'success': True,
                'codigo': convidado.codigo_convite,
                'nome': convidado.nome,
                'ja_confirmou': convidado.ja_confirmou
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Convidado não encontrado. Verifique o nome ou WhatsApp informado.'
            })
            
    except Exception as e:
        app.logger.error(f"Erro ao identificar convidado: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro interno. Tente novamente.'
        })

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

@app.route('/selecionar_presente', methods=['POST'])
def selecionar_presente():
    """Rota para selecionar um presente"""
    try:
        data = request.get_json()
        presente_id = data.get('presente_id')
        nome_convidado = data.get('nome_convidado')
        
        if not presente_id or not nome_convidado:
            return jsonify({'success': False, 'message': 'Dados incompletos'})
        
        presente = Presente.query.get(presente_id)
        if not presente:
            return jsonify({'success': False, 'message': 'Presente não encontrado'})
        
        if presente.selecionado_por:
            return jsonify({'success': False, 'message': 'Este presente já foi selecionado por outro convidado'})
        
        # Marcar presente como selecionado
        presente.selecionado_por = nome_convidado
        presente.data_selecao = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Presente selecionado com sucesso por {nome_convidado}!'})
        
    except Exception as e:
        app.logger.error(f"Erro ao selecionar presente: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'})

# Rota alternativa para contornar problemas de cache
@app.route('/presentes')
def presentes():
    """Rota alternativa para lista de presentes"""
    return lista_presentes()

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
    presentes_selecionados = Presente.query.filter(Presente.selecionado_por.isnot(None)).all()
    return render_template('admin.html', 
                         presentes=presentes, 
                         confirmacoes=confirmacoes,
                         presentes_selecionados=presentes_selecionados)

@app.route('/api/confirmar-presenca', methods=['POST'])
def confirmar_presenca():
    """API para confirmar presença"""
    try:
        data = request.get_json()
        codigo_convite = data.get('codigo_convite')
        
        # Buscar convidado se tiver código
        convidado = None
        if codigo_convite:
            convidado = Convidado.query.filter_by(codigo_convite=codigo_convite).first()
        
        confirmacao = Confirmacao(
            nome_convidado=data.get('nome'),
            email=data.get('email'),
            telefone=data.get('telefone'),
            confirmou_presenca=data.get('confirmou_presenca', False),
            numero_acompanhantes=data.get('acompanhantes', 0),
            observacoes=data.get('observacoes', '')
            # convidado_id=convidado.id if convidado else None  # Temporariamente comentado
        )
        
        db.session.add(confirmacao)
        
        # Se é um convidado cadastrado, atualizar status baseado na resposta
        if convidado:
            confirmou_presenca = data.get('confirmou_presenca', False)
            if confirmou_presenca:
                convidado.ja_confirmou = True
                convidado.status_resposta = 'confirmado'
            else:
                convidado.ja_confirmou = True  # Já respondeu
                convidado.status_resposta = 'nao_comparecera'
        
        db.session.commit()
        
        response_data = {'success': True, 'message': 'Confirmação enviada com sucesso!'}
        if convidado:
            response_data['codigo'] = convidado.codigo_convite
            response_data['ja_confirmou'] = convidado.ja_confirmou
            response_data['status_resposta'] = convidado.status_resposta
        
        return jsonify(response_data)
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

@app.route('/api/cadastrar-convidado', methods=['POST'])
@login_required
def cadastrar_convidado():
    """API para cadastrar novo convidado"""
    try:
        data = request.get_json()
        nome = data.get('nome', '').strip()
        whatsapp = data.get('whatsapp', '').strip()
        email = data.get('email', '').strip()
        
        app.logger.info(f"Tentando cadastrar: {nome}, WhatsApp: {whatsapp}")
        
        if not nome:
            return jsonify({'success': False, 'message': 'Nome é obrigatório'})
        
        # Limpar WhatsApp (apenas números)
        if whatsapp:
            whatsapp = ''.join(filter(str.isdigit, whatsapp))
            if len(whatsapp) < 10:
                return jsonify({'success': False, 'message': 'WhatsApp deve ter pelo menos 10 dígitos'})
        
        # Verificar se já existe
        if whatsapp and Convidado.query.filter_by(whatsapp=whatsapp).first():
            return jsonify({'success': False, 'message': 'WhatsApp já cadastrado'})
        
        # Gerar código do convite antes de criar o objeto
        import hashlib
        base = f"{nome}_{whatsapp or email}_{datetime.utcnow().isoformat()}"
        codigo_convite = hashlib.md5(base.encode()).hexdigest()[:12].upper()
        
        app.logger.info(f"Código gerado: {codigo_convite}")
        
        # Criar convidado com código já gerado
        convidado = Convidado(
            nome=nome,
            whatsapp=whatsapp if whatsapp else None,
            email=email if email else None,
            codigo_convite=codigo_convite
        )
        
        app.logger.info("Adicionando convidado ao banco...")
        db.session.add(convidado)
        db.session.commit()
        app.logger.info("Convidado salvo no banco!")
        
        return jsonify({
            'success': True, 
            'message': 'Convidado cadastrado com sucesso!',
            'codigo': convidado.codigo_convite,
            'link': url_for('convite', codigo=convidado.codigo_convite, _external=True)
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao cadastrar convidado: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/listar-convidados')
@login_required
def listar_convidados():
    """API para listar todos os convidados"""
    try:
        convidados = Convidado.query.order_by(Convidado.data_cadastro.desc()).all()
        lista = []
        
        for conv in convidados:
            # Buscar confirmação por nome (temporário, enquanto não temos relacionamento)
            confirmacao = Confirmacao.query.filter_by(nome_convidado=conv.nome).first()
            lista.append({
                'id': conv.id,
                'nome': conv.nome,
                'whatsapp': conv.whatsapp,
                'email': conv.email,
                'codigo_convite': conv.codigo_convite,
                'ja_confirmou': conv.ja_confirmou,
                'status_resposta': conv.status_resposta,
                'convite_enviado': conv.convite_enviado,
                'data_envio_convite': conv.data_envio_convite.strftime('%d/%m/%Y %H:%M') if conv.data_envio_convite else '',
                'data_cadastro': conv.data_cadastro.strftime('%d/%m/%Y %H:%M') if conv.data_cadastro else '',
                'data_ultima_visita': conv.data_ultima_visita.strftime('%d/%m/%Y %H:%M') if conv.data_ultima_visita else 'Nunca',
                'link_convite': url_for('convite', codigo=conv.codigo_convite, _external=True),
                'confirmou_presenca': confirmacao.confirmou_presenca if confirmacao else False,
                'acompanhantes': confirmacao.numero_acompanhantes if confirmacao else 0
            })
        
        return jsonify({'success': True, 'convidados': lista})
        
    except Exception as e:
        app.logger.error(f"Erro ao listar convidados: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/gerar-links-whatsapp', methods=['POST'])
@login_required
def gerar_links_whatsapp():
    """Gera links do WhatsApp para envio em massa - apenas convidados pendentes"""
    try:
        # Buscar apenas convidados com status 'pendente' (convite não enviado)
        convidados = Convidado.query.filter_by(status_resposta='pendente').all()
        
        if not convidados:
            return jsonify({
                'success': False, 
                'message': 'Não há convidados pendentes para enviar convites'
            })
        
        links_whatsapp = []
        base_url = request.host_url.rstrip('/')
        
        for convidado in convidados:
            if convidado.whatsapp:
                # Limpar número de WhatsApp (remover caracteres especiais)
                whatsapp_limpo = ''.join(filter(str.isdigit, convidado.whatsapp))
                
                # Se não começar com 55, adicionar código do Brasil
                if not whatsapp_limpo.startswith('55'):
                    whatsapp_limpo = '55' + whatsapp_limpo
                
                # Mensagem personalizada
                link_convite = f"{base_url}/?codigo={convidado.codigo_convite}"
                mensagem = f"""Olá {convidado.nome}! 💕

Samuel & Iara têm o prazer de convidá-lo(a) para celebrar nossa união! 

🎊 Acesse seu convite personalizado:
{link_convite}

Esperamos você em nosso grande dia! ❤️"""
                
                # Codificar mensagem para URL
                mensagem_codificada = quote(mensagem)
                
                # Gerar link do WhatsApp
                link_whatsapp = f"https://wa.me/{whatsapp_limpo}?text={mensagem_codificada}"
                
                links_whatsapp.append({
                    'id': convidado.id,
                    'nome': convidado.nome,
                    'whatsapp': convidado.whatsapp,
                    'whatsapp_limpo': whatsapp_limpo,
                    'link_whatsapp': link_whatsapp,
                    'link_convite': link_convite
                })
        
        return jsonify({
            'success': True,
            'total': len(links_whatsapp),
            'links': links_whatsapp,
            'message': f'{len(links_whatsapp)} convites pendentes encontrados'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@app.route('/api/enviar-whatsapp-automatico', methods=['POST'])
@login_required
def enviar_whatsapp_automatico():
    """Marca todos os convidados pendentes como 'convite_enviado' automaticamente"""
    try:
        data = request.get_json()
        ids_convidados = data.get('ids_convidados', [])
        
        if not ids_convidados:
            return jsonify({
                'success': False,
                'message': 'Nenhum convidado especificado'
            })
        
        # Atualizar status dos convidados especificados
        convidados_atualizados = Convidado.query.filter(
            Convidado.id.in_(ids_convidados),
            Convidado.status_resposta == 'pendente'
        ).all()
        
        total_atualizados = 0
        for convidado in convidados_atualizados:
            convidado.status_resposta = 'convite_enviado'
            total_atualizados += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'total_atualizados': total_atualizados,
            'message': f'{total_atualizados} convites marcados como enviados automaticamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@app.route('/api/enviar-whatsapp-individual', methods=['POST'])
@login_required
def enviar_whatsapp_individual():
    """Gera link individual do WhatsApp para um convidado específico"""
    try:
        data = request.get_json()
        convidado_id = data.get('convidado_id')
        
        if not convidado_id:
            return jsonify({
                'success': False,
                'message': 'ID do convidado não especificado'
            })
        
        convidado = Convidado.query.get(convidado_id)
        if not convidado:
            return jsonify({
                'success': False,
                'message': 'Convidado não encontrado'
            })
        
        if not convidado.whatsapp:
            return jsonify({
                'success': False,
                'message': 'Convidado não possui WhatsApp cadastrado'
            })
        
        # Limpar número de WhatsApp
        whatsapp_limpo = ''.join(filter(str.isdigit, convidado.whatsapp))
        if not whatsapp_limpo.startswith('55'):
            whatsapp_limpo = '55' + whatsapp_limpo
        
        # Gerar mensagem e link
        base_url = request.host_url.rstrip('/')
        link_convite = f"{base_url}/?codigo={convidado.codigo_convite}"
        mensagem = f"""Olá {convidado.nome}! 💕

Samuel & Iara têm o prazer de convidá-lo(a) para celebrar nossa união! 

🎊 Acesse seu convite personalizado:
{link_convite}

Esperamos você em nosso grande dia! ❤️"""
        
        mensagem_codificada = quote(mensagem)
        link_whatsapp = f"https://wa.me/{whatsapp_limpo}?text={mensagem_codificada}"
        
        return jsonify({
            'success': True,
            'link_whatsapp': link_whatsapp,
            'nome_convidado': convidado.nome,
            'whatsapp': convidado.whatsapp
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@app.route('/api/marcar-convite-enviado', methods=['POST'])
@login_required
def marcar_convite_enviado():
    """Marca um convite como enviado"""
    try:
        data = request.get_json()
        convidado_id = data.get('convidado_id')
        
        convidado = Convidado.query.get(convidado_id)
        if not convidado:
            return jsonify({'success': False, 'message': 'Convidado não encontrado'})
        
        convidado.convite_enviado = True
        convidado.data_envio_convite = datetime.utcnow()
        if convidado.status_resposta == 'pendente':
            convidado.status_resposta = 'convite_enviado'
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Convite marcado como enviado para {convidado.nome}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@app.route('/api/marcar-todos-enviados', methods=['POST'])
@login_required
def marcar_todos_enviados():
    """Marca todos os convites como enviados"""
    try:
        convidados = Convidado.query.filter_by(convite_enviado=False).all()
        
        for convidado in convidados:
            convidado.convite_enviado = True
            convidado.data_envio_convite = datetime.utcnow()
            if convidado.status_resposta == 'pendente':
                convidado.status_resposta = 'convite_enviado'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{len(convidados)} convites marcados como enviados'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@app.route('/api/excluir-convidado/<int:convidado_id>', methods=['DELETE'])
@login_required
def excluir_convidado(convidado_id):
    """API para excluir um convidado do banco de dados"""
    try:
        convidado = Convidado.query.get(convidado_id)
        if not convidado:
            return jsonify({'success': False, 'message': 'Convidado não encontrado'})
        
        nome_convidado = convidado.nome
        
        # Excluir confirmações relacionadas (se existirem)
        confirmacoes_relacionadas = Confirmacao.query.filter_by(nome_convidado=nome_convidado).all()
        for confirmacao in confirmacoes_relacionadas:
            db.session.delete(confirmacao)
        
        # Limpar presentes selecionados por este convidado
        presentes_selecionados = Presente.query.filter_by(selecionado_por=nome_convidado).all()
        for presente in presentes_selecionados:
            presente.selecionado_por = None
            presente.data_selecao = None
        
        # Excluir o convidado
        db.session.delete(convidado)
        db.session.commit()
        
        app.logger.info(f"Convidado {nome_convidado} excluído do banco de dados")
        
        return jsonify({
            'success': True, 
            'message': f'Convidado {nome_convidado} excluído com sucesso!'
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao excluir convidado: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao excluir: {str(e)}'}), 500

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
