"""Reportes de la tienda: inventario, ventas y mas vendidos."""

import gestor

# Un producto con menos unidades que este minimo se considera con stock bajo
STOCK_MINIMO = 5


def formatear_moneda(valor):
    # le da formato de dinero al numero
    return "$" + str(round(valor, 2))


def productos_stock_bajo():
    """Regresa la lista de productos con stock por debajo del minimo."""
    productos_bajos = []
    for codigo in gestor.INVENTARIO:
        if gestor.INVENTARIO[codigo]["stock"] < STOCK_MINIMO:
            productos_bajos.append(gestor.INVENTARIO[codigo])
    return productos_bajos


def reporte_inventario():
    """Arma el reporte del inventario, lo imprime y lo regresa como texto."""
    texto = "===== INVENTARIO =====\n"
    valor_total = 0
    for codigo in gestor.INVENTARIO:
        producto = gestor.INVENTARIO[codigo]
        linea = producto["codigo"] + " | " + producto["nombre"] + " | "
        linea = linea + formatear_moneda(producto["precio"])
        linea = linea + " | stock: " + str(producto["stock"])
        if producto["stock"] < STOCK_MINIMO:
            linea = linea + "  <-- STOCK BAJO"
        texto = texto + linea + "\n"
        valor_total = valor_total + producto["precio"] * producto["stock"]
    texto = texto + "Valor total del inventario: " + formatear_moneda(valor_total)
    texto = texto + "\n"
    print(texto)
    return texto


def total_vendido():
    """Suma el total (con IVA) de todas las ventas registradas."""
    total = 0
    for venta in gestor.VENTAS:
        total = total + venta["total"]
    return round(total, 2)


def mas_vendidos(n=3):
    """Regresa los n productos mas vendidos como lista de (codigo, unidades)."""
    unidades_por_codigo = {}
    for venta in gestor.VENTAS:
        if venta["codigo"] in unidades_por_codigo:
            unidades_por_codigo[venta["codigo"]] = (
                unidades_por_codigo[venta["codigo"]] + venta["cantidad"]
            )
        else:
            unidades_por_codigo[venta["codigo"]] = venta["cantidad"]
    ranking = []
    for codigo in unidades_por_codigo:
        ranking.append((codigo, unidades_por_codigo[codigo]))
    # ordenamiento de burbuja (TODO: algun dia usar sorted)
    for i in range(len(ranking)):
        for j in range(0, len(ranking) - i - 1):
            if ranking[j][1] < ranking[j + 1][1]:
                temporal = ranking[j]
                ranking[j] = ranking[j + 1]
                ranking[j + 1] = temporal
    return ranking[0:n]


def resumen_ventas():
    """Arma el resumen de ventas del dia, lo imprime y lo regresa."""
    texto = "===== RESUMEN DE VENTAS =====\n"
    total = 0
    for venta in gestor.VENTAS:
        texto = texto + "Folio " + str(venta["folio"]) + ": " + venta["nombre"]
        texto = texto + " x" + str(venta["cantidad"]) + " = "
        texto = texto + formatear_moneda(venta["total"]) + "\n"
        total = total + venta["total"]
    texto = texto + "Numero de ventas: " + str(len(gestor.VENTAS)) + "\n"
    texto = texto + "Total del dia: " + formatear_moneda(total) + "\n"
    print(texto)
    return texto


def reporte_viejo_csv(ruta):
    # version vieja del reporte que pedia contabilidad, ya no se usa
    # desde que cambiaron de sistema, pero por si las dudas aqui sigue
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write("codigo,nombre,stock\n")
        for codigo in gestor.INVENTARIO:
            producto = gestor.INVENTARIO[codigo]
            archivo.write(
                producto["codigo"] + "," + producto["nombre"] + ","
                + str(producto["stock"]) + "\n"
            )
    return ruta
