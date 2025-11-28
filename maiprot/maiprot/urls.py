"""
URL configuration for maiprot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Rutas de la web principal
    path('', include('appweb.urls')),

    # API
    path('api/v1/', include('appweb.api.urls')),
    path('api-auth/', include('rest_framework.urls')),

    # ESQUEMA Y DOCUMENTACIÓN (solo una vez)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
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

# ==== SERVIR ARCHIVOS DE MEDIA (IMÁGENES) ====
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

