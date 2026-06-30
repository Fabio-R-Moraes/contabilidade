from pathlib import Path
import os
from utils.enviroment import parse_separar_virgula_str_to_list, get_env_variaveis

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'INSECURE')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # if os.environ.get('DEBUG') == 1 else False

ALLOWED_HOSTS : list[str] = parse_separar_virgula_str_to_list(get_env_variaveis('ALLOWED_HOSTS'))
CSRF_TRUSTED_ORIGINS : list[str] = parse_separar_virgula_str_to_list(get_env_variaveis('CSRF_TRUSTED_ORIGINS'))

ROOT_URLCONF = 'projeto.urls'

WSGI_APPLICATION = 'projeto.wsgi.application'
