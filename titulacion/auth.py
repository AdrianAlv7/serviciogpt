# backends.py (or in your app's auth.py)
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .models import Egresado

User = get_user_model()

class EgresadoAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, curp=None, **kwargs):
        try:
            # Find the student by school_id
            egresado = Egresado.objects.get(curp=curp)
            # Check if the email matches the user's email
            if egresado.usuario.email == email:
                return egresado.usuario
        except Egresado.DoesNotExist:
            return None
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
# Verifica si el usuario es parte de servicios escolares
def is_servicions_escolares(user): 
    return user.is_authenticated and user.groups.filter(name='servicios_escolares').exists()

# Verifica si el usuario es parte de egresado
def is_egresado(user):
    return user.is_authenticated and user.groups.filter(name='egresados').exists()