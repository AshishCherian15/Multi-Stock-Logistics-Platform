from django.apps import AppConfig

class AuthSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_system'
    
    def ready(self):
        # Clear all sessions on server start to force re-login
        from django.contrib.sessions.models import Session
        try:
            Session.objects.all().delete()
            print("✅ All sessions cleared - Users must login again")
        except:
            pass
