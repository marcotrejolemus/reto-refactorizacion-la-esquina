"""Caracterizacion del comportamiento observable de La Esquina.

Uso: python caracterizar.py <ruta_src> <dir_trabajo>
Imprime retornos, tickets, reportes, errores y JSON (sin fechas).
"""

import contextlib
import io
import json
import os
import sys

src, trabajo = sys.argv[1], sys.argv[2]
sys.path.insert(0, src)

import almacen  # noqa: E402
import gestor  # noqa: E402
import reportes  # noqa: E402


def sin_fecha(venta):
    if venta is None:
        return None
    return {k: v for k, v in venta.items() if k != "fecha"}


def callado(func, *args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ret = func(*args)
    return ret, buf.getvalue()


gestor.reiniciar_sistema()
altas = [
    ("", "Vacio", 1.0, 1), (None, "None", 1.0, 1),
    ("A1", "Café de grano", 100.0, 500), ("A1", "Dup", 1.0, 1),
    ("A2", "Azúcar", 0, 1), ("A3", "Leche", 26.0, 3),
    ("A4", "Neg", 1.0, -1), ("B1", "Galletas", 49.9, 200),
    ("C1", "Chocolate", 78.9, 2), ("D1", "Arroz", 1000.0, 50),
]
for alta in altas:
    print("alta", alta, gestor.agregarProducto(*alta), repr(gestor.ultimo_error))

print("buscar", gestor.buscarProducto("CAF"), gestor.buscarProducto("zzz"))
print("stock", gestor.actualizar_stock("A3", 2), gestor.actualizar_stock("A3", -99),
      gestor.actualizar_stock("NO", 1), repr(gestor.ultimo_error))

ventas = [
    ("", 1, ""), (None, 1, ""), ("NO", 1, ""), ("A1", 0, ""), ("A1", None, ""),
    ("A1", -1, ""), ("C1", 3, ""), ("A1", 4, ""), ("A1", 5, ""), ("A1", 9, ""),
    ("A1", 10, ""), ("A1", 2, "VIP1"), ("A1", 3, "VIP1"), ("A1", 6, "VIP007"),
    ("A1", 20, "VIP"), ("A1", 20, "VI"), ("A1", 6, None), ("A1", 6, "vip9"),
    ("B1", 3, ""), ("B1", 7, "VIPx"), ("B1", 11, ""), ("B1", 21, "VIPz"),
    ("D1", 1, "VIP"), ("A3", 5, ""),
]
for venta in ventas:
    v = gestor.registrar_venta(*venta)
    print("venta", venta, sin_fecha(v), repr(gestor.ultimo_error))

for cot in [("A1", 6), ("A1", 0), ("NO", 1), ("", 1), ("B1", 11), ("D1", 1)]:
    print("cotizar", cot, gestor.cotizar(*cot), repr(gestor.ultimo_error))

print("bajos", reportes.productos_stock_bajo())
print("inventario", callado(reportes.reporte_inventario))
print("total", reportes.total_vendido())
print("mas_vendidos", reportes.mas_vendidos(), reportes.mas_vendidos(10))
print("resumen", callado(reportes.resumen_ventas))
print("descuento_viejo", gestor.calcular_descuento_viejo(900),
      gestor.calcular_descuento_viejo(800))

ruta_csv = os.path.join(trabajo, "viejo.csv")
csv_func = getattr(reportes, "reporte_viejo_csv", None) or reportes.reporteViejoCSV
print("csv_ret_ok", csv_func(ruta_csv) == ruta_csv)
with open(ruta_csv, encoding="utf-8") as f:
    print("csv", repr(f.read()))

ruta = os.path.join(trabajo, "datos.json")
print("guardar", almacen.guardar_datos(ruta))
with open(ruta, encoding="utf-8") as f:
    datos = json.load(f)
for v in datos["ventas"]:
    v.pop("fecha")
print("json", json.dumps(datos, ensure_ascii=False, sort_keys=False))
with open(ruta, encoding="utf-8") as f:
    texto = f.read()
print("json_lineas", len(texto.splitlines()), "ensure_ascii_false", "Café" in texto)

gestor.reiniciar_sistema()
print("cargar", almacen.cargar_datos(ruta), len(gestor.INVENTARIO), len(gestor.VENTAS))
print("folio_siguiente", gestor.registrar_venta("B1", 1)["folio"])
print("cargar_no_existe", almacen.cargar_datos(os.path.join(trabajo, "x.json")),
      repr(gestor.ultimo_error))
corrupto = os.path.join(trabajo, "corrupto.json")
with open(corrupto, "w", encoding="utf-8") as f:
    f.write("{no es json")
print("cargar_corrupto", almacen.cargar_datos(corrupto), repr(gestor.ultimo_error))
hay = getattr(almacen, "hay_archivo", None) or almacen.hayArchivo
print("hay_archivo", hay(ruta), hay(corrupto + "x"))
print("eliminar", gestor.eliminar_producto("B1"), gestor.eliminar_producto("B1"),
      repr(gestor.ultimo_error))
