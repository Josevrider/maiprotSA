from rest_framework import serializers
from ..models import Producto, Pedido, DetallePedido, Factura 


# -----------------------------------------------------
# 1. Serializador de Producto (Para el Catálogo)
# -----------------------------------------------------

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'precio']

# -----------------------------------------------------
# 2. Serializador de DetallePedido (Para líneas de pedido)
# -----------------------------------------------------

class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre') 

    class Meta:
        model = DetallePedido
        fields = ['producto', 'producto_nombre', 'cantidad', 'precio_unitario_guardado', 'subtotal']
        read_only_fields = ['subtotal'] 

# -----------------------------------------------------
# 3. Serializador de Pedido (Encabezado)
# -----------------------------------------------------

class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(source='detallepedido_set', many=True, read_only=True)
    
    class Meta:
        model = Pedido
        fields = ['id', 'usuario', 'fecha_pedido', 'estado', 'total_pedido', 'detalles']
        read_only_fields = ['usuario', 'total_pedido', 'fecha_pedido']

class FacturaSerializer(serializers.ModelSerializer):
    pedido = PedidoSerializer(read_only=True) 
    
    class Meta:
        model = Factura
        fields = ['id', 'pedido', 'fecha_emision', 'monto_total', 'estado']