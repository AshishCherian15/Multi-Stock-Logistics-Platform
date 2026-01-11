import os
import sys
from django.core.wsgi import get_wsgi_application

# Ensure project root is on Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "greaterwms.settings")

application = get_wsgi_application()

# Vercel requires this
app = application
handler = application