# Bitácora de refactorización

**Nombre:** Marco Trejo
**Matrícula:** *(por completar)*
**Fecha de inicio:** 2026-10-08
**Rama:** `refactorizacion` → `main`
**Herramienta:** Claude Code (modelo Claude Opus 5.5)

Cada refactorización se registra con el prompt utilizado, el cambio aplicado,
su justificación y la evidencia real de `pytest` y `ruff check src`.

## Resumen

| #  | Prompt usado | Cambio realizado | Justificación | Tests OK | Ruff (errores) | Commit |
|----|--------------|------------------|---------------|----------|----------------|--------|
| 0  | P-01, P-02 (ver abajo) | Configuración: `CLAUDE.md`, `.claudeignore`, `docs/bitacora.md`, `docs/reflexion.md` | Dar contexto y reglas a la IA antes de tocar código | 20 passed | 20 (sin cambios, `src/` intacto) | `5d6389e` |
| 1  | P-03 (ver abajo) | Higiene: quitar declaraciones `coding` (UP009×4), `import os` sin uso en `reportes` (F401) y ordenar imports de `main` (I001) | Ruido innecesario en Python 3; imports sin uso y desordenados dificultan la lectura | 20 passed | 20 → 14 | `4cedd85` |
| 2  | P-04 a P-08 (ver abajo) | Renombres PEP 8 (`contador_ventas`, `hay_archivo`, `reporte_viejo_csv`, `formatear_moneda`), variables descriptivas y constantes de negocio (descuentos, VIP, IVA, stock mínimo, formato de fecha) | Nombres que revelan intención; reglas de negocio con un solo punto de definición | 20 passed; caracterización idéntica (SHA-256) | 14 → 9 | `8b3a458` |
| 3  | P-09 (ver abajo) | `with open(...)` en `guardar_datos`, `cargar_datos` y `reporte_viejo_csv`; quitar el modo `"r"` redundante. `except Exception` se conserva (decisión del usuario) | Cierre garantizado de archivos aunque ocurra una excepción | 20 passed; caracterización idéntica (SHA-256) y JSON igual salvo `fecha` | 9 → 5 | *(pendiente de aprobación)* |
| 4  |              |                  |               |          |                |        |
| 5  |              |                  |               |          |                |        |

---

## Línea base (antes de cualquier cambio)

Comandos ejecutados el 2026-10-08 sobre el commit `a43153d`:

```text
> .\.venv\Scripts\python -m pytest -q
....................                                                     [100%]
20 passed in 0.04s

> .\.venv\Scripts\python -m ruff check src --statistics
4	UP009 	[*] utf8-encoding-declaration
3	SIM102	[ ] collapsible-if
3	SIM115	[ ] open-file-with-context-handler
2	C901  	[ ] complex-structure
2	N802  	[ ] invalid-function-name
1	SIM108	[ ] if-else-block-instead-of-if-exp
1	N816  	[ ] mixed-case-variable-in-global-scope
1	SIM103	[ ] needless-bool
1	UP015 	[*] redundant-open-modes
1	I001  	[*] unsorted-imports
1	F401  	[*] unused-import
Found 20 errors.
```

Detalle por ubicación (línea base):

```text
src\almacen.py:1:1: UP009 UTF-8 encoding declaration is unnecessary
src\almacen.py:16:9: SIM115 Use a context manager for opening files
src\almacen.py:30:9: SIM115 Use a context manager for opening files
src\almacen.py:30:20: UP015 Unnecessary mode argument
src\almacen.py:48:5: N802 Function name `hayArchivo` should be lowercase
src\almacen.py:50:5: SIM103 Return the condition `bool(os.path.exists(ruta))` directly
src\gestor.py:1:1: UP009 UTF-8 encoding declaration is unnecessary
src\gestor.py:15:1: N816 Variable `contadorVentas` in global scope should not be mixedCase
src\gestor.py:86:5: C901 `registrar_venta` is too complex (12 > 10)
src\gestor.py:120:9: SIM108 Use ternary operator ... instead of `if`-`else`-block
src\gestor.py:126:5: SIM102 Use a single `if` statement instead of nested `if` statements
src\gestor.py:127:9: SIM102 Use a single `if` statement instead of nested `if` statements
src\gestor.py:128:13: SIM102 Use a single `if` statement instead of nested `if` statements
src\main.py:1:1: UP009 UTF-8 encoding declaration is unnecessary
src\main.py:4:1: I001 Import block is un-sorted or un-formatted
src\main.py:21:5: C901 `menu` is too complex (17 > 10)
src\reportes.py:1:1: UP009 UTF-8 encoding declaration is unnecessary
src\reportes.py:4:8: F401 `os` imported but unused
src\reportes.py:83:5: N802 Function name `reporteViejoCSV` should be lowercase
src\reportes.py:86:9: SIM115 Use a context manager for opening files
```

---

## Fase 0 — Configuración inicial

### Prompts utilizados

**P-01 (diagnóstico y plan):**

> Actúa como un ingeniero senior de Python especializado en Clean Code, refactorización y calidad de software.
>
> Estoy realizando el reto académico "Refactorización Asistida por IA" del programa Next-Gen Coding del Tecnológico de Monterrey.
>
> Analiza el proyecto actual "La Esquina", incluyendo los módulos src/gestor.py, src/almacen.py, src/reportes.py, src/main.py, las pruebas de tests/ y el archivo pyproject.toml.
>
> Solicito:
> 1. Explicar brevemente la arquitectura actual y las responsabilidades de cada módulo.
> 2. Identificar los principales code smells, indicando su ubicación y consecuencias.
> 3. Proponer cinco refactorizaciones significativas, ordenadas de menor a mayor riesgo.
> 4. Justificar técnicamente cada refactorización.
> 5. Explicar cómo validar cada cambio mediante pytest y ruff check src.
> 6. Proponer criterios de aceptación verificables, preservando el comportamiento existente.
>
> Restricciones obligatorias:
> - No modificar archivos todavía.
> - No modificar tests/ ni pyproject.toml.
> - Conservar las APIs públicas agregarProducto y buscarProducto.
> - Mantener los cálculos de descuentos, IVA, folios, inventario y persistencia JSON.
> - Preservar formatos de reportes, tickets, retornos y mensajes de error.
> - No instalar dependencias sin autorización.
>
> Entrega una tabla con: número, archivo, problema identificado, refactorización propuesta, beneficio, riesgo y criterio de validación.
>
> Finaliza recomendando la primera refactorización a implementar y espera mi aprobación.

**P-02 (ajustes al plan y Fase 0):**

> El plan propuesto está aprobado conceptualmente, pero necesito incorporar los siguientes ajustes antes de iniciar su implementación:
>
> **1. Configuración inicial obligatoria** — Agregar una fase 0 para crear y revisar: CLAUDE.md con descripción del proyecto, convenciones Python, restricciones, comandos de pytest y Ruff y reglas de preservación del comportamiento; .claudeignore con las exclusiones solicitadas por la actividad, aclarando que no constituye por sí solo un control efectivo de acceso en Claude Code; docs/bitacora.md y docs/reflexion.md como documentos iniciales de trabajo. No modificar tests/ ni pyproject.toml.
>
> **2. Preservación del comportamiento** — No eliminar funciones públicas ni elementos potencialmente utilizados externamente solamente porque los tests actuales no los invoquen. Justificar cualquier eliminación de código muerto y solicitar mi aprobación.
>
> **3. Ejecución incremental obligatoria** — Ejecutar una sola refactorización a la vez. Después de cada refactorización: ejecutar python -m pytest -q; ejecutar python -m ruff check src; revisar git diff; documentar el prompt realmente utilizado, modificaciones, justificación, resultados de pruebas y errores detectados; solicitar mi aprobación antes de crear un commit; no comenzar la siguiente refactorización hasta recibir mi autorización.
>
> **4. Evidencia académica** — Conservar evidencia verificable de los cambios y de las pruebas realizadas. No generar resultados ficticios ni afirmar que Ruff está limpio antes de comprobarlo.
>
> **5. Ejecución controlada** — No implementar automáticamente las cinco refactorizaciones. Primero completar la fase 0 y detenerse para solicitar mi aprobación.
>
> Actualiza el plan incorporando estas instrucciones. No edites todavía el código fuente.

### Cambios realizados
- `CLAUDE.md`: descripción, módulos, comandos, restricciones, reglas de
  preservación del comportamiento, convenciones y flujo de trabajo.
- `.claudeignore`: `.venv/`, cachés (`__pycache__/`, `*.pyc`, `.pytest_cache/`,
  `.ruff_cache/`), `.env`, `.DS_Store`, `.git/` y datos generados. Incluye la
  aclaración de que no es un control de acceso efectivo (el control real es
  `permissions.deny` en `.claude/settings.json`, no creado sin autorización).
- `docs/bitacora.md` (este archivo) y `docs/reflexion.md` (esqueleto).
- **Sin cambios** en `src/`, `tests/` ni `pyproject.toml`.

### Justificación
`CLAUDE.md` le da a la IA el contexto y las reglas del reto en cada sesión,
reduciendo el riesgo de cambios que alteren el comportamiento o toquen archivos
prohibidos. `.claudeignore` documenta qué no aporta contexto útil (entornos,
cachés, datos generados). La bitácora y la reflexión son entregables del reto.

### Evidencia (2026-10-08, tras crear los archivos)

```text
> .\.venv\Scripts\python -m pytest -q
....................                                                     [100%]
20 passed in 0.03s

> .\.venv\Scripts\python -m ruff check src --statistics
(mismos 20 errores de la línea base: UP009×4, SIM102×3, SIM115×3, C901×2,
 N802×2, SIM108, N816, SIM103, UP015, I001, F401)
Found 20 errors.
```

### Observaciones / errores detectados
- El README pide `BITACORA.md` en la raíz; por instrucción del usuario se usa
  `docs/bitacora.md`. Pendiente decidir si se copia también a la raíz al final.
