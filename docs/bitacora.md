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
| 1  | P-03 (ver abajo) | Higiene: quitar declaraciones `coding` (UP009×4), `import os` sin uso en `reportes` (F401) y ordenar imports de `main` (I001) | Ruido innecesario en Python 3; imports sin uso y desordenados dificultan la lectura | 20 passed | 20 → 14 | *(pendiente de aprobación)* |
| 2  |              |                  |               |          |                |        |
| 3  |              |                  |               |          |                |        |
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

**Commit:** *(pendiente de aprobación)*
