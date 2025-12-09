from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Pedido, PerfilUsuario
import re


# -----------------------------------------------------
# 1. FORMULARIO DE REGISTRO CON RUT Y CONFIRMAR CONTRASEÑA
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

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        password2 = cleaned.get("password2")

        if password and password2 and password != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned

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
