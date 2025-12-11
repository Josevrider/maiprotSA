from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from .models import Pedido, PerfilUsuario
from .email_utils import enviar_correo_html   # IMPORTANTE


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

    def clean_rut(self):
        rut = self.cleaned_data["rut"].replace(".", "").replace("-", "").upper()

        # Validar estructura (módulo 11)
        if not validar_rut(rut):
            raise ValidationError("El RUT ingresado no es válido.")

        # Verificar que NO exista ya en la base de datos
        if User.objects.filter(username=rut).exists():
            raise ValidationError("Este RUT ya está registrado.")

        return rut

    def clean(self):
        cleaned = super().clean()

        password = cleaned.get("password")
        password2 = cleaned.get("password2")

        if password and password2 and password != password2:
            raise ValidationError("Las contraseñas no coinciden.")

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)

        user.username = self.cleaned_data["rut"]
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


# -----------------------------------------------------
# 5. FORMULARIO PERSONALIZADO PARA RECUPERAR CONTRASEÑA
# -----------------------------------------------------
class PasswordResetCustomForm(PasswordResetForm):

    def save(self, domain_override=None,
             subject_template_name="registration/password_reset_subject.txt",
             email_template_name="registration/password_reset_email.html",
             html_email_template_name=None,
             use_https=True,
             token_generator=default_token_generator,
             from_email=None,
             request=None,
             extra_email_context=None):

        email = self.cleaned_data["email"]
        users = self.get_users(email)

        for user in users:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)

            context = {
                "email": user.email,
                "domain": request.get_host(),
                "site_name": "Maiprot",
                "uid": uid,
                "user": user,
                "token": token,
                "protocol": "https",
            }

            enviar_correo_html(
                subject="Restablecer contraseña - Maiprot",
                template_html=email_template_name,
                template_txt="registration/password_reset_email.txt",
                context=context,
                recipient=user.email
            )