- Sin errores en la fase.

**Commit:** `5d6389e` — `chore: agregar configuración de Claude Code y documentos de trabajo`
(archivos: `.claudeignore`, `CLAUDE.md`, `docs/bitacora.md`, `docs/reflexion.md`).

---

## Refactorización #1 — Higiene de código e imports (UP009, F401, I001)

### Prompt utilizado

**P-03:**

> Autorizo iniciar exclusivamente la refactorización #1 del plan aprobado.
>
> Objetivo: mejorar la higiene del código y la organización de imports, corrigiendo las reglas UP009, F401 e I001 de Ruff.
>
> Instrucciones:
> 1. Identifica los archivos y líneas que requieren cambios.
> 2. Elimina únicamente declaraciones de codificación innecesarias e imports sin utilizar.
> 3. Ordena los imports conforme a las convenciones de Python.
> 4. No elimines funciones, clases, constantes ni lógica de negocio.
> 5. No modifiques tests/ ni pyproject.toml.
> 6. No cambies las interfaces públicas ni el comportamiento observable.
>
> Después de realizar los cambios:
> - Ejecuta python -m pytest -q.
> - Ejecuta python -m ruff check src --statistics.
> - Ejecuta git diff para mostrar las diferencias.
> - Actualiza docs/bitacora.md con el prompt utilizado, los cambios, la justificación y los resultados reales de ambas validaciones.
> - Registra también el commit de la Fase 0: 5d6389e.
>
> No realices todavía el commit de la refactorización #1.
>
> Detente al finalizar y espera mi aprobación antes de continuar con cualquier otra refactorización.

### Cambios realizados
Las modificaciones se hicieron a mano con ediciones puntuales; no se usó `ruff --fix`.

| Archivo | Línea original | Regla | Cambio |
|---|---|---|---|
| `src/gestor.py` | 1 | UP009 | Eliminada `# -*- coding: utf-8 -*-` |
| `src/almacen.py` | 1 | UP009 | Eliminada `# -*- coding: utf-8 -*-` |
| `src/reportes.py` | 1 | UP009 | Eliminada `# -*- coding: utf-8 -*-` |
| `src/reportes.py` | 4 | F401 | Eliminado `import os` (no se usa en el módulo) |
| `src/main.py` | 1 | UP009 | Eliminada `# -*- coding: utf-8 -*-` |
| `src/main.py` | 4-6 | I001 | Imports ordenados alfabéticamente: `almacen`, `gestor`, `reportes` |

No se eliminaron funciones, clases, constantes ni lógica. `tests/` y
`pyproject.toml` sin cambios. `git diff --stat`: 4 archivos, 1 inserción, 7 eliminaciones.

### Justificación
- **UP009:** en Python 3 la codificación por defecto del código fuente es UTF-8
  (PEP 3120), así que la declaración es redundante.
- **F401:** un import sin uso confunde sobre las dependencias reales del módulo
  y agrega una carga innecesaria.
- **I001:** un orden consistente de imports (isort) facilita la lectura y
  reduce conflictos en los merges.
- **Comportamiento:** reordenar los imports de `main` no cambia nada porque
  ninguno de los tres módulos tiene efectos secundarios al importarse que
  dependan del orden (`almacen` y `reportes` ya importan `gestor` por su cuenta).
  `os` no se usaba en `reportes`, lo que ruff confirma con F401.

### Evidencia (2026-10-08)

```text
> .\.venv\Scripts\python -m pytest -q
....................                                                     [100%]
20 passed in 0.04s

> .\.venv\Scripts\python -m ruff check src --statistics
3	SIM102	[ ] collapsible-if
3	SIM115	[ ] open-file-with-context-handler
2	C901  	[ ] complex-structure
2	N802  	[ ] invalid-function-name
1	SIM108	[ ] if-else-block-instead-of-if-exp
1	N816  	[ ] mixed-case-variable-in-global-scope
1	SIM103	[ ] needless-bool
1	UP015 	[*] redundant-open-modes
Found 14 errors.
```

```diff
--- a/src/almacen.py
+++ b/src/almacen.py
-# -*- coding: utf-8 -*-
 """Persistencia del gestor: carga y guardado de datos en JSON."""
--- a/src/gestor.py
+++ b/src/gestor.py
-# -*- coding: utf-8 -*-
 """Modulo principal del gestor de inventario y ventas de "La Esquina".
--- a/src/main.py
+++ b/src/main.py
-# -*- coding: utf-8 -*-
 """Punto de entrada del gestor de tienda (menu interactivo en consola)."""
 
-import gestor
 import almacen
+import gestor
 import reportes
--- a/src/reportes.py
+++ b/src/reportes.py
-# -*- coding: utf-8 -*-
 """Reportes de la tienda: inventario, ventas y mas vendidos."""
 
-import os
-
 import gestor
```

