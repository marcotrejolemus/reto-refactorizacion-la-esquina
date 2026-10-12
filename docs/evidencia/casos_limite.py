"""Casos limite de descuentos, VIP y empates en mas_vendidos.

Uso: python casos_limite.py <ruta_src>
Solo trabaja en memoria: no lee ni escribe archivos.
"""

import sys

sys.path.insert(0, sys.argv[1])

import gestor  # noqa: E402
import reportes  # noqa: E402


def mostrar_venta(etiqueta, venta):
    if venta is None:
        print(etiqueta, None, repr(gestor.ultimo_error))
        return
    datos = {k: v for k, v in venta.items() if k != "fecha"}
    print(etiqueta, datos, "tipo_descuento=" + type(venta["descuento"]).__name__)


# --- Limites de descuento por volumen (subtotal = precio x cantidad) ---
gestor.reiniciar_sistema()
casos_volumen = [
    ("V499", 499.0, 1), ("V500", 500.0, 1), ("V999", 999.0, 1),
    ("V1000", 1000.0, 1), ("F499", 1.0, 499), ("F500", 1.0, 500),
    ("F999", 1.0, 999), ("F1000", 1.0, 1000), ("D0.1x5000", 0.1, 5000),
    ("D0.1x10000", 0.1, 10000), ("D33.33x30", 33.33, 30),
    ("D49.99x20", 49.99, 20), ("D99.99x10", 99.99, 10),
]
for codigo, precio, cantidad in casos_volumen:
    gestor.agregarProducto(codigo, "Prod " + codigo, precio, 100000)
    print("cotizar", codigo, gestor.cotizar(codigo, cantidad))
    mostrar_venta("venta " + codigo, gestor.registrar_venta(codigo, cantidad))

# --- Limites VIP: subtotal despues del descuento por volumen vs 200 ---
gestor.reiniciar_sistema()
casos_vip = [
    ("P200", 200.0, 1, "VIP1"), ("P201", 201.0, 1, "VIP1"),
    ("P200b", 1.0, 200, "VIP"), ("P201b", 1.0, 201, "VIP"),
    ("P200.01", 200.01, 1, "VIP9"), ("P201n", 201.0, 1, ""),
    ("P201m", 201.0, 1, "vip1"), ("P201s", 201.0, 1, "XVIP"),
    ("P201c", 201.0, 1, "VI"), ("P201x", 201.0, 1, None),
    ("P500", 500.0, 1, "VIP"), ("P1000", 1000.0, 1, "VIP"),
]
for codigo, precio, cantidad, cliente in casos_vip:
    gestor.agregarProducto(codigo, "Prod " + codigo, precio, 1000)
    # cotizar no recibe cliente: nunca aplica el extra VIP
    print("cotizar", codigo, gestor.cotizar(codigo, cantidad))
    venta = gestor.registrar_venta(codigo, cantidad, cliente)
    mostrar_venta("venta " + codigo + " cliente=" + repr(cliente), venta)

# --- Empates en mas_vendidos (orden de primera aparicion) ---
gestor.reiniciar_sistema()
for codigo in ["X", "Y", "Z", "W", "Q"]:
    gestor.agregarProducto(codigo, "Prod " + codigo, 1.0, 1000)
for codigo, cantidad in [
    ("X", 3), ("Y", 1), ("Z", 5), ("Y", 2), ("W", 3), ("Q", 1), ("X", 0),
]:
    gestor.registrar_venta(codigo, cantidad)
print("mas_vendidos n=3", reportes.mas_vendidos())
print("mas_vendidos n=10", reportes.mas_vendidos(10))
print("mas_vendidos n=2", reportes.mas_vendidos(2))
print("mas_vendidos n=0", reportes.mas_vendidos(0))

gestor.reiniciar_sistema()
for codigo in ["B", "A", "C"]:
    gestor.agregarProducto(codigo, "Prod " + codigo, 1.0, 1000)
    gestor.registrar_venta(codigo, 4)
print("mas_vendidos todos_empatados", reportes.mas_vendidos(10))

gestor.reiniciar_sistema()
print("mas_vendidos sin_ventas", reportes.mas_vendidos())
