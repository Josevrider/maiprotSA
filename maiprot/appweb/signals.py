from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import PerfilUsuario 


# ----------------------------------------------------------------------
# 1. FUNCIÓN PARA CREAR EL PERFIL
# ----------------------------------------------------------------------


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Crea un PerfilUsuario automáticamente (usando get_or_create) solo 
    cuando el usuario es nuevo (created=True), asegurando unicidad.
    """
    if created:
        PerfilUsuario.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Guarda el PerfilUsuario asociado cada vez que se guarda el User."""
    try:
        instance.perfilusuario.save()
    except PerfilUsuario.DoesNotExist:
        pass

# ----------------------------------------------------------------------
# 2. FUNCIÓN PARA GUARDAR EL PERFIL
# ----------------------------------------------------------------------

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    Se activa cada vez que se guarda el objeto User (después del created inicial).
    Esto garantiza que si editas el User, el PerfilUsuario también se guarda.
    """
    
    try:
        instance.perfilusuario.save()
    except PerfilUsuario.DoesNotExist:

        pass