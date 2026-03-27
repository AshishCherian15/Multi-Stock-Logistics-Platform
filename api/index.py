import os
import sys
from django.core.wsgi import get_wsgi_application

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "greaterwms.settings")

app = get_wsgi_application()
