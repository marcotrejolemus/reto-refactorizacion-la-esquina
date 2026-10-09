# CLAUDE.md — Gestor "La Esquina"

## Proyecto
Aplicación de consola en Python (>= 3.10) para el inventario y las ventas de la
tienda "La Esquina": alta de productos, ventas con descuentos e IVA, cotizaciones,
alertas de stock bajo, más vendidos y persistencia en JSON.

Es el reto académico "Refactorización Asistida por IA" (Next-Gen Coding, Tec de
Monterrey). Objetivo: mejorar la calidad del código **sin alterar su
comportamiento observable**.

| Módulo | Responsabilidad |
|---|---|
| `src/gestor.py` | Dominio: productos, ventas, cotización. Estado global `INVENTARIO`, `VENTAS`, contador de folios y `ultimo_error`. |
| `src/almacen.py` | Persistencia JSON (`guardar_datos`, `cargar_datos`). |
| `src/reportes.py` | Reportes: inventario, stock bajo, total vendido, más vendidos, resumen de ventas. |
| `src/main.py` | Menú interactivo de consola. |
| `tests/` | Pruebas de caja negra con pytest (`conftest.py` agrega `src/` al path). |

## Comandos
Usar siempre el intérprete del entorno virtual (Windows):

```powershell
.\.venv\Scripts\python -m pytest -q          # todas las pruebas deben pasar
.\.venv\Scripts\python -m ruff check src     # meta final: 0 errores
```

## Restricciones (obligatorias)
- **No modificar** nada en `tests/` ni el archivo `pyproject.toml`.
- No silenciar el linter con `# noqa` ni cambiando su configuración.
- No instalar ni actualizar dependencias sin autorización.
- Conservar las APIs públicas `agregarProducto` y `buscarProducto` (nombre y firma).
- No eliminar funciones públicas ni elementos potencialmente usados externamente
  solo porque los tests no los invoquen: justificar y pedir aprobación primero.
- No ejecutar `src/main.py` desde la raíz del repo (lee/escribe
  `datos_ejemplo.json`); hacerlo desde un directorio temporal.

## Preservación del comportamiento
Cualquier refactorización debe mantener idénticos:
- Cálculos: descuento por volumen (10% si subtotal >= 1000, 5% si >= 500),
  extra VIP de 2% (cliente que inicia con `"VIP"` y subtotal menos descuento > 200,
  solo en `registrar_venta`), IVA 16%, redondeos a 2 decimales y el **orden de
  las operaciones de punto flotante**.
- Folios consecutivos, descuento de stock y restauración del contador al cargar.
- Formato JSON: claves `inventario`, `ventas`, `contador`; `indent=2`,
  `ensure_ascii=False`.
- Retornos (`True`/`False`/`None`/`dict`/`list`/`str`) y claves del dict de venta.
- Mensajes de `ultimo_error` (p. ej. `"codigo vacio"`, `"producto no existe"`,
  `"cantidad invalida"`, `"stock insuficiente"`, `"archivo corrupto"`) y su orden
  de evaluación.
- Texto exacto de tickets, reportes y menú.

## Convenciones de Python
- PEP 8, `snake_case` para funciones y variables, constantes en `MAYUSCULAS`.
- Nombres descriptivos; nada de `temp2`, `aux`, `x`.
- Guard clauses en lugar de `if` anidados; funciones pequeñas y cohesivas
  (complejidad ciclomática <= 10).
- `with open(...)` para archivos; capturar excepciones específicas.
- Comentarios y docstrings en español, al estilo del código existente.

## Flujo de trabajo
1. Una sola refactorización a la vez.
2. Después de cada una: `pytest -q`, `ruff check src`, revisar `git diff`.
3. Registrar en `docs/bitacora.md`: prompt textual usado, cambios, justificación,
   salidas reales de pytest y ruff, errores detectados.
4. Pedir aprobación antes de cada `git commit` (un commit por refactorización)
   y antes de iniciar la siguiente refactorización.
5. Nunca reportar resultados que no se hayan ejecutado y verificado.
