from django.contrib import admin
from .models import Producto, Pedido, Factura, PerfilUsuario, DetallePedido, ImagenProducto, BannerPromocional 

from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from weasyprint import HTML
from django.conf import settings
from django.db.models import Sum

# -----------------------------------------------------
# ACCIÓN PERSONALIZADA DE WEASYPRINT
# -----------------------------------------------------

@admin.action(description='Generar PDF de la Factura')
def generar_pdf_factura(modeladmin, request, queryset):
    factura = queryset.first() 
    
    if not factura:
        modeladmin.message_user(request, "Por favor, selecciona al menos una factura.", level='error')
        return redirect('admin:appweb_factura_changelist')


    html_string = render_to_string('factura_pdf.html', {'factura': factura})
    

    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    
    pdf_file = html.write_pdf()

   
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Factura_{factura.id}_{factura.pedido.usuario.username}.pdf"'
    
    return response

# -------------------------------------------------------------------
# INLINE PARA IMÁGENES ADICIONALES DE PRODUCTO
# -------------------------------------------------------------------
class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1

# -------------------------------------------------------------------
# REGISTRO DE MODELOS USANDO DECORADOR @admin.register
# -------------------------------------------------------------------

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido_link', 'fecha_emision', 'monto_total', 'estado')
    list_filter = ('estado', 'fecha_emision')
    search_fields = ('pedido__usuario__username', 'id')
    actions = [generar_pdf_factura]
    
    def pedido_link(self, obj):
        link = reverse("admin:appweb_pedido_change", args=[obj.pedido.id])
        return mark_safe(f'<a href="{link}">Pedido N°{obj.pedido.id}</a>')
    pedido_link.short_description = 'Pedido'

# ✅ REGISTRO DE PRODUCTO CORREGIDO (ÚNICO REGISTRO)
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'descripcion')
    search_fields = ('nombre',)
    inlines = [ImagenProductoInline]

# -------------------------------------------------------------------
# REGISTROS SIMPLES FALTANTES (usando admin.site.register)
# -------------------------------------------------------------------


admin.site.register(PerfilUsuario)
admin.site.register(Pedido)
admin.site.register(DetallePedido)

