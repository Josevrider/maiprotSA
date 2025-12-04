from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Pedido, PerfilUsuario
import re


# -----------------------------------------------------
# 1. FORMULARIO DE REGISTRO CON RUT Y CONFIRMAR CONTRASEÑA
# -----------------------------------------------------
class RegistroForm(forms.ModelForm):
    first_name = forms.CharField(label="Nombre", max_length=50)
    last_name = forms.CharField(label="Apellido", max_length=50)
    email = forms.EmailField(label="Correo electrónico")

    rut = forms.CharField(label="RUT", max_length=12)

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput
    )

    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "rut",
            "username",  # lo ocultamos en el HTML, pero debe existir
            "password"
        ]

    # ------------------------------
    # VALIDACIÓN DE RUT CHILENO
    # ------------------------------
    def clean_rut(self):
        rut = self.cleaned_data["rut"].replace(".", "").replace("-", "").lower()

        if not re.match(r"^\d{7,8}[0-9kK]$", rut):
            raise ValidationError("El RUT ingresado no es válido (formato incorrecto).")

        cuerpo = rut[:-1]
        dv_ingresado = rut[-1]

        # Cálculo del dígito verificador
        suma = 0
        multiplo = 2

        for c in reversed(cuerpo):
            suma += int(c) * multiplo
            multiplo = 9 if multiplo == 7 else multiplo + 1

        dv_calculado = 11 - (suma % 11)

        if dv_calculado == 11:
            dv_calculado = "0"
        elif dv_calculado == 10:
            dv_calculado = "k"
        else:
            dv_calculado = str(dv_calculado)

        if dv_calculado != dv_ingresado:
            raise ValidationError("El RUT ingresado no es válido (dígito incorrecto).")

        return rut

    # ------------------------------
    # VALIDACIÓN DE CONTRASEÑAS
    # ------------------------------
    def clean(self):
        cleaned_data = super().clean()

        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise ValidationError("Las contraseñas no coinciden.")

        return cleaned_data


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
# 4. PEDIDOS
# -----------------------------------------------------
class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ["estado"]
