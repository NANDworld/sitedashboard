# Sistema de Cadastro de Produtos com Dashboard Gerencial

## 📋 Descrição

Sistema web completo para cadastro e gerenciamento de produtos, desenvolvido com Flask (Python), HTML, CSS e SQLite.

## 🚀 Como Executar

### 1. Instalar Python

Certifique-se de ter o Python 3.8 ou superior instalado:
- Acesse: https://www.python.org/downloads/
- Baixe e instale a versão mais recente
- Verifique a instalação: python --version

### 2. Instalar Dependências

Abra o terminal na pasta do projeto e execute:

    pip install -r requirements.txt

Ou instale manualmente:

    pip install Flask==3.0.3
    pip install gunicorn==23.0.0

### 3. Executar o Sistema

No terminal, na pasta do projeto, execute:

    python app.py

O sistema iniciará no endereço: http://localhost:5000

### 4. Acessar o Sistema

Abra seu navegador e acesse:
- Dashboard: http://localhost:5000/
- Produtos: http://localhost:5000/produtos
- Novo Produto: http://localhost:5000/produto/novo

## 🗄️ Banco de Dados SQLite

O banco de dados é criado automaticamente na primeira execução (arquivo: produtos.db).

### Como executar comandos SQL no SQLite:

Metodo 1 - Interface de Linha de Comando:
    sqlite3 produtos.db
    .tables
    SELECT * FROM produtos;
    .quit

Metodo 2 - Usando o arquivo banco_de_dados.txt:
O arquivo contém scripts SQL prontos para consulta e criação de índices.

Metodo 3 - Interface Grafica (Recomendado):
- Baixe o DB Browser for SQLite: https://sqlitebrowser.org/
- Abra o arquivo produtos.db
- Execute consultas visualmente

## 📁 Estrutura de Arquivos

sistemadesahboards/
├── app.py              # Aplicação Flask principal
├── requirements.txt    # Dependências Python
├── banco_de_dados.txt  # Scripts SQL
├── README.txt          # Este arquivo
├── produtos.db         # Banco de dados SQLite (criado automaticamente)
├── templates/
│   ├── index.html      # Dashboard gerencial
│   ├── produtos.html   # Lista de produtos
│   └── formulario.html # Formulário de cadastro/edição
└── static/
    └── style.css       # Estilos CSS

## 🔧 Funcionalidades

### Dashboard Gerencial
- Total de produtos cadastrados
- Total de unidades em estoque
- Valor total do estoque
- Produtos com estoque baixo (alerta visual)
- Lista de produtos que precisam de reposição

### Gerenciamento de Produtos
- Listar todos os produtos
- Cadastrar novo produto
- Editar produto existente
- Excluir produto
- Pesquisar por nome, categoria ou fornecedor
- Validação de dados nos formulários
- Alertas de estoque baixo

## 🔒 Segurança

- Utiliza consultas parametrizadas contra SQL Injection
- Validação de dados no backend e frontend
- Senha de sessão configurada no secret_key

## 🎨 Tecnologias Utilizadas

- Backend: Python 3 + Flask
- Banco de Dados: SQLite
- Frontend: HTML5 + CSS3
- Icones: Emoji nativo

## 📝 Requisitos do Sistema

- Python 3.8+
- 100MB de espaço em disco
- Navegador web moderno

## ⚠️ Notas Importantes

1. O banco de dados SQLite é criado automaticamente na primeira execução
2. Não é necessario configurar senha para o SQLite (banco local)
3. Os dados sao persistidos no arquivo produtos.db
4. Para backup, copie o arquivo produtos.db

## 🐛 Solucao de Problemas

Problema: Erro ao executar python app.py
Solucao: Verifique se o Python esta instalado e no PATH

Problema: Erro de dependencias
Solucao: Execute pip install -r requirements.txt

Problema: Pagina nao carrega
Solucao: Verifique se o servidor esta rodando (porta 5000)

## 📞 Suporte

Para duvidas ou problemas, verifique o arquivo banco_de_dados.txt para consultas SQL avançadas.
