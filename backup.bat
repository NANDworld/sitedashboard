@echo off
REM Script de Backup Automático
REM Nome do Solicitante: Gestor da Filial Norte
REM Descrição: Backup automático do banco de dados às 06h e 18h

echo ========================================
echo   Backup do Banco de Dados
echo ========================================
echo.
echo Data: %DATE%
echo Hora: %TIME%
echo.

REM Diretórios
set BACKUP_DIR=C:\BKP_BANCO
set DB_FILE=dbfilialnorte.db

REM Criar pasta de backup se não existir
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Gerar nome do backup com máscara BKP-DDMMAAAHHMM
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set MYDATE=%%c%%b%%a)
for /f "tokens=1-2 delims=: " %%a in ('time /t') do (set MYTIME=%%a%%b)

set BACKUP_NAME=BKP-%MYDATE%%MYTIME%.db
set BACKUP_PATH=%BACKUP_DIR%\%BACKUP_NAME%

echo Copiando banco de dados...
echo Origem: %DB_FILE%
echo Destino: %BACKUP_PATH%
echo.

copy /Y "%DB_FILE%" "%BACKUP_PATH%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   ✅ Backup realizado com sucesso!
    echo   Arquivo: %BACKUP_NAME%
    echo   Local: %BACKUP_DIR%
    echo ========================================
) else (
    echo.
    echo ========================================
    echo   ❌ Erro ao realizar backup!
    echo ========================================
)

echo.
pause
