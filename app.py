from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

app = Flask(__name__)

# Configuração do banco de dados PostgreSQL (Railway)
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT', 5432)


app.secret_key = os.getenv('SECRET_KEY', 'chave-padrao')

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
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );''',
        '''CREATE TABLE IF NOT EXISTS presentes (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            link VARCHAR(255) NOT NULL,
            reservado_por VARCHAR(100),
            reservado_em TIMESTAMP
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
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cur = conn.cursor()
        for comando in comandos:
            cur.execute(comando)
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

# RSVP: confirmação de presença
@app.route('/rsvp', methods=['GET', 'POST'])
def rsvp():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        mensagem = request.form.get('mensagem')
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute('INSERT INTO convidados (nome, email, telefone, confirmado, mensagem) VALUES (%s, %s, %s, %s, %s)',
                        (nome, email, telefone, True, mensagem))
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

# Painel admin
@app.route('/painel')
def admin_panel():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin.html')

# Logout admin
@app.route('/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    criar_tabelas()
    app.run(debug=True)
