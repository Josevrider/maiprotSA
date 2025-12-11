from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Pedido, PerfilUsuario


# -----------------------------------------------------
# FUNCIÓN SEGURA PARA VALIDAR RUT (MÓDULO 11)
# -----------------------------------------------------
def validar_rut(rut):
    rut = rut.replace(".", "").replace("-", "").upper()

    if len(rut) < 2:
        return False

    cuerpo = rut[:-1]
    dv = rut[-1]

    if not cuerpo.isdigit():
        return False

    suma = 0
    multiplicador = 2

    for c in reversed(cuerpo):
        suma += int(c) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2

    resto = suma % 11
    dv_calculado = 11 - resto

    if dv_calculado == 11:
        dv_calculado = "0"
    elif dv_calculado == 10:
        dv_calculado = "K"
    else:
        dv_calculado = str(dv_calculado)

    return dv == dv_calculado


# -----------------------------------------------------
# 1. FORMULARIO DE REGISTRO
# -----------------------------------------------------
class RegistroForm(forms.ModelForm):

    rut = forms.CharField(
        max_length=12,
        required=True,
        label="RUT",
        help_text="Ej: 11.111.111-1"
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Contraseña"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Confirmar contraseña"
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        labels = {
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
        }

    # -------------------------------------------------
    # VALIDACIÓN COMPLETA DEL RUT
    # -------------------------------------------------
    def clean_rut(self):
        rut = self.cleaned_data["rut"].replace(".", "").replace("-", "").upper()

        # Validar estructura (módulo 11)
        if not validar_rut(rut):
            raise ValidationError("El RUT ingresado no es válido.")

        # Verificar que NO exista ya en la base de datos
        if User.objects.filter(username=rut).exists():
            raise ValidationError("Este RUT ya está registrado.")

        return rut

    # -------------------------------------------------
    # VALIDACIÓN: contraseñas iguales
    # -------------------------------------------------
    def clean(self):
        cleaned = super().clean()

        password = cleaned.get("password")
        password2 = cleaned.get("password2")

        if password and password2 and password != password2:
            raise ValidationError("Las contraseñas no coinciden.")

        return cleaned

    # -------------------------------------------------
    # GUARDAR EL RUT COMO USERNAME
    # -------------------------------------------------
    def save(self, commit=True):
        user = super().save(commit=False)

        # Usar RUT normalizado como username
        user.username = self.cleaned_data["rut"]

        # Guardar contraseña encriptada
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user


# -----------------------------------------------------
# 2. FORMULARIO PERFIL USER
# -----------------------------------------------------
class PerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


# -----------------------------------------------------
# 3. FORMULARIO PERFILUSUARIO
# -----------------------------------------------------
class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ["direccion", "telefono", "imagen_perfil"]


# -----------------------------------------------------
# 4. FORMULARIO PEDIDOS
# -----------------------------------------------------
class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ["estado"]