### Observaciones / errores detectados
- Las 6 infracciones objetivo (UP009×4, F401, I001) desaparecieron; las otras
  14 siguen igual, con los números de línea desplazados en -1 (o -3 en
  `reportes.py` a partir de la línea 4).
- Git avisa que los saltos de línea LF pasarán a CRLF (configuración de Git en
  Windows); el contenido no cambia.
- Sin errores en la fase.

**Commit:** `4cedd85` — `refactor: eliminar declaraciones de codificación e imports sin uso y ordenar imports`

---

## Refactorización #2 — Nombres descriptivos y constantes de negocio

### Prompts utilizados

**P-04 (autorización inicial):**

> Autorizo iniciar exclusivamente la Refactorización #2: nombres descriptivos y constantes de negocio.
>
> Apruebo los renombres propuestos:
> - contadorVentas → contador_ventas
> - hayArchivo → hay_archivo
> - reporteViejoCSV → reporte_viejo_csv
>
> Antes de aplicarlos, identifica todas sus referencias en el proyecto y documenta cualquier impacto potencial de compatibilidad. Actualiza las referencias internas correspondientes.
>
> Condiciones obligatorias:
> 1. Mantener agregarProducto y buscarProducto sin cambios de nombre ni firma.
> 2. Sustituir variables poco descriptivas por nombres significativos.
> 3. Introducir constantes para las reglas de descuentos, IVA y stock.
> 4. Conservar exactamente los valores, cálculos, retornos y formatos actuales.
> 5. No eliminar código heredado durante esta etapa.
> 6. No modificar tests/ ni pyproject.toml.
> 7. No iniciar ninguna otra refactorización.
>
> Al terminar:
> - Ejecuta las 20 pruebas con pytest.
> - Ejecuta Ruff y registra el número real de errores restantes.
> - Revisa y presenta git diff.
> - Actualiza docs/bitacora.md con el prompt, modificaciones, justificación y resultados reales.
> - Detente antes del commit y solicita mi aprobación.
>
> No continúes con la Refactorización #3 sin mi autorización.

**P-05 (revisión de los scripts de caracterización antes de ejecutarlos):**

> Antes de autorizar la ejecución de las pruebas de caracterización, muéstrame el contenido completo de los archivos caracterizar.py y menu_entrada.txt que pretendes utilizar.
>
> Explica qué operaciones realizarán, qué archivos crearán o modificarán y cómo garantizas que no se alterará el proyecto original.
>
> No ejecutes todavía estos scripts ni modifiques archivos de src/, tests/ o pyproject.toml.
>
> Una vez revisado el contenido, te autorizaré continuar.

**P-06 (autorización de la caracterización inicial):**

> He revisado los scripts caracterizar.py y menu_entrada.txt.
>
> Autorizo ejecutar las pruebas de caracterización sobre el código actual, utilizando exclusivamente los directorios temporales indicados.
>
> Instrucciones:
>
> 1. Ejecuta la caracterización inicial y conserva los resultados como línea base.
> 2. Confirma que las salidas se guardaron correctamente y que el repositorio Git permanece limpio.
> 3. Documenta cualquier error de ejecución o codificación UTF-8.
> 4. No modifiques src/, tests/ ni pyproject.toml durante esta ejecución.
> 5. No inicies todavía la Refactorización #2.
>
> Presenta los resultados y espera mi autorización antes de modificar el código.

**P-07 (verificación con comandos simples, tras un comando rechazado):**

> La verificación anterior fue rechazada porque Claude Code detectó un error de sintaxis en PowerShell: "Missing closing ')' in expression".
>
> Por favor, realiza las verificaciones con comandos simples, separados y sin subexpresiones complejas.
>
> 1. Confirma que las ejecuciones iniciales de caracterizar.py y main.py terminaron correctamente. Revisa los códigos de salida y los archivos de errores.
> 2. Verifica que existen antes_caracterizacion.txt y antes_menu.txt y que contienen resultados válidos.
> 3. Calcula el hash SHA-256 de cada archivo con comandos Get-FileHash separados.
> 4. Ejecuta git status --short para comprobar que el repositorio permanece limpio.
> 5. Comprueba que datos_ejemplo.json no presenta modificaciones.
> 6. Confirma que src/, tests/ y pyproject.toml permanecen sin cambios.
>
> No repitas las pruebas si ya terminaron correctamente.
>
> No modifiques código fuente ni inicies todavía la Refactorización #2.
>
> Presenta un resumen de los resultados y espera mi aprobación.

**P-08 (autorización de la implementación):**

