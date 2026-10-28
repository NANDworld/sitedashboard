# Script para enviar projeto ao GitHub (SSH)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Enviando para GitHub via SSH" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configura git
Write-Host "Configurando git..." -ForegroundColor Yellow
git config user.email "SEU_EMAIL_AQUI"
git config user.name "SEU_NOME_AQUI"

# Adiciona arquivos
Write-Host "Adicionando arquivos..." -ForegroundColor Yellow
git add .

# Commit
Write-Host "Criando commit..." -ForegroundColor Yellow
git commit -m "Initial commit: Sistema de Produtos com Dashboard

- CSS corrigido e responsivo
- Gráficos Chart.js com lazy loading
- Tabela mobile com cards
- Porta alterada para 8009"

# Remote SSH
Write-Host "Configurando remote SSH..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin git@github.com:NANDworld/sitedashboard.git

# Push
Write-Host "Enviando para GitHub..." -ForegroundColor Yellow
git push -u origin main

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ Projeto enviado com sucesso!" -ForegroundColor Green
Write-Host "  🔗 https://github.com/NANDworld/sitedashboard" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
