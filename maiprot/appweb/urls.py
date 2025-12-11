from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    # ---------------------------
    # PÁGINAS BASE
    # ---------------------------
    path('', views.inicio, name='inicio'),
    path('catalogo/', views.catalogo, name='catalogo'),

    # ---------------------------
    # AUTENTICACIÓN
    # ---------------------------
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),

    # ---------------------------
    # PERFIL DE USUARIO
    # ---------------------------
    path('perfil/', views.ver_perfil, name='ver_perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),

    # ---------------------------
    # CARRITO DE COMPRAS
    # ---------------------------
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_item, name='eliminar_item'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),

    # ---------------------------
    # PEDIDOS
    # ---------------------------
    path('pedido/realizar/', views.realizar_pedido, name='realizar_pedido'),
    path('pedido/<int:pedido_id>/', views.ver_pedido, name='ver_pedido'),

    # ---------------------------
    # FACTURA
    # ---------------------------
    path('pedido/<int:pedido_id>/factura/', views.generar_factura, name='generar_factura'),
    path('factura/<int:factura_id>/', views.ver_factura, name='ver_factura'),

    # =====================================================
    # RECUPERAR CONTRASEÑA - SISTEMA COMPLETO
    # =====================================================

    # 1️⃣ Usuario ingresa su correo
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='password/password_reset.html',
            email_template_name='password/password_reset_email.html',
            subject_template_name='password/password_reset_subject.txt'
        ),
        name='password_reset'
    ),

    # 2️⃣ Django confirma que envió el correo
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='password/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    # 3️⃣ Usuario abre el enlace enviado al correo
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='password/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    # 4️⃣ Contraseña cambiada con éxito
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='password/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
