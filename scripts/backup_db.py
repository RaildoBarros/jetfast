import shutil
import os
from datetime import datetime

# Caminhos (Ajuste para os seus diretórios)
ORIGEM = '/home/raildo/jetfast/db.sqlite3'
DESTINO_DIR = '/home/raildo/backups/'
NOME_BACKUP = f'backup_{datetime.now().strftime("%Y%m%d_%H%M")}.sqlite3'

if not os.path.exists(DESTINO_DIR):
    os.makedirs(DESTINO_DIR)

shutil.copy2(ORIGEM, os.path.join(DESTINO_DIR, NOME_BACKUP))
print(f"Backup realizado com sucesso: {NOME_BACKUP}")