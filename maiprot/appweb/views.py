from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistroForm, PedidoForm, PerfilForm, PerfilUsuarioForm 
from .models import Producto, Pedido, Factura , DetallePedido, Carrito, ItemCarrito
from django.contrib import messages 
from .models import PerfilUsuario
from django.db.models import Sum, F
from django.http import JsonResponse


# ============================
# FORMATEAR MONTOS A CLP
# ============================
def formatear_clp(valor):
    try:
        return f"${valor:,.0f}".replace(",", ".")
    except:
        return valor
    
# -----------------------------------------------------
# VISTAS BASE DEL PROYECTO MAIPROT
# -----------------------------------------------------

def inicio(request):
    """Página de inicio."""
    return render(request, 'index.html')

def catalogo(request):
    """Muestra el catálogo de productos."""
    productos = Producto.objects.all()
    return render(request, 'catalogo.html', {'productos': productos})

# -----------------------------------------------------
# VISTAS DE AUTENTICACIÓN
# -----------------------------------------------------

def registro(request):
    """Registro con RUT como username y validación completa."""
    if request.method == 'POST':
        form = RegistroForm(request.POST)

        if form.is_valid():
            # Crear el usuario sin guardar aún
            user = form.save(commit=False)

            # Username = RUT (limpio)
            rut = form.cleaned_data["rut"].strip()
            user.username = rut

            # Guardar la contraseña correctamente
            user.set_password(form.cleaned_data["password"])
            user.save()

            messages.success(
                request,
                "🎉 ¡Tu cuenta fue creada exitosamente! Ahora puedes iniciar sesión."
            )

            return redirect('login')

        else:
            # Mostrar errores uno por uno
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"⚠️ {error}")

    else:
        form = RegistroForm()

    return render(request, 'registro.html', {'form': form})



def login_usuario(request):
    if request.method == 'POST':
        user_input = request.POST['username']   # Puede ser RUT o correo
        password = request.POST['password']

        # 1) Intentar login asumiendo que es username (RUT)
        user = authenticate(request, username=user_input, password=password)

        # 2) Si no funcionó, intentamos tratarlo como correo
        if user is None:
            try:
                user_obj = User.objects.get(email=user_input)
                user = authenticate(
                    request,
                    username=user_obj.username,
                    password=password
                )
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            nombre = user.first_name if user.first_name else user.username
            messages.success(request, f"¡Nos alegra verte de nuevo, {nombre}! 👋")
            return redirect('inicio')
        else:
            messages.error(request, '❌ RUT/Correo o contraseña incorrectos.')

    return render(request, 'login.html')

@login_required
def logout_usuario(request):
    messages.info(request, "Has cerrado sesión correctamente. ¡Te esperamos pronto! 👋")
    logout(request)
    return redirect('inicio')


# -----------------------------------------------------
# VISTAS DE PERFIL DEL USUARIO 
# -----------------------------------------------------

@login_required
def ver_perfil(request):
    """Muestra los datos del usuario logueado."""
    return render(request, 'perfil.html', {'usuario': request.user})

@login_required
def editar_perfil(request):
    """
    Permite al usuario modificar sus datos de perfil (modelo User) 
    y sus datos adicionales (modelo PerfilUsuario) simultáneamente.
    """
    
  
    perfil_usuario = request.user.perfilusuario
        
    if request.method == 'POST':
        user_form = PerfilForm(request.POST, instance=request.user)
        perfil_form = PerfilUsuarioForm(request.POST, request.FILES, instance=perfil_usuario) 
        
        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            perfil_form.save()
            
            messages.success(request, "✔️ Tu perfil fue actualizado correctamente.")
            return redirect('ver_perfil')
        else:
            messages.error(request, 'Hubo errores en la información. Por favor, revisa ambos formularios.')
    else:
        user_form = PerfilForm(instance=request.user)
        perfil_form = PerfilUsuarioForm(instance=perfil_usuario)
        
    contexto = {
        'user_form': user_form,
        'perfil_form': perfil_form
    }
    
    return render(request, 'editar_perfil.html', contexto)


# -----------------------------------------------------
# VISTAS DE PEDIDOS Y FACTURACIÓN (Placeholders)
# -----------------------------------------------------

@login_required
def pedidos(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.usuario = request.user
            pedido.save()
            return redirect('inicio')
        else:
            # Si el formulario NO es válido, lo devolvemos con errores
            return render(request, 'pedidos.html', {'form': form})
    
    else:
        form = PedidoForm()

    return render(request, 'pedidos.html', {'form': form})

@login_required
def ver_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    detalles = pedido.detalles.all()

    return render(request, "ver_pedido.html", {
        "pedido": pedido,
        "detalles": detalles
    })

@login_required
def generar_factura(request, pedido_id):
    """Genera la factura de un pedido (usando la lógica de DetallePedido)."""
    pass 

@login_required
def ver_factura(request, factura_id):
    """Muestra la factura generada."""
    pass 

@login_required
def admin_panel(request):
    """Panel de administración."""
    pass

@login_required
def generar_factura(request, pedido_id):
    """Genera la factura de un pedido si aún no existe."""
    try:
        # 1. Obtener el pedido
        pedido = Pedido.objects.get(id=pedido_id, usuario=request.user)
    except Pedido.DoesNotExist:
        messages.error(request, 'Pedido no encontrado o no autorizado.')
        return redirect('pedidos')
    
    # 2. Verificar si la factura ya existe (OneToOneField)
    if hasattr(pedido, 'factura'):
        messages.info(request, f'La factura para el pedido {pedido_id} ya existe.')
        return redirect('ver_factura', factura_id=pedido.factura.id)
        
   
    total_calculado = DetallePedido.objects.filter(pedido=pedido).aggregate(
        total=Sum(F('cantidad') * F('precio_unitario_guardado'))
    )['total']
    
    if total_calculado is None:
        total_calculado = 0.00 # Si no hay detalles, el total es 0
        
    # 4. Crear la Factura
    factura = Factura.objects.create(
        pedido=pedido,
        monto_total=total_calculado,
        estado='PENDIENTE' # Estado inicial
    )
    
    messages.success(request, f'Factura N°{factura.id} generada con éxito para el Pedido {pedido_id}.')
    return redirect('ver_factura', factura_id=factura.id)


# -----------------------------------------------------
#   CÓDIGO PARA VER LA FACTURA
# -----------------------------------------------------

@login_required
def ver_factura(request, factura_id):
    """Muestra la factura generada con montos formateados."""

    try:
        factura = Factura.objects.get(id=factura_id, pedido__usuario=request.user)
    except Factura.DoesNotExist:
        messages.error(request, 'Factura no encontrada o no autorizada.')
        return redirect('pedidos')

    detalles = factura.pedido.detalles.all()

    # Agregar valores formateados a cada detalle
    for d in detalles:
        d.precio_formateado = formatear_clp(d.precio_unitario_guardado)
        subtotal = d.cantidad * d.precio_unitario_guardado
        d.subtotal_formateado = formatear_clp(subtotal)

    contexto = {
        'factura': factura,
        'detalles': detalles,
        'total_formateado': formatear_clp(factura.monto_total)
    }

    return render(request, 'factura.html', contexto)


# -----------------------------------------------------
#  CARRITO DE COMPRAS (CORREGIDO Y COMPLETO)
# -----------------------------------------------------

def agregar_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = request.user.carrito

    # Capturar cantidad desde POST
    cantidad = int(request.POST.get("cantidad", 1))

    item, creado = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        producto=producto
    )

    if creado:
        item.cantidad = cantidad
    else:
        item.cantidad += cantidad

    item.save()

    messages.success(request, f"🛒 {producto.nombre} fue agregado a tu carrito.")

    return redirect("catalogo")

@login_required
def ver_carrito(request):
    """Muestra todos los productos del carrito."""
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    return render(request, "carrito.html", {"carrito": carrito})


@login_required
def eliminar_item_carrito(request, item_id):
    """Elimina un solo item del carrito."""
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    item.delete()
    messages.warning(request, "🗑️ El producto fue eliminado del carrito.")
    return redirect("ver_carrito")


@login_required
def vaciar_carrito(request):
    """Vacía el carrito completamente."""
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    carrito.items.all().delete()
    messages.warning(request, "🛒 Tu carrito se vació completamente.")
    return redirect("ver_carrito")

@login_required
def realizar_pedido(request):
    usuario = request.user
    carrito = usuario.carrito
    items = carrito.items.all()

    # Si el carrito está vacío, no permitir continuar
    if not items.exists():
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('catalogo')

    if request.method == "POST":
        urgente = request.POST.get("urgente")
        plazo = int(request.POST.get("plazo"))

        # Crear pedido
        pedido = Pedido.objects.create(
            usuario=usuario,
            monto_total=carrito.total(),
            estado="PENDIENTE"
        )

        # Crear detalles del pedido
        for item in items:
            DetallePedido.objects.create(
                pedido=pedido,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario_guardado=item.producto.precio
            )

        # Vaciar carrito
        carrito.items.all().delete()

        # Redirigir a resumen del pedido
        messages.success(request, f"📦 Tu pedido #{pedido.id} ha sido generado exitosamente.")
        return redirect('ver_pedido', pedido.id)

    # ⬇⬇⬇ ESTA PARTE ES LA CLAVE: enviamos todo al template
    return render(request, "realizar_pedido.html", {
        "carrito": carrito,
        "items": items,
        "total": carrito.total(),
    })

@login_required
def actualizar_cantidad(request, item_id):
    """Vista AJAX para actualizar cantidad o eliminar item del carrito"""
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)

    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    cantidad = int(request.POST.get("cantidad", 1))

    # Si cantidad = 0 → eliminar
    if cantidad <= 0:
        item.delete()
        carrito = item.carrito
        return JsonResponse({
            "eliminado": True,
            "total": carrito.total(),
        })

    # Si solo se actualiza cantidad
    item.cantidad = cantidad
    item.save()

    carrito = item.carrito

    return JsonResponse({
        "eliminado": False,
        "subtotal": item.subtotal(),
        "total": carrito.total(),
    })



@login_required
def eliminar_item(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    item.delete()
    messages.success(request, "Producto eliminado del carrito.")
    return redirect("ver_carrito")

