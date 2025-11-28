from django import forms
from django.contrib.auth.models import User
from .models import Pedido, PerfilUsuario 

# -----------------------------------------------------
# 1. Autenticación
# -----------------------------------------------------

class RegistroForm(forms.ModelForm):
   
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name'] 
        
# -----------------------------------------------------
# 2. Edición de Perfil (Conexión al Perfil y al Usuario)
# -----------------------------------------------------

class PerfilForm(forms.ModelForm):
    """
    Formulario para editar los datos esenciales del modelo User.
    Se conecta directamente a la vista 'editar_perfil' que creamos.
    """
    class Meta:
        model = User
        
        fields = ['first_name', 'last_name', 'email'] 
        

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['direccion', 'telefono', 'imagen_perfil']
        

# -----------------------------------------------------
# 3. Pedidos
# -----------------------------------------------------

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        
        fields = ['estado'] 
