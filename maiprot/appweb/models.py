from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True) 

    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('PROCESO', 'En Proceso'),
        ('COMPLETADO', 'Completado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    fecha_pedido = models.DateTimeField(default=timezone.now)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')

    # 🔥 NUEVOS CAMPOS
    urgente = models.BooleanField(default=False)
    plazo_dias = models.PositiveIntegerField(default=7)

    def __str__(self):
        return f"Pedido N°{self.id} de {self.usuario.username}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    precio_unitario_guardado = models.DecimalField(max_digits=10, decimal_places=2) 
    
    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario_guardado

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Pedido {self.pedido.id}"

class Factura(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente de Pago'),
        ('PAGADA', 'Pagada'),
        ('ANULADA', 'Anulada'),
    ]
    
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='factura')
    fecha_emision = models.DateTimeField(default=timezone.now)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')

    def __str__(self):
        return f"Factura N°{self.id} (Pedido {self.pedido.id})"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"
    
class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True) 
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    imagen_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True) 
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(user=instance)

@receiver(post_save, sender=User)
def guardar_perfil(sender, instance, **kwargs):
    instance.perfilusuario.save()

class ImagenProducto(models.Model):
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE, 
        related_name='imagenes_adicionales' 
    )
    imagen = models.ImageField(upload_to='productos_galeria/')
    descripcion = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Imagen para {self.producto.nombre}"

class BannerPromocional(models.Model):
    titulo = models.CharField(max_length=100, help_text="Título o mensaje principal del banner.")
    imagen = models.ImageField(upload_to='banners/', help_text="La imagen principal de la promoción (ej: 1920x500).")
    enlace_url = models.URLField(max_length=200, blank=True, null=True, help_text="URL a donde dirige el banner (ej: /catalogo/).")
    activo = models.BooleanField(default=True, help_text="Marca si el banner debe mostrarse en la web.")
    orden = models.IntegerField(default=0, help_text="Define la posición en el carrusel (orden ascendente).")

    class Meta:
        verbose_name = "Banner Promocional"
        verbose_name_plural = "Banners Promocionales"
        ordering = ['orden']
        
    def __str__(self):
        return self.titulo

class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

    def total(self):
        return sum(item.subtotal() for item in self.items.all())


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.cantidad * self.producto.precio

@receiver(post_save, sender=User)
def crear_carrito_usuario(sender, instance, created, **kwargs):
    if created:
        Carrito.objects.create(usuario=instance)