> Autorizo iniciar exclusivamente la Refactorización #2: nombres descriptivos y constantes de negocio, conforme al plan aprobado.
>
> Utiliza los resultados de caracterización que acabamos de generar como línea base.
>
> Condiciones:
> 1. Mantener las funciones públicas agregarProducto y buscarProducto sin cambios de nombre.
> 2. Realizar los renombres aprobados y actualizar sus referencias internas. Documentar cualquier incompatibilidad potencial con consumidores externos.
> 3. Sustituir variables poco descriptivas por nombres significativos.
> 4. Introducir constantes para descuentos, IVA y límites de stock sin alterar valores ni operaciones matemáticas.
> 5. Conservar los comportamientos identificados de ultimo_error, el valor entero 0 del descuento y las condiciones VIP.
> 6. No eliminar funciones heredadas ni modificar tests/ o pyproject.toml.
> 7. No comenzar la Refactorización #3.
>
> Al finalizar:
> - Ejecuta pytest.
> - Ejecuta Ruff.
> - Repite ambas pruebas de caracterización.
> - Compara los resultados posteriores contra los archivos originales utilizando sus contenidos o hashes SHA-256.
> - Documenta cualquier diferencia, incluso si parece menor.
> - Revisa git diff y actualiza docs/bitacora.md.
>
> Detente antes del commit y espera mi autorización.

### Inventario de referencias e impacto de compatibilidad

Búsqueda realizada antes de editar (`src/`, `tests/`, raíz; excluido `.venv/`):

| Nombre anterior | Nombre nuevo | Referencias internas actualizadas | En `tests/` | Impacto externo potencial |
|---|---|---|---|---|
| `gestor.contadorVentas` | `gestor.contador_ventas` | `gestor.py` (6), `almacen.py` (2) | No | Código externo que lea o escriba `gestor.contadorVentas` dejaría de ver el folio real (lectura: `AttributeError`; escritura: crearía un atributo nuevo sin efecto). La clave JSON `"contador"` **no cambia**, así que los archivos guardados siguen siendo compatibles. |
| `almacen.hayArchivo` | `almacen.hay_archivo` | `main.py:22` | No | Llamadas externas a `hayArchivo` lanzarían `AttributeError`. |
| `reportes.reporteViejoCSV` | `reportes.reporte_viejo_csv` | Ninguna (no se llama en el proyecto) | No | Llamadas externas lanzarían `AttributeError`. La función **se conserva**. |
| `reportes.hacer_cosa` | `reportes.formatear_moneda` | `reportes.py` (4 usos) | No | Llamadas externas lanzarían `AttributeError`. Renombre incluido en el plan aprobado (v2, paso 2). |

No se agregaron alias con el nombre viejo: un alias en camelCase volvería a
activar N802/N816 y el reto exige `ruff check src` sin errores.

### Cambios realizados

**`src/gestor.py`**
- Constantes nuevas (mismos valores literales que antes): `UMBRAL_DESCUENTO_ALTO = 1000`,
  `TASA_DESCUENTO_ALTO = 0.10`, `UMBRAL_DESCUENTO_MEDIO = 500`,
  `TASA_DESCUENTO_MEDIO = 0.05`, `PREFIJO_VIP = "VIP"`, `MONTO_MINIMO_VIP = 200`,
  `TASA_DESCUENTO_VIP = 0.02`, `TASA_IVA = 0.16`, `FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"`.
- `contadorVentas` → `contador_ventas`.
- Variables: `x` → `producto`, `aux` → `nuevo_stock` / `subtotal`, `temp2` → `encontrados` / `producto`,
  `k` → `codigo`, `desc` → `descuento`, `t` → `ticket`.
- La condición VIP pasa de `len(cliente) >= 3` y `cliente[0:3] == "VIP"` a
  `len(cliente) >= len(PREFIJO_VIP)` y `cliente[0:len(PREFIJO_VIP)] == PREFIJO_VIP`
  (equivalente, porque `len("VIP") == 3`).
