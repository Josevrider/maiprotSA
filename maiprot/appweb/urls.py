from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('catalogo/', views.catalogo, name='catalogo'),

    # Autenticación
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),

    # Carrito
    path('agregar-carrito/<int:producto_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),


    # Pedidos
    path('pedido/<int:pedido_id>/', views.ver_pedido, name='ver_pedido'),
    path('realizar-pedido/', views.realizar_pedido, name='realizar_pedido'),

    # Facturación
    path('factura/<int:factura_id>/', views.ver_factura, name='ver_factura'),
    path('generar_factura/<int:pedido_id>/', views.generar_factura, name='generar_factura'),

    # Perfil de usuario
    path('perfil/', views.ver_perfil, name='ver_perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),

    # Panel admin (si lo usarás)
    path('admin-panel/', views.admin_panel, name='admin_panel'),
]
