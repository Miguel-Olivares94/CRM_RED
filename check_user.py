import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

User = get_user_model()
try:
    user = User.objects.get(email='vendedor1@claro.cl')
    print(f"Usuario: {user.email}")
    print(f"Grupos: {', '.join([g.name for g in user.groups.all()])}")
    print(f"Es superuser: {user.is_superuser}")
    print(f"Es staff: {user.is_staff}")
except User.DoesNotExist:
    print("Usuario no encontrado")
except Exception as e:
    print(f"Error: {e}")