- Se conservan: la estructura de `if` anidados (se atiende en #4/#5), `descuento = 0`
  como **entero**, la condición estricta `> MONTO_MINIMO_VIP`, el orden de las
  operaciones (`base * TASA_IVA`, `round(base + impuesto, 2)`, `base + base * TASA_IVA`
  en `cotizar`) y el comportamiento de `ultimo_error` (no se limpia en operaciones exitosas).
- **Sin cambios**: `calcular_descuento_viejo`, `exportar_txt` (comentado) y `MODO_DEBUG`,
  por ser código heredado (no se le introdujeron constantes para no alterarlo).

**`src/almacen.py`**: `d` → `datos`, `f` → `archivo`, `k` → `codigo`, `v` → `venta`;
`gestor.contadorVentas` → `gestor.contador_ventas`; `hayArchivo` → `hay_archivo` con
`return os.path.exists(ruta)` (SIM103; `os.path.exists` ya regresa `bool`). El `open`
sin `with` y el `except Exception` se dejan para la #3.

**`src/reportes.py`**: constante `STOCK_MINIMO = 5` (usada en `productos_stock_bajo` y
`reporte_inventario`); `hacer_cosa(v)` → `formatear_moneda(valor)`;
`reporteViejoCSV` → `reporte_viejo_csv`; variables `s` → `texto`, `t` → `total`,
`aux` → `valor_total` / `unidades_por_codigo`, `temp` → `ranking`, `p` → `producto`,
`v` → `venta`. Algunas concatenaciones se partieron en dos líneas por el límite de
88 caracteres; el texto resultante es el mismo. El ordenamiento de burbuja se conserva (#4).

**`src/main.py`**: `hayArchivo` → `hay_archivo`; variables `temp2` → `respuesta`,
`op` → `opcion`, `c/n/p/s` → `codigo/nombre/precio/stock`, `cant` → `cantidad`,
`cli` → `cliente`, `v` → `venta`, `t` → `total`, `bajos` → `productos_bajos`;
`par[0], par[1]` → desempaquetado `codigo, unidades`.

`git diff --stat`: 4 archivos de `src/`, 196 inserciones y 172 eliminaciones.
`tests/`, `pyproject.toml` y `datos_ejemplo.json` sin cambios.

### Justificación
- **Nombres:** `temp2`, `aux`, `x` o `hacer_cosa` no dicen qué contienen o qué hacen;
  nombres como `subtotal`, `nuevo_stock` o `formatear_moneda` hacen el código legible
  sin necesidad de comentarios. Los renombres cumplen PEP 8 (N802, N816).
- **Constantes:** las reglas de negocio (umbrales, tasas, IVA, prefijo VIP, stock
  mínimo) estaban como números mágicos repetidos en `registrar_venta`, `cotizar` y
  `reportes`. Al nombrarlas se documenta su significado y queda un solo punto para
  cambiarlas, lo que también prepara la extracción de la lógica duplicada en la #4.
- **Seguridad del cambio:** las constantes tienen exactamente los mismos valores
  literales y se usan en las mismas posiciones de cada expresión, por lo que la
  aritmética de punto flotante es idéntica.

### Evidencia (2026-10-09)

```text
> .\.venv\Scripts\python -m pytest -q
....................                                                     [100%]
20 passed in 0.07s

> .\.venv\Scripts\python -m ruff check src --statistics
3	SIM102	[ ] collapsible-if
3	SIM115	[ ] open-file-with-context-handler
2	C901  	[ ] complex-structure
1	UP015 	[*] redundant-open-modes
Found 9 errors.

> .\.venv\Scripts\python -m ruff check src --output-format concise
src\almacen.py:15:15: SIM115 Use a context manager for opening files
src\almacen.py:29:15: SIM115 Use a context manager for opening files
src\almacen.py:29:26: UP015 [*] Unnecessary mode argument
src\gestor.py:98:5: C901 `registrar_venta` is too complex (12 > 10)
src\gestor.py:138:5: SIM102 Use a single `if` statement instead of nested `if` statements
src\gestor.py:139:9: SIM102 Use a single `if` statement instead of nested `if` statements
src\gestor.py:140:13: SIM102 Use a single `if` statement instead of nested `if` statements
src\main.py:20:5: C901 `menu` is too complex (17 > 10)
src\reportes.py:91:15: SIM115 Use a context manager for opening files
Found 9 errors.
```

#### Caracterización (fuera del repositorio, en el directorio temporal de la sesión)

Scripts: `caracterizar.py` (ejercita las APIs y reportes en memoria y escribe en un
directorio de trabajo temporal) y `menu_entrada.txt` (entrada guionizada para
`main.py`, ejecutado con el directorio actual en una carpeta temporal). Ejecución con
`python -B`, `PYTHONIOENCODING=utf-8` y redirección `cmd /c ... < archivo` para no
perder caracteres UTF-8.

| Salida | Antes (`4cedd85`) SHA-256 | Después SHA-256 | Resultado |
|---|---|---|---|
| `caracterizacion.txt` (59 líneas) | `A1968732D884E01470D103D3EF2475175A616FC538A3B2A1C93175DD929C4EF3` | `A1968732D884E01470D103D3EF2475175A616FC538A3B2A1C93175DD929C4EF3` | Idéntico (`fc /b`: no differences) |
| `menu.txt` (167 líneas) | `FB264F9C0D47D6A500DFEAFE79C63C738D7A2586CD9C30783C8DAB3FEFC9EFEF` | `FB264F9C0D47D6A500DFEAFE79C63C738D7A2586CD9C30783C8DAB3FEFC9EFEF` | Idéntico (`fc /b`: no differences) |
| `viejo.csv` | — | — | Idéntico (`fc /b`: no differences) |
| `datos_ejemplo.json` generado por el menú | — | — | Solo difiere el campo `fecha` (marca de tiempo de cada ejecución: `2026-10-08 23:48:25` vs `2026-10-09 00:06:06`); el resto es igual |

Códigos de salida: 0 en las cuatro ejecuciones; archivos de error (stderr) de 0 bytes.

### Observaciones / errores detectados
- **SIM108 desapareció sin que se cambiara la estructura.** Ruff no sugiere el operador
  ternario cuando la línea resultante pasaría de 88 caracteres; con los nombres nuevos
  (`descuento = subtotal * TASA_DESCUENTO_MEDIO if subtotal >= UMBRAL_DESCUENTO_MEDIO else 0`)
  quedaría de unos 91. El code smell (`else:` con un `if` anidado) **sigue presente** y se
  atenderá en la #4. Por eso la reducción real fue de 5 errores (N816, N802×2, SIM103,
  SIM108) y no de 4 como se había estimado.
- Durante la caracterización inicial se rechazó un comando de verificación por un error
  de sintaxis de PowerShell (`Missing closing ')' in expression`); se rehízo con
  comandos simples y separados (P-07). No afectó a los resultados.
- `src/__pycache__/` existe, generado por `pytest` (que no usa `-B`); está en
  `.gitignore` y no forma parte del proyecto.
- Git avisa que los saltos de línea LF pasarán a CRLF; el contenido no cambia.

**Commit:** `8b3a458` — `refactor: usar nombres descriptivos y constantes para reglas de negocio`

---

## Refactorización #3 — Persistencia y administración segura de archivos

### Prompt utilizado

**P-09:**

> Autorizo iniciar exclusivamente la Refactorización #3: mejora de la persistencia y administración segura de archivos.
>
> **Objetivo:**
> Refactorizar el manejo de archivos en src/almacen.py y src/reportes.py utilizando gestores de contexto `with open()` y mejorando el manejo de excepciones cuando sea seguro.
>
> **Instrucciones:**
>
> 1. Identifica los bloques que utilizan open() y close() manualmente.
> 2. Sustitúyelos por gestores de contexto para garantizar el cierre adecuado de archivos.
> 3. Revisa el uso de `except Exception` y determina qué excepciones específicas pueden utilizarse sin cambiar el comportamiento contratado.
> 4. Conserva exactamente los mensajes de error, valores de retorno, estructura JSON, indentación, codificación UTF-8 y formato CSV.
> 5. Mantén las claves JSON originales: inventario, ventas y contador.
> 6. Conserva las funciones públicas y el contador de folios.
> 7. No modifiques tests/ ni pyproject.toml.
> 8. No realices modificaciones fuera de esta refactorización.
>
> **Validación obligatoria:**
>
> - Ejecutar pytest: deben aprobarse las 20 pruebas.
> - Ejecutar Ruff y reportar el número real de errores restantes.
> - Repetir las pruebas de caracterización utilizando los mismos escenarios.
> - Comparar JSON, CSV, reportes y resultados con la línea base.
> - Verificar que las únicas diferencias admisibles sean marcas de tiempo generadas dinámicamente.
> - Mostrar git diff.
> - Actualizar docs/bitacora.md con los prompts, cambios, justificaciones, resultados y el commit anterior `8b3a458`.
>
> **Importante:**
>
> No cambies silenciosamente qué errores se capturan o propagan. Si una mejora en el manejo de excepciones modifica el comportamiento anterior, explícame la diferencia y solicita aprobación antes de aplicarla.
>
> No realices el commit de la Refactorización #3.
>
> Detente al terminar las verificaciones y espera mi aprobación antes de continuar.

### Bloques identificados con `open()`/`close()` manual

| Ubicación (en `8b3a458`) | Función | Problema |
|---|---|---|
| `src/almacen.py:15-17` | `guardar_datos` | Si `json.dump` falla, el archivo queda abierto (SIM115). |
| `src/almacen.py:29-36` | `cargar_datos` | Dos `close()` manuales (uno en el `except`), modo `"r"` redundante (SIM115, UP015). |
| `src/reportes.py:91-99` | `reporte_viejo_csv` | Si una escritura falla, el archivo queda abierto (SIM115). |

### Análisis de `except Exception` (`src/almacen.py`, `cargar_datos`)

El `try` solo protege a `json.load(archivo)`. El `open()` está **fuera** del `try`, así que
errores al abrir (permisos, ruta que es un directorio) ya se propagaban y se siguen propagando.

| Excepción que puede lanzar `json.load` | ¿Es `ValueError`? | Hoy (`except Exception`) | Con `except ValueError` |
|---|---|---|---|
| `json.JSONDecodeError` (JSON inválido) | Sí | `False` + `"archivo corrupto"` | Igual |
| `UnicodeDecodeError` (bytes no UTF-8) | Sí | `False` + `"archivo corrupto"` | Igual |
| `RecursionError` (anidamiento extremo) | No | `False` + `"archivo corrupto"` | **Se propaga** |
| `OSError` al leer (fallo de disco) | No | `False` + `"archivo corrupto"` | **Se propaga** |
| `MemoryError` (archivo enorme) | No | `False` + `"archivo corrupto"` | **Se propaga** |

**Decisión:** acotar a `ValueError` cambiaría el comportamiento en los tres últimos casos,
así que **no se aplicó**. Ruff no marca `except Exception` con las reglas configuradas, así
que conservarlo no impide llegar a 0 errores.

**Decisión del usuario (P-11):** conservar `except Exception` para no alterar qué errores
se capturan o se propagan.

### Cambios realizados
- `guardar_datos`: `open`/`close` → `with open(ruta, "w", encoding="utf-8") as archivo:`.
  Se conservan `indent=2`, `ensure_ascii=False`, las claves `inventario`, `ventas` y
  `contador`, y el retorno `True`.
- `cargar_datos`: `with open(ruta, encoding="utf-8") as archivo:` con el `try/except`
  dentro; se quitan los dos `close()` manuales y el modo `"r"` (es el modo por omisión).
  Mismo orden: verificación de existencia → lectura → `"archivo corrupto"` → carga
  del estado y del contador de folios.
- `reporte_viejo_csv`: `open`/`close` → `with open(...)`; mismo encabezado, mismas
  líneas y mismo retorno `ruta`.
- `git diff --stat`: 2 archivos (`src/almacen.py`, `src/reportes.py`).

### Justificación
`with` garantiza que el archivo se cierre (y su búfer se escriba en disco) aunque
ocurra una excepción, sin depender de `close()` manuales repetidos en cada camino.
Es la forma idiomática en Python y elimina el riesgo de fugas de descriptores.

**Diferencia de comportamiento documentada (no contractual):** si `json.dump` o una
escritura del CSV fallaran a mitad de camino (por ejemplo, `TypeError` por un valor no
serializable), antes el archivo quedaba abierto hasta que lo recolectara el recolector
de basura; ahora se cierra de inmediato. En ambos casos la excepción se propaga igual y
el archivo queda incompleto. Los retornos y mensajes no cambian.

### Evidencia (2026-10-09)

```text
> .\.venv\Scripts\python -m pytest -q
....................                                                     [100%]
20 passed in 0.06s

> .\.venv\Scripts\python -m ruff check src --statistics
3	SIM102	collapsible-if
2	C901  	complex-structure
Found 5 errors.

> .\.venv\Scripts\python -m ruff check src --output-format concise
src\gestor.py:98:5: C901 `registrar_venta` is too complex (12 > 10)
src\gestor.py:138:5: SIM102 Use a single `if` statement instead of nested `if` statements
src\gestor.py:139:9: SIM102 Use a single `if` statement instead of nested `if` statements
src\gestor.py:140:13: SIM102 Use a single `if` statement instead of nested `if` statements
src\main.py:20:5: C901 `menu` is too complex (17 > 10)
Found 5 errors.
```

#### Caracterización (mismos escenarios y scripts que en la #2; línea base de `4cedd85`)

| Salida | SHA-256 línea base | SHA-256 después de la #3 | Resultado |
|---|---|---|---|
| `caracterizacion.txt` | `A1968732D884E01470D103D3EF2475175A616FC538A3B2A1C93175DD929C4EF3` | `A1968732D884E01470D103D3EF2475175A616FC538A3B2A1C93175DD929C4EF3` | Idéntico |
| `menu.txt` | `FB264F9C0D47D6A500DFEAFE79C63C738D7A2586CD9C30783C8DAB3FEFC9EFEF` | `FB264F9C0D47D6A500DFEAFE79C63C738D7A2586CD9C30783C8DAB3FEFC9EFEF` | Idéntico |
| `viejo.csv` | — | — | Idéntico (`fc /b`: no differences) |
| `datos.json` (guardado por el script, 258 líneas) | — | — | Solo difieren las 17 líneas `fecha`; sin ellas, 241 = 241 líneas y 0 diferencias |
| `datos_ejemplo.json` (guardado por el menú) | — | — | Solo difieren las 2 líneas `fecha`; sin ellas, 43 = 43 líneas y 0 diferencias |

`caracterizacion.txt` incluye además: la recarga (5 productos y 17 ventas), el folio
siguiente (18), `"el archivo no existe"` y el JSON corrupto (`False`, `"archivo corrupto"`),
todos iguales a la línea base. Códigos de salida 0 y stderr de 0 bytes en ambas ejecuciones.

### Observaciones / errores detectados
- Las únicas diferencias encontradas son las marcas de tiempo `fecha`, generadas con
  `datetime.now()` en cada venta.
- `except Exception` se conserva por decisión del usuario (ver arriba).
- Antes del commit se hizo una revisión final (P-10): archivos modificados,
  `git diff --check` sin problemas, `pytest` 20 passed y `ruff` 5 errores, ejecutados de nuevo.
- Prompts posteriores a P-09:
  - **P-10:** "Gracias. Antes de autorizar el commit de la Refactorización #3, realiza una
    revisión final. Confirma que únicamente se modificaron: src/almacen.py, src/reportes.py,
    docs/bitacora.md. Verifica que tests/, pyproject.toml y datos_ejemplo.json siguen sin
    modificaciones. Confirma los resultados de pytest (20/20), Ruff (5 errores restantes),
    las comparaciones funcionales y que las únicas diferencias de los JSON corresponden a
    los valores dinámicos de fecha. Ejecuta git status y git diff --check. Presenta un
    resumen final y detente antes del commit. No inicies todavía la Refactorización #4."
  - **P-11:** "Conserva except Exception y crea el commit con el mensaje propuesto"
- Sin errores en la fase. `tests/`, `pyproject.toml` y `datos_ejemplo.json` sin cambios.

**Commit:** *(pendiente de aprobación)*
