"""Casos de validacion y efectos de registrar_venta.

Uso: python casos_validacion.py <ruta_src>
Solo trabaja en memoria: no lee ni escribe archivos.
"""

import sys

sys.path.insert(0, sys.argv[1])

import gestor  # noqa: E402

NAN = float("nan")
INF = float("inf")


def estado():
    """Foto del estado global: stock por producto, folio y numero de ventas."""
    stocks = {codigo: p["stock"] for codigo, p in gestor.INVENTARIO.items()}
    return "stock=%r folio=%r ventas=%r" % (
        stocks, gestor.contador_ventas, len(gestor.VENTAS)
    )


def probar(etiqueta, codigo, cantidad, cliente=""):
    """Registra una venta e imprime retorno, ultimo_error y estado posterior."""
    try:
        venta = gestor.registrar_venta(codigo, cantidad, cliente)
    except Exception as error:  # se registra el tipo de excepcion, no se oculta
        print(etiqueta, "EXCEPCION", type(error).__name__, str(error))
        print("   ", "ultimo_error=%r" % gestor.ultimo_error, estado())
        return None
    if venta is None:
        print(etiqueta, "None", "ultimo_error=%r" % gestor.ultimo_error)
    else:
        datos = {k: v for k, v in venta.items() if k != "fecha"}
        print(etiqueta, "OK", datos)
        print("   ", "claves=%r" % list(venta.keys()))
        print("   ", "ticket=%r" % venta["ticket"])
        print("   ", "es_ultima_venta=%r" % (venta is gestor.VENTAS[-1]))
        print("   ", "tipo_descuento=%s" % type(venta["descuento"]).__name__)
        print("   ", "ultimo_error=%r" % gestor.ultimo_error)
    print("   ", estado())
    return venta


gestor.reiniciar_sistema()
gestor.agregarProducto("A1", "Café", 100.0, 10)
gestor.agregarProducto("B1", "Galletas", 5.0, 3)
gestor.agregarProducto("Z0", "Agotado", 1.0, 0)
producto_a1 = gestor.INVENTARIO["A1"]
print("inicio", estado())

# --- Orden de validaciones con varios errores a la vez ---
probar("vacio_y_cantidad_0", "", 0)
probar("none_y_none", None, None)
probar("vacio_y_cantidad_ok", "", 5)
probar("inexistente_y_cantidad_0", "NO", 0)
probar("inexistente_y_none", "NO", None)
probar("inexistente_y_nan", "NO", NAN)

# --- Cantidades invalidas sobre un producto existente ---
probar("cantidad_none", "A1", None)
probar("cantidad_0", "A1", 0)
probar("cantidad_menos_1", "A1", -1)
probar("cantidad_menos_cero", "A1", -0.0)
probar("cantidad_nan", "A1", NAN)

# --- Stock insuficiente ---
probar("stock_mas_1", "A1", 11)
probar("stock_cero", "Z0", 1)
probar("cantidad_inf", "A1", INF)

# --- Codigo no hashable (debe fallar igual que hoy) ---
probar("codigo_lista", ["A1"], 1)

# --- ultimo_error no se limpia con una venta exitosa ---
gestor.ultimo_error = "marca previa"
probar("stock_exacto", "B1", 3)
probar("stock_agotado_despues", "B1", 1)

# --- Ventas exitosas: tickets con y sin linea de descuento ---
gestor.ultimo_error = "marca previa"
probar("sin_descuento", "A1", 1)
probar("cantidad_decimal", "A1", 2.5)
gestor.agregarProducto("C1", "Cafetera", 100.0, 50)
probar("descuento_volumen", "C1", 6)
probar("descuento_vip", "C1", 6, "VIP007")
probar("cliente_none", "C1", 6, None)
probar("vip_alto", "C1", 10, "VIP")

print("producto_a1_mismo_objeto", producto_a1 is gestor.INVENTARIO["A1"])
print("folios", [v["folio"] for v in gestor.VENTAS])
print("fin", estado())
