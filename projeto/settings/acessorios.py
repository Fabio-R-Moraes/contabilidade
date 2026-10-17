from .ambiente import BASE_DIR
import os

STATIC_URL = '/static/'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_FILES_DIRS = [
    os.path.join(BASE_DIR, 'financeiro', 'static'),
    ]
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

#Configuração para envio de e-mail via Gmail SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'fmoraes05@gmail.com'
EMAIL_HOST_PASSWORD = 'xdno rtas zwvs idfw'
DEFAULT_FROM_EMAIL = 'fmoraes05@gmail.com'
CONTACT_EMAIL = 'fmoraes05@gmail.com'
