#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Cadastro de Produtos com Dashboard Gerencial
Flask + SQLite + Backup Automático
Nome do Solicitante: Gestor da Filial Norte
"""

import sqlite3
import os
import shutil
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages

app = Flask(__name__)
app.secret_key = 'sistema_produtos_secret_key_2024'

# Configuração do banco de dados
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dbfilialnorte.db')
BACKUP_DIR = 'C:/BKP_BANCO'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL DEFAULT 0,
            fornecedor TEXT NOT NULL,
            validade DATE,
            vendido INTEGER NOT NULL DEFAULT 0,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_nome ON produtos(nome)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_categoria ON produtos(categoria)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fornecedor ON produtos(fornecedor)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_validade ON produtos(validade)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_vendido ON produtos(vendido)')
    conn.commit()
    conn.close()

def criar_backup():
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        if not os.path.exists(DATABASE):
            return False
        timestamp = datetime.now().strftime('%d%m%Y%H%M')
        backup_name = f'BKP-{timestamp}.db'
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        shutil.copy2(DATABASE, backup_path)
        return True
    except Exception as e:
        print(f'Erro no backup: {e}')
        return False

def schedule_backups():
    import threading
    def backup_thread():
        while True:
            now = datetime.now()
            if now.hour < 6:
                next_run = now.replace(hour=6, minute=0, second=0, microsecond=0)
            elif now.hour < 18:
                next_run = now.replace(hour=18, minute=0, second=0, microsecond=0)
            else:
                next_run = (now + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)
            sleep_seconds = (next_run - now).total_seconds()
            if sleep_seconds > 0:
                import time
                time.sleep(sleep_seconds)
            if criar_backup():
                print(f'Backup realizado: {datetime.now().strftime("%d/%m/%Y %H:%M")}')
    thread = threading.Thread(target=backup_thread, daemon=True)
    thread.start()

@app.route('/')
def dashboard():
    conn = get_db_connection()
    total_produtos = conn.execute('SELECT COUNT(*) FROM produtos').fetchone()[0]
    total_unidades = conn.execute('SELECT SUM(quantidade) FROM produtos').fetchone()[0] or 0
    valor_total = conn.execute('SELECT SUM(preco * quantidade) FROM produtos').fetchone()[0] or 0
    estoque_baixo = conn.execute('SELECT COUNT(*) FROM produtos WHERE quantidade <= 10').fetchone()[0]
    hoje = datetime.now().strftime('%Y-%m-%d')
    produtos_vencidos = conn.execute('SELECT COUNT(*) FROM produtos WHERE validade IS NOT NULL AND validade < ?', (hoje,)).fetchone()[0]
    produtos_baixo = conn.execute('SELECT nome, quantidade FROM produtos WHERE quantidade <= 10').fetchall()
    produtos_vencidos_list = conn.execute('SELECT nome, validade FROM produtos WHERE validade IS NOT NULL AND validade < ?', (hoje,)).fetchall()
    top_vendidos = conn.execute('SELECT nome, vendido FROM produtos ORDER BY vendido DESC LIMIT 5').fetchall()
    categoria_stats = conn.execute('SELECT categoria, COUNT(*) as total, SUM(preco * quantidade) as valor FROM produtos GROUP BY categoria ORDER BY total DESC LIMIT 5').fetchall()
    vendas_categoria = conn.execute('SELECT categoria, SUM(vendido) as total_vendas FROM produtos GROUP BY categoria ORDER BY total_vendas DESC LIMIT 5').fetchall()
    conn.close()
    return render_template('index.html',
                         total_produtos=total_produtos, total_unidades=total_unidades,
                         valor_total=valor_total, estoque_baixo=estoque_baixo,
                         produtos_vencidos=produtos_vencidos,
                         produtos_baixo=produtos_baixo, produtos_vencidos_list=produtos_vencidos_list,
                         top_vendidos=top_vendidos, categoria_stats=categoria_stats,
                         vendas_categoria=vendas_categoria, lazy_mode=True)

@app.route('/produtos')
def listar_produtos():
    termo_pesquisa = request.args.get('pesquisa', '')
    conn = get_db_connection()
    if termo_pesquisa:
        produtos = conn.execute('SELECT * FROM produtos WHERE nome LIKE ? OR categoria LIKE ? OR fornecedor LIKE ? ORDER BY nome',
                              (f'%{termo_pesquisa}%', f'%{termo_pesquisa}%', f'%{termo_pesquisa}%')).fetchall()
    else:
        produtos = conn.execute('SELECT * FROM produtos ORDER BY nome').fetchall()
    conn.close()
    return render_template('produtos.html', produtos=produtos, termo_pesquisa=termo_pesquisa)

@app.route('/produto/novo', methods=['GET', 'POST'])
def novo_produto():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        categoria = request.form.get('categoria', '').strip()
        preco = request.form.get('preco', '').strip()
        quantidade = request.form.get('quantidade', '').strip()
        fornecedor = request.form.get('fornecedor', '').strip()
        validade = request.form.get('validade', '').strip()
        erros = []
        if not nome:
            erros.append('O nome do produto é obrigatório.')
        elif len(nome) < 3:
            erros.append('O nome deve ter pelo menos 3 caracteres.')
        if not categoria:
            erros.append('A categoria é obrigatória.')
        try:
            preco_valor = float(preco.replace(',', '.'))
            if preco_valor <= 0:
                erros.append('O preço deve ser maior que zero.')
        except (ValueError, TypeError):
            erros.append('O preço deve ser um número válido.')
        try:
            quantidade_valor = int(quantidade)
            if quantidade_valor < 0:
                erros.append('A quantidade não pode ser negativa.')
        except (ValueError, TypeError):
            erros.append('A quantidade deve ser um número inteiro válido.')
        if not fornecedor:
            erros.append('O fornecedor é obrigatório.')
        if validade:
            try:
                datetime.strptime(validade, '%Y-%m-%d')
            except ValueError:
                erros.append('Data de validade inválida. Use o formato AAAA-MM-DD.')
        if erros:
            for erro in erros:
                flash(erro, 'error')
            return render_template('formulario.html', produto=None, acao='cadastrar')
        conn = get_db_connection()
        conn.execute('INSERT INTO produtos (nome, categoria, preco, quantidade, fornecedor, validade) VALUES (?, ?, ?, ?, ?, ?)',
                    (nome, categoria, preco_valor, quantidade_valor, fornecedor, validade or None))
        conn.commit()
        conn.close()
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_produtos'))
    return render_template('formulario.html', produto=None, acao='cadastrar')

@app.route('/produto/editar/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    conn = get_db_connection()
    produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
    if not produto:
        flash('Produto não encontrado.', 'error')
        conn.close()
        return redirect(url_for('listar_produtos'))
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        categoria = request.form.get('categoria', '').strip()
        preco = request.form.get('preco', '').strip()
        quantidade = request.form.get('quantidade', '').strip()
        fornecedor = request.form.get('fornecedor', '').strip()
        validade = request.form.get('validade', '').strip()
        erros = []
        if not nome:
            erros.append('O nome do produto é obrigatório.')
        elif len(nome) < 3:
            erros.append('O nome deve ter pelo menos 3 caracteres.')
        if not categoria:
            erros.append('A categoria é obrigatória.')
        try:
            preco_valor = float(preco.replace(',', '.'))
            if preco_valor <= 0:
                erros.append('O preço deve ser maior que zero.')
        except (ValueError, TypeError):
            erros.append('O preço deve ser um número válido.')
        try:
            quantidade_valor = int(quantidade)
            if quantidade_valor < 0:
                erros.append('A quantidade não pode ser negativa.')
        except (ValueError, TypeError):
            erros.append('A quantidade deve ser um número inteiro válido.')
        if not fornecedor:
            erros.append('O fornecedor é obrigatório.')
        if validade:
            try:
                datetime.strptime(validade, '%Y-%m-%d')
            except ValueError:
                erros.append('Data de validade inválida. Use o formato AAAA-MM-DD.')
        if erros:
            for erro in erros:
                flash(erro, 'error')
            conn.close()
            return render_template('formulario.html', produto=produto, acao='editar')
        conn.execute('UPDATE produtos SET nome=?, categoria=?, preco=?, quantidade=?, fornecedor=?, validade=?, atualizado_em=CURRENT_TIMESTAMP WHERE id=?',
                    (nome, categoria, preco_valor, quantidade_valor, fornecedor, validade or None, id))
        conn.commit()
        conn.close()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('listar_produtos'))
    conn.close()
    return render_template('formulario.html', produto=produto, acao='editar')

@app.route('/produto/vender/<int:id>', methods=['POST'])
def vender_produto(id):
    conn = get_db_connection()
    produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
    if not produto:
        flash('Produto não encontrado.', 'error')
        conn.close()
        return redirect(url_for('listar_produtos'))
    if produto['quantidade'] <= 0:
        flash('Produto sem estoque!', 'error')
        conn.close()
        return redirect(url_for('listar_produtos'))
    conn.execute('UPDATE produtos SET quantidade = quantidade - 1, vendido = vendido + 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Venda registrada com sucesso!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/produto/excluir/<int:id>', methods=['POST'])
def excluir_produto(id):
    conn = get_db_connection()
    produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
    if not produto:
        flash('Produto não encontrado.', 'error')
        conn.close()
        return redirect(url_for('listar_produtos'))
    conn.execute('DELETE FROM produtos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Produto excluído com sucesso!', 'success')
    return redirect(url_for('listar_produtos'))

init_db()
schedule_backups()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8009)
