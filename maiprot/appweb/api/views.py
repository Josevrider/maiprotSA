from rest_framework import viewsets, permissions
from appweb.models import Producto, Pedido, Factura
from .serializers import ProductoSerializer, PedidoSerializer, FacturaSerializer 
from rest_framework.authentication import TokenAuthentication
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from appweb.models import ItemCarrito, Carrito


# -----------------------------------------------------
# 1. API para el Catálogo (Productos)
# -----------------------------------------------------

class ProductoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint de solo lectura que permite ver la lista de productos y el detalle.
    """
    queryset = Producto.objects.all().order_by('nombre')
    serializer_class = ProductoSerializer
    permission_classes = [permissions.AllowAny] 

# -----------------------------------------------------
# 2. API para Actualizar
# -----------------------------------------------------

@login_required
def api_actualizar_cantidad(request, item_id):
    """Actualiza la cantidad del item sin recargar la página (AJAX)."""
    if request.method == "POST":
        item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)

        cantidad = int(request.POST.get("cantidad", 1))
        if cantidad <= 0:
            item.delete()
            return JsonResponse({"eliminado": True, "total": item.carrito.total()})

        item.cantidad = cantidad
        item.save()

        return JsonResponse({
            "subtotal": item.subtotal(),
            "total": item.carrito.total()
        })

    return JsonResponse({"error": "Método no permitido"}, status=405)
