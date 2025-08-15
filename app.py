from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
from dotenv import load_dotenv
import psycopg2
import uuid
import hashlib

load_dotenv()

app = Flask(__name__)

# Configuração do banco de dados PostgreSQL (Railway)
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT', 5432)


app.secret_key = os.getenv('SECRET_KEY', 'chave-padrao')

# Função para gerar link único do convidado
def gerar_link_convite(nome, email=None):
    """Gera um link único para o convidado baseado no nome e timestamp"""
    base_string = f"{nome}_{email or ''}_{uuid.uuid4().hex[:8]}"
    hash_object = hashlib.md5(base_string.encode())
    return hash_object.hexdigest()[:12]

# Função para obter conexão
def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
def criar_tabelas():
    comandos = [
        '''CREATE TABLE IF NOT EXISTS convidados (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(120),
            telefone VARCHAR(20),
            confirmado BOOLEAN DEFAULT FALSE,
            mensagem TEXT,
            link_convite VARCHAR(100) UNIQUE,
            convite_enviado BOOLEAN DEFAULT FALSE,
            enviado_em TIMESTAMP,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );''',
        '''CREATE TABLE IF NOT EXISTS presentes (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            link VARCHAR(255) NOT NULL,
            reservado_por VARCHAR(100),
            reservado_em TIMESTAMP,
            descricao TEXT,
            preco DECIMAL(10,2),
            categoria VARCHAR(50) DEFAULT 'Outros'
        );''',
        '''CREATE TABLE IF NOT EXISTS admin (
            id SERIAL PRIMARY KEY,
            usuario VARCHAR(50) NOT NULL,
            senha VARCHAR(255) NOT NULL
        );''',
        '''INSERT INTO admin (usuario, senha) 
           SELECT 'admin', 'casamento2024' 
           WHERE NOT EXISTS (SELECT 1 FROM admin WHERE usuario = 'admin');'''
    ]
    
    # Comandos de migração para adicionar colunas que podem não existir
    migracoes = [
        '''ALTER TABLE convidados ADD COLUMN IF NOT EXISTS link_convite VARCHAR(100) UNIQUE;''',
        '''ALTER TABLE convidados ADD COLUMN IF NOT EXISTS convite_enviado BOOLEAN DEFAULT FALSE;''',
        '''ALTER TABLE convidados ADD COLUMN IF NOT EXISTS enviado_em TIMESTAMP;''',
        '''ALTER TABLE convidados ADD COLUMN IF NOT EXISTS criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP;'''
    ]
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cur = conn.cursor()
        
        # Executar criação de tabelas
        for comando in comandos:
            cur.execute(comando)
        
        # Executar migrações
        for migracao in migracoes:
            try:
                cur.execute(migracao)
            except Exception as e:
                print(f"Migração já aplicada ou erro: {e}")
        
        conn.commit()
        cur.close()
        conn.close()
        print("Tabelas criadas/verificadas com sucesso.")
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")


# Rota principal: convite interativo
@app.route('/')
def convite():
    maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
    latitude = -23.55052
    longitude = -46.633308
    nome_local = 'Espaço de Eventos'
    endereco = 'Rua das Flores, 123 - Centro, São Paulo - SP'
    return render_template('convite.html', maps_api_key=maps_api_key, latitude=latitude, longitude=longitude, nome_local=nome_local, endereco=endereco)

# Rota de convite personalizado
@app.route('/convite/<link_convite>')
def convite_personalizado(link_convite):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT nome, email FROM convidados WHERE link_convite = %s", (link_convite,))
        convidado = cur.fetchone()
        cur.close()
        conn.close()
        
        if not convidado:
            # Se não encontrar o link, redireciona para convite geral
            return redirect(url_for('convite'))
        
        nome_convidado = convidado[0]
        email_convidado = convidado[1]
        
        maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
        latitude = -23.55052
        longitude = -46.633308
        nome_local = 'Espaço de Eventos'
        endereco = 'Rua das Flores, 123 - Centro, São Paulo - SP'
        
        return render_template('convite.html', 
                             maps_api_key=maps_api_key, 
                             latitude=latitude, 
                             longitude=longitude, 
                             nome_local=nome_local, 
                             endereco=endereco,
                             nome_convidado=nome_convidado,
                             email_convidado=email_convidado,
                             link_convite=link_convite)
    except Exception as e:
        print(f"Erro ao carregar convite personalizado: {e}")
        return redirect(url_for('convite'))

# RSVP: confirmação de presença
@app.route('/rsvp', methods=['GET', 'POST'])
def rsvp():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        mensagem = request.form.get('mensagem')
        link_convite = request.form.get('link_convite')  # Para convites personalizados
        
        try:
            conn = get_conn()
            cur = conn.cursor()
            
            if link_convite:
                # Atualizar convidado existente
                cur.execute(
                    """UPDATE convidados 
                       SET email = COALESCE(%s, email), 
                           telefone = COALESCE(%s, telefone), 
                           confirmado = TRUE, 
                           mensagem = %s 
                       WHERE link_convite = %s""",
                    (email, telefone, mensagem, link_convite)
                )
                if cur.rowcount == 0:
                    # Se não encontrou o link, criar novo convidado
                    link_novo = gerar_link_convite(nome, email)
                    cur.execute(
                        'INSERT INTO convidados (nome, email, telefone, confirmado, mensagem, link_convite) VALUES (%s, %s, %s, %s, %s, %s)',
                        (nome, email, telefone, True, mensagem, link_novo)
                    )
            else:
                # Criar novo convidado (convite geral)
                link_novo = gerar_link_convite(nome, email)
                cur.execute(
                    'INSERT INTO convidados (nome, email, telefone, confirmado, mensagem, link_convite) VALUES (%s, %s, %s, %s, %s, %s)',
                    (nome, email, telefone, True, mensagem, link_novo)
                )
            
            conn.commit()
            cur.close()
            conn.close()
            flash('Confirmação registrada com sucesso!', 'success')
        except Exception as e:
            flash('Erro ao registrar confirmação: ' + str(e), 'danger')
        return redirect(url_for('rsvp'))
    return render_template('rsvp.html')


# Lista de presentes e reserva
@app.route('/presentes', methods=['GET', 'POST'])
def presentes():
    if request.method == 'POST':
        presente_id = request.form.get('presente_id')
        nome_reserva = request.form.get('nome_reserva')
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute('UPDATE presentes SET reservado_por = %s, reservado_em = NOW() WHERE id = %s AND reservado_por IS NULL', (nome_reserva, presente_id))
            if cur.rowcount == 0:
                flash('Este presente já foi reservado por outra pessoa.', 'danger')
            else:
                conn.commit()
                flash('Presente reservado com sucesso! Obrigado pelo carinho.', 'success')
            cur.close()
            conn.close()
        except Exception as e:
            flash('Erro ao reservar presente: ' + str(e), 'danger')
        return redirect(url_for('presentes'))
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('SELECT id, nome, link, reservado_por FROM presentes ORDER BY id')
        presentes = [
            {'id': row[0], 'nome': row[1], 'link': row[2], 'reservado_por': row[3]} for row in cur.fetchall()
        ]
        cur.close()
        conn.close()
    except Exception as e:
        presentes = []
        flash('Erro ao carregar lista de presentes: ' + str(e), 'danger')
    return render_template('lista_presentes.html', presentes=presentes)

# Login admin
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        senha = request.form.get('senha')
        # Usar senha simples sem usuário para facilitar acesso
        if senha == 'casamento2024':
            session['admin'] = 'admin'
            return redirect(url_for('admin_panel'))
        else:
            flash('Senha inválida.', 'danger')
    return render_template('admin_login.html')

# API para adicionar convidado
@app.route('/api/adicionar-convidado', methods=['POST'])
def api_adicionar_convidado():
    if 'admin' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    data = request.get_json()
    nome = data.get('nome', '').strip()
    email = data.get('email', '').strip()
    telefone = data.get('telefone', '').strip()
    
    if not nome:
        return jsonify({'success': False, 'message': 'Nome é obrigatório'})
    
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        # Gerar link único para o convidado
        link_convite = gerar_link_convite(nome, email)
        
        # Verificar se já existe convidado com mesmo nome
        cur.execute("SELECT id FROM convidados WHERE nome ILIKE %s", (nome,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Já existe um convidado com este nome'})
        
        # Inserir novo convidado
        cur.execute(
            """INSERT INTO convidados (nome, email, telefone, link_convite) 
               VALUES (%s, %s, %s, %s) RETURNING id""",
            (nome, email if email else None, telefone if telefone else None, link_convite)
        )
        convidado_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        # Construir URL completo do convite
        convite_url = request.url_root + f'convite/{link_convite}'
        
        return jsonify({
            'success': True, 
            'message': f'Convidado {nome} adicionado com sucesso!',
            'convidado': {
                'id': convidado_id,
                'nome': nome,
                'email': email,
                'telefone': telefone,
                'link_convite': convite_url
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao adicionar convidado: {str(e)}'})

# API para adicionar presente
@app.route('/api/adicionar-presente', methods=['POST'])
def api_adicionar_presente():
    if 'admin' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    data = request.get_json()
    nome = data.get('nome')
    descricao = data.get('descricao')
    preco = data.get('preco')
    categoria = data.get('categoria')
    link_amazon = data.get('link_amazon')
    
    if not nome or not categoria or not link_amazon:
        return jsonify({'success': False, 'message': 'Campos obrigatórios não preenchidos'})
    
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO presentes (nome, descricao, preco, categoria, link) VALUES (%s, %s, %s, %s, %s)",
            (nome, descricao, preco, categoria, link_amazon)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Presente adicionado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao adicionar presente: {str(e)}'})

# Painel admin
@app.route('/painel')
def admin_panel():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    # Buscar convidados e presentes
    conn = get_conn()
    cur = conn.cursor()
    
    # Buscar convidados
    cur.execute("SELECT * FROM convidados ORDER BY criado_em DESC")
    convidados = cur.fetchall()
    
    # Buscar presentes
    cur.execute("SELECT * FROM presentes ORDER BY id")
    presentes = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Converter para dicionários
    convidados_dict = []
    for c in convidados:
        convidados_dict.append({
            'id': c[0],
            'nome': c[1],
            'email': c[2],
            'telefone': c[3],
            'confirmado': c[4],
            'mensagem': c[5],
            'criado_em': c[6]
        })
    
    presentes_dict = []
    for p in presentes:
        presentes_dict.append({
            'id': p[0],
            'nome': p[1],
            'link': p[2],
            'reservado_por': p[3],
            'reservado_em': p[4],
            'descricao': p[5] if len(p) > 5 else '',
            'preco': p[6] if len(p) > 6 else 0,
            'categoria': p[7] if len(p) > 7 else 'Outros'
        })
    
    return render_template('admin.html', convidados=convidados_dict, presentes=presentes_dict)

# Logout admin
@app.route('/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    criar_tabelas()
    app.run(debug=True)
