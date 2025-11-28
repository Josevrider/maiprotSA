from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet
from django.urls import path, include
from . import views


router = DefaultRouter()
router.register(r'productos', ProductoViewSet)



urlpatterns = [
    path('', include(router.urls)), 
    path("api/carrito/actualizar/<int:item_id>/", views.api_actualizar_cantidad, name="api_actualizar_cantidad"),

]