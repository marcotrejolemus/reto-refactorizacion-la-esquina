"""Modulo principal del gestor de inventario y ventas de "La Esquina".

Aqui vive casi toda la logica del negocio. Historicamente este archivo
lo fueron parchando varias personas, asi que hay de todo un poco.
"""

from datetime import datetime

# ---------------------------------------------------------------
# Reglas de negocio: descuentos, clientes VIP e impuestos
# ---------------------------------------------------------------
UMBRAL_DESCUENTO_ALTO = 1000
TASA_DESCUENTO_ALTO = 0.10
UMBRAL_DESCUENTO_MEDIO = 500
TASA_DESCUENTO_MEDIO = 0.05
PREFIJO_VIP = "VIP"
MONTO_MINIMO_VIP = 200
TASA_DESCUENTO_VIP = 0.02
TASA_IVA = 0.16
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"

# ---------------------------------------------------------------
# Estado global de la aplicacion (inventario, ventas y contadores)
# ---------------------------------------------------------------
INVENTARIO = {}
VENTAS = []
contador_ventas = 0
ultimo_error = ""
MODO_DEBUG = False


def reiniciar_sistema():
    """Borra todo el estado del sistema (inventario, ventas y folios)."""
    global contador_ventas, ultimo_error
    INVENTARIO.clear()
    VENTAS.clear()
    contador_ventas = 0
    ultimo_error = ""


def agregarProducto(codigo, nombre, precio, stock):
    # valida los datos y da de alta un producto en el inventario
    global ultimo_error
    if codigo is None or codigo == "":
        ultimo_error = "codigo vacio"
        return False
    if codigo in INVENTARIO:
        ultimo_error = "el producto ya existe"
        return False
    if precio <= 0:
        ultimo_error = "precio invalido"
        return False
    if stock < 0:
        ultimo_error = "stock invalido"
        return False
    producto = {}
    producto["codigo"] = codigo
    producto["nombre"] = nombre
    producto["precio"] = precio
    producto["stock"] = stock
    INVENTARIO[codigo] = producto
    return True


def eliminar_producto(codigo):
    """Quita un producto del inventario. Regresa False si no existe."""
    global ultimo_error
    if codigo in INVENTARIO:
        del INVENTARIO[codigo]
        return True
    ultimo_error = "producto no existe"
    return False


def actualizar_stock(codigo, cantidad):
    """Suma unidades al stock (o resta si la cantidad es negativa)."""
    global ultimo_error
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return False
    nuevo_stock = INVENTARIO[codigo]["stock"] + cantidad
    if nuevo_stock < 0:
        ultimo_error = "el stock no puede quedar negativo"
        return False
    INVENTARIO[codigo]["stock"] = nuevo_stock
    return True


def buscarProducto(texto):
    # busca productos cuyo nombre contenga el texto (sin importar mayusculas)
    encontrados = []
    for codigo in INVENTARIO:
        if texto.lower() in INVENTARIO[codigo]["nombre"].lower():
            encontrados.append(INVENTARIO[codigo])
    return encontrados


def _descuento_por_volumen(subtotal):
    """Calcula el descuento por volumen de compra (sin el extra VIP)."""
    if subtotal >= UMBRAL_DESCUENTO_ALTO:
        return subtotal * TASA_DESCUENTO_ALTO
    if subtotal >= UMBRAL_DESCUENTO_MEDIO:
        return subtotal * TASA_DESCUENTO_MEDIO
    return 0


def _es_cliente_vip(cliente):
    """Indica si el codigo de cliente empieza con el prefijo VIP."""
    return (
        cliente != ""
        and cliente is not None
        and len(cliente) >= len(PREFIJO_VIP)
        and cliente[0:len(PREFIJO_VIP)] == PREFIJO_VIP
    )


def _validar_venta(codigo, cantidad):
    """Revisa los datos de una venta en el orden original.

    Regresa el producto del inventario si la venta es valida; si no,
    regresa None y deja el motivo en ultimo_error. Cada condicion es la
    negacion completa de la original (sin De Morgan) para que valores
    como float("nan") sigan dando el mismo mensaje.
    """
    global ultimo_error
    if not (codigo is not None and codigo != ""):
        ultimo_error = "codigo vacio"
        return None
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return None
    if not (cantidad is not None and cantidad > 0):
        ultimo_error = "cantidad invalida"
        return None
    if not INVENTARIO[codigo]["stock"] >= cantidad:
        ultimo_error = "stock insuficiente"
        return None
    return INVENTARIO[codigo]


