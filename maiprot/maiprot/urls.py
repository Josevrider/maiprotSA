"""
URL configuration for maiprot project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# === 🔥 IMPORTACIÓN PARA CREAR SUPERUSUARIO TEMPORAL ===
from django.contrib.auth.models import User
from django.http import HttpResponse
from appweb.views import create_admin

def crear_admin(request):
    """
    Crea un superusuario temporalmente desde la URL:
    https://tuapp.onrender.com/crear-admin/
    Luego borra esta función y su ruta.
    """
    if User.objects.filter(username="admin").exists():
        return HttpResponse("El admin ya existe")

    User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="admin123"
    )
    return HttpResponse("Superusuario creado correctamente")
# ========================================================


from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # RUTA TEMPORAL PARA CREAR ADMIN
    path("crear-admin/", crear_admin),   # 👈🔥 ESTA ES LA NUEVA RUTA

    # Rutas de la web principal
    path('', include('appweb.urls')),

    # API
    path('api/v1/', include('appweb.api.urls')),
    path('api-auth/', include('rest_framework.urls')),

    # ESQUEMA Y DOCUMENTACIÓN
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Password Reset
    path("password_reset/",
         auth_views.PasswordResetView.as_view(
             template_name="password/password_reset.html"
         ),
         name="password_reset"),
    path("password_reset_done/",
         auth_views.PasswordResetDoneView.as_view(
             template_name="password/password_reset_done.html"
         ),
         name="password_reset_done"),
    path("reset/<uidb64>/<token>/",
         auth_views.PasswordResetConfirmView.as_view(
             template_name="password/password_reset_confirm.html"
         ),
         name="password_reset_confirm"),
    path("reset_complete/",
         auth_views.PasswordResetCompleteView.as_view(
             template_name="password/password_reset_complete.html"
         ),
         name="password_reset_complete"),
    
    

]

# Archivos media
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
