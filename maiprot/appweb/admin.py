from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import redirect
from weasyprint import HTML

from .models import (
    Producto, Pedido, Factura, PerfilUsuario,
    DetallePedido, ImagenProducto, BannerPromocional
)

# =====================================================
# UTILIDAD: Formateo CLP sin decimales
# =====================================================
def clp(monto):
    try:
        monto = int(round(float(monto)))
        return f"$ {monto:,}".replace(",", ".")
    except:
        return monto


# =====================================================
# ACCIÓN ADMIN: Generar PDF de la Factura
# =====================================================
@admin.action(description='Generar PDF de la Factura')
def generar_pdf_factura(modeladmin, request, queryset):
    factura = queryset.first()

    if not factura:
        modeladmin.message_user(request, "Selecciona una factura.", level='error')
        return redirect('admin:appweb_factura_changelist')

    html_string = render_to_string('factura_pdf.html', {'factura': factura})
    pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Factura_{factura.id}.pdf"'
    return response


# =====================================================
# INLINE: Imágenes adicionales
# =====================================================
class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1


# =====================================================
# INLINE: Detalles Pedido
# =====================================================
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario_guardado', 'subtotal_format')

    def subtotal_format(self, obj):
        return clp(obj.subtotal)
    subtotal_format.short_description = "Subtotal"


# =====================================================
# ADMIN Pedido
# =====================================================
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_pedido', 'estado', 'total_format')
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('usuario__username', 'id')
    inlines = [DetallePedidoInline]

    def total_format(self, obj):
        return clp(obj.total_pedido)
    total_format.short_description = "Total Pedido"


# =====================================================
# ADMIN Factura – con protección anticrash
# =====================================================
@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido_link', 'fecha_emision', 'total_format', 'estado')
    list_filter = ('estado', 'fecha_emision')
    search_fields = ('pedido__usuario__username', 'id')
    actions = [generar_pdf_factura]

    readonly_fields = ('detalles_pedido', 'total_pedido_preview')

    # JS para recargar al seleccionar pedido
    class Media:
        js = ("admin/factura_auto_reload.js",)

    # Guardar request actual
    def get_form(self, request, obj=None, **kwargs):
        self._current_request = request
        return super().get_form(request, obj, **kwargs)

    fieldsets = (
        (None, {
            'fields': (
                'pedido',
                'fecha_emision',
                'monto_total',
                'total_pedido_preview',
                'estado'
            )
        }),
        ("Detalles del Pedido", {
            'fields': ('detalles_pedido',),
        }),
    )

    # ================================
    # Mostrar total ANTES de guardar
    # ================================
    def total_pedido_preview(self, obj):
        pedido_id = None

        if obj and obj.pedido_id:
            pedido_id = obj.pedido_id

        if not pedido_id and hasattr(self, "_current_request"):
            pedido_id = self._current_request.GET.get("pedido")

        if pedido_id:
            pedido = Pedido.objects.filter(id=pedido_id).first()
            if pedido:
                return clp(pedido.total_pedido)

        return "Seleccione un pedido"

    total_pedido_preview.short_description = "Total del Pedido"

    # ======================================
    # Mostrar productos ANTES de guardar
    # ======================================
    def detalles_pedido(self, obj):
        pedido_id = None

        if obj and obj.pedido_id:
            pedido_id = obj.pedido_id

        if not pedido_id and hasattr(self, "_current_request"):
            pedido_id = self._current_request.GET.get("pedido")

        if pedido_id:
            pedido = Pedido.objects.filter(id=pedido_id).first()
            if pedido:
                html = "<ul>"
                for d in pedido.detalles.all():
                    html += f"<li>{d.cantidad} x {d.producto.nombre} — {clp(d.subtotal)}</li>"
                html += "</ul>"
                return mark_safe(html)

        return "-"

    detalles_pedido.short_description = "Productos del Pedido"

    # ================================
    # Link al pedido – anticrash
    # ================================
    def pedido_link(self, obj):
        if not obj.pedido_id:
            return "— (sin pedido)"
        try:
            url = reverse("admin:appweb_pedido_change", args=[obj.pedido.id])
            return mark_safe(f'<a href="{url}">Pedido N°{obj.pedido.id}</a>')
        except:
            return "— (pedido inválido)"
    pedido_link.short_description = "Pedido"

    # ================================
    # Total formateado – anticrash
    # ================================
    def total_format(self, obj):
        try:
            return clp(obj.monto_total or 0)
        except:
            return "$0"

    total_format.short_description = "Total Factura"


# =====================================================
# ADMIN Producto
# =====================================================
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_format', 'descripcion')
    search_fields = ('nombre',)
    inlines = [ImagenProductoInline]

    def precio_format(self, obj):
        return clp(obj.precio)
    precio_format.short_description = "Precio"


# =====================================================
# REGISTROS SIMPLES
# =====================================================
admin.site.register(PerfilUsuario)
admin.site.register(DetallePedido)
admin.site.register(BannerPromocional)
