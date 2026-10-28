#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduler de Backup Automático
Executa backups às 06h e 18h todos os dias
Nome do Solicitante: Gestor da Filial Norte
"""

import sqlite3
import os
import shutil
import time
from datetime import datetime

DATABASE = 'dbfilialnorte.db'
BACKUP_DIR = 'C:/BKP_BANCO'

def criar_backup():
    """Cria backup do banco de dados"""
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        
        if not os.path.exists(DATABASE):
            print(f'Erro: Banco de dados {DATABASE} não encontrado!')
            return False
        
        timestamp = datetime.now().strftime('%d%m%Y%H%M')
        backup_name = f'BKP-{timestamp}.db'
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        
        shutil.copy2(DATABASE, backup_path)
        print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M")}] Backup realizado: {backup_name}')
        return True
    except Exception as e:
        print(f'Erro no backup: {e}')
        return False

def proximo_backup():
    """Calcula tempo até o próximo backup (06h ou 18h)"""
    now = datetime.now()
    hour = now.hour
    
    if hour < 6:
        next_run = now.replace(hour=6, minute=0, second=0, microsecond=0)
    elif hour < 18:
        next_run = now.replace(hour=18, minute=0, second=0, microsecond=0)
    else:
        next_run = (now + __import__('datetime').timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)
    
    return (next_run - now).total_seconds()

if __name__ == '__main__':
    print('=' * 50)
    print('  Scheduler de Backup - Filial Norte')
    print('=' * 50)
    print()
    print('Backup automático agendado para:')
    print('  - 06:00 (manhã)')
    print('  - 18:00 (tarde)')
    print()
    
    while True:
        sleep_seconds = proximo_backup()
        print(f'Aguardando {sleep_seconds/3600:.1f} horas para o próximo backup...')
        time.sleep(sleep_seconds)
        criar_backup()
