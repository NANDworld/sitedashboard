@echo off
cd /d "C:\Users\UsuarioPc\Downloads\Paata de projetos com AI\sistemadesahboards"

echo ================================
echo   Enviando para GitHub (SSH)
echo ================================
echo.

echo Configurando git...
git config user.email "SEU_EMAIL"
git config user.name "SEU_NOME"

echo Adicionando arquivos...
git add .

echo Criando commit...
git commit -m "Initial commit: Sistema de Produtos com Dashboard

- CSS corrigido e responsivo
- Gráficos Chart.js com lazy loading
- Tabela mobile com cards
- Porta alterada para 8009"

echo Configurando remote SSH...
git remote remove origin 2>nul
git remote add origin git@github.com:NANDworld/sitedashboard.git

echo Enviando para GitHub...
git push -u origin main

echo.
echo ================================
echo   ✅ Projeto enviado!
echo   🔗 https://github.com/NANDworld/sitedashboard
echo ================================
pause
