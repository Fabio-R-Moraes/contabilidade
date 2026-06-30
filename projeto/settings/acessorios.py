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
