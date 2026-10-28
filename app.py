#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Cadastro de Produtos com Dashboard Gerencial
Flask + SQLite
"""

import sqlite3
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'sistema_produtos_secret_key_2024'

# Configuração do banco de dados
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'produtos.db')

def get_db_connection():
    """Cria conexão com o banco de dados SQLite"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa o banco de dados com a tabela de produtos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Cria a tabela de produtos se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL DEFAULT 0,
            fornecedor TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Ruta inicial - Dashboard
@app.route('/')
def dashboard():
    """Exibe o dashboard gerencial com métricas principais"""
    conn = get_db_connection()
    
    # Total de produtos cadastrados
    total_produtos = conn.execute('SELECT COUNT(*) FROM produtos').fetchone()[0]
    
    # Total de unidades em estoque
    total_unidades = conn.execute('SELECT SUM(quantidade) FROM produtos').fetchone()[0] or 0
    
    # Valor total do estoque (preço * quantidade)
    valor_total = conn.execute('SELECT SUM(preco * quantidade) FROM produtos').fetchone()[0] or 0
    
    # Produtos com estoque baixo (quantidade <= 10)
    estoque_baixo = conn.execute('SELECT COUNT(*) FROM produtos WHERE quantidade <= 10').fetchone()[0]
    
    # Lista de produtos com estoque baixo para alerta
    produtos_baixo = conn.execute('SELECT nome, quantidade FROM produtos WHERE quantidade <= 10').fetchall()
    
    # Dados para gráficos - lazy loading mode
    # Categoria distribution
    categoria_stats = conn.execute('''
        SELECT categoria, COUNT(*) as total, SUM(preco * quantidade) as valor
        FROM produtos
        GROUP BY categoria
        ORDER BY total DESC
        LIMIT 5
    ''').fetchall()
    
    # Estoque por fornecedor (top 5)
    fornecedor_stats = conn.execute('''
        SELECT fornecedor, COUNT(*) as total, SUM(quantidade) as unidades
        FROM produtos
        GROUP BY fornecedor
        ORDER BY total DESC
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('index.html',
                         total_produtos=total_produtos,
                         total_unidades=total_unidades,
                         valor_total=valor_total,
                         estoque_baixo=estoque_baixo,
                         produtos_baixo=produtos_baixo,
                         categoria_stats=categoria_stats,
                         fornecedor_stats=fornecedor_stats,
                         lazy_mode=True)

# Listar todos os produtos
@app.route('/produtos')
def listar_produtos():
    """Lista todos os produtos com possibilidade de pesquisa"""
    termo_pesquisa = request.args.get('pesquisa', '')
    
    conn = get_db_connection()
    
    if termo_pesquisa:
        produtos = conn.execute(
            '''SELECT * FROM produtos 
               WHERE nome LIKE ? OR categoria LIKE ? OR fornecedor LIKE ?
               ORDER BY nome''',
            (f'%{termo_pesquisa}%', f'%{termo_pesquisa}%', f'%{termo_pesquisa}%')
        ).fetchall()
    else:
        produtos = conn.execute('SELECT * FROM produtos ORDER BY nome').fetchall()
    
    conn.close()
    
    return render_template('produtos.html', produtos=produtos, termo_pesquisa=termo_pesquisa)

# Página de cadastro
@app.route('/produto/novo', methods=['GET', 'POST'])
def novo_produto():
    """Formulário para cadastrar novo produto"""
    
    if request.method == 'POST':
        # Coleta dados do formulário
        nome = request.form.get('nome', '').strip()
        categoria = request.form.get('categoria', '').strip()
        preco = request.form.get('preco', '').strip()
        quantidade = request.form.get('quantidade', '').strip()
        fornecedor = request.form.get('fornecedor', '').strip()
        
        # Validação dos dados
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
        
        if erros:
            for erro in erros:
                flash(erro, 'error')
            return render_template('formulario.html', produto=None, acao='cadastrar')
        
        # Insere no banco de dados
        conn = get_db_connection()
        conn.execute(
            '''INSERT INTO produtos (nome, categoria, preco, quantidade, fornecedor)
               VALUES (?, ?, ?, ?, ?)''',
            (nome, categoria, preco_valor, quantidade_valor, fornecedor)
        )
        conn.commit()
        conn.close()
        
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_produtos'))
    
    return render_template('formulario.html', produto=None, acao='cadastrar')

# Página de edição
@app.route('/produto/editar/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    """Formulário para editar produto existente"""
    conn = get_db_connection()
    produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
    
    if not produto:
        flash('Produto não encontrado.', 'error')
        conn.close()
        return redirect(url_for('listar_produtos'))
    
    if request.method == 'POST':
        # Coleta dados
        nome = request.form.get('nome', '').strip()
        categoria = request.form.get('categoria', '').strip()
        preco = request.form.get('preco', '').strip()
        quantidade = request.form.get('quantidade', '').strip()
        fornecedor = request.form.get('fornecedor', '').strip()
        
        # Validação
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
        
        if erros:
            for erro in erros:
                flash(erro, 'error')
            conn.close()
            return render_template('formulario.html', produto=produto, acao='editar')
        
        # Atualiza no banco
        conn.execute(
            '''UPDATE produtos 
               SET nome=?, categoria=?, preco=?, quantidade=?, fornecedor=?, atualizado_em=CURRENT_TIMESTAMP
               WHERE id=?''',
            (nome, categoria, preco_valor, quantidade_valor, fornecedor, id)
        )
        conn.commit()
        conn.close()
        
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('listar_produtos'))
    
    conn.close()
    return render_template('formulario.html', produto=produto, acao='editar')

# Excluir produto
@app.route('/produto/excluir/<int:id>', methods=['POST'])
def excluir_produto(id):
    """Exclui um produto do banco de dados"""
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

# Inicializa o banco de dados ao iniciar a aplicação
init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8009)