def _calcular_montos(precio, cantidad, cliente):
    """Calcula subtotal, descuento, impuesto y total de una venta."""
    subtotal = precio * cantidad
    # descuentos por volumen de compra
    descuento = _descuento_por_volumen(subtotal)
    # los clientes cuyo codigo empieza con VIP tienen un extra,
    # pero solo si su compra (ya con descuento) pasa de cierto monto
    if _es_cliente_vip(cliente) and subtotal - descuento > MONTO_MINIMO_VIP:
        descuento = descuento + subtotal * TASA_DESCUENTO_VIP
    base = subtotal - descuento
    impuesto = base * TASA_IVA
    total = round(base + impuesto, 2)
    return subtotal, descuento, impuesto, total


def _armar_ticket(venta, descuento):
    """Arma el ticket en texto plano.

    Recibe el descuento sin redondear: la linea de descuento solo se
    agrega cuando es mayor que cero, igual que antes.
    """
    ticket = ""
    ticket = ticket + "TIENDA LA ESQUINA\n"
    ticket = ticket + "----------------------------\n"
    ticket = ticket + "Folio: " + str(venta["folio"]) + "\n"
    ticket = ticket + venta["nombre"] + " x" + str(venta["cantidad"]) + "\n"
    ticket = ticket + "Subtotal: $" + str(venta["subtotal"]) + "\n"
    if descuento > 0:
        ticket = ticket + "Descuento: -$" + str(venta["descuento"]) + "\n"
    ticket = ticket + "IVA: $" + str(venta["impuesto"]) + "\n"
    ticket = ticket + "TOTAL: $" + str(venta["total"]) + "\n"
    return ticket


def registrar_venta(codigo, cantidad, cliente=""):
    """Registra una venta completa.

    Valida los datos, calcula descuentos e impuestos, descuenta el stock,
    genera el folio, arma el ticket en texto y guarda el registro en la
    lista de ventas. Si algo falla regresa None y deja el motivo en
    ultimo_error.
    """
    global contador_ventas
    producto = _validar_venta(codigo, cantidad)
    if producto is None:
        return None
    subtotal, descuento, impuesto, total = _calcular_montos(
        producto["precio"], cantidad, cliente
    )
    # descontar del inventario
    producto["stock"] = producto["stock"] - cantidad
    contador_ventas = contador_ventas + 1
    venta = {}
    venta["folio"] = contador_ventas
    venta["codigo"] = codigo
    venta["nombre"] = producto["nombre"]
    venta["cantidad"] = cantidad
    venta["subtotal"] = round(subtotal, 2)
    venta["descuento"] = round(descuento, 2)
    venta["impuesto"] = round(impuesto, 2)
    venta["total"] = total
    venta["cliente"] = cliente
    venta["fecha"] = datetime.now().strftime(FORMATO_FECHA)
    venta["ticket"] = _armar_ticket(venta, descuento)
    VENTAS.append(venta)
    return venta


def cotizar(codigo, cantidad):
    """Calcula cuanto costaria una compra sin registrar la venta."""
    global ultimo_error
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return None
    if cantidad is None or cantidad <= 0:
        ultimo_error = "cantidad invalida"
        return None
    subtotal = INVENTARIO[codigo]["precio"] * cantidad
    descuento = _descuento_por_volumen(subtotal)
    base = subtotal - descuento
    total = base + base * TASA_IVA
    return round(total, 2)


def calcular_descuento_viejo(monto):
    # NOTA: esta era la formula de descuentos que se uso hasta 2023,
    # ya nadie la llama pero la dejamos por si acaso
    if monto > 800:
        return monto * 0.08
    return 0


# def exportar_txt(ruta):
#     f = open(ruta, "w")
#     for k in INVENTARIO:
#         f.write(k + " - " + str(INVENTARIO[k]["stock"]) + "\n")
#     f.close()
#     return True
