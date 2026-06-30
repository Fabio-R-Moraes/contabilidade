from .ambiente import BASE_DIR
from pathlib import Path

caminho_bd = Path(__file__).resolve().parent.parent.parent

print(f"CAMINHO: {caminho_bd}")
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': caminho_bd / 'dinheiro.sqlite3',
    }
}
