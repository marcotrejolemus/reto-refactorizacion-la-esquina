# Bitácora de refactorización

**Nombre:** Marco Antonio Trejo Lemus
**Matrícula:** *(pendiente de confirmación institucional)*
**Fecha:** 2026-10-08 a 2026-10-11

Registro de cada refactorización realizada con Claude Code en la rama
`refactorizacion`. Cada prompt se resume fielmente; el texto completo de todos
los prompts, las salidas reales de `pytest` y `ruff check src`, los diffs y las
decisiones tomadas están en [`docs/bitacora.md`](docs/bitacora.md). Los scripts
y salidas de referencia de la caracterización están en
[`docs/evidencia/`](docs/evidencia/README.md).

Antes de refactorizar se configuró el proyecto para Claude Code (`CLAUDE.md` y
`.claudeignore`, commit `5d6389e`) y se registró la línea base: 20 pruebas
pasando y 20 errores de `ruff check src`.

| #  | Prompt usado | Cambio realizado | Justificación | Tests OK |
|----|--------------|------------------|---------------|----------|
| 1  | "Autorizo iniciar exclusivamente la refactorización #1 [...] corrigiendo las reglas UP009, F401 e I001 de Ruff [...] No elimines funciones, clases, constantes ni lógica de negocio." (P-03) | Se quitaron las declaraciones `# -*- coding: utf-8 -*-` de los 4 módulos, el `import os` sin uso de `reportes.py` y se ordenaron los imports de `main.py`. Commit `4cedd85` | En Python 3 la codificación por omisión ya es UTF-8; los imports sin uso o desordenados confunden sobre las dependencias reales. Ruff: 20 → 14 | Sí, 20/20 |
| 2  | "Autorizo iniciar exclusivamente la Refactorización #2: nombres descriptivos y constantes de negocio [...] Introducir constantes para descuentos, IVA y límites de stock sin alterar valores ni operaciones matemáticas." (P-04 a P-08; incluye revisar y aprobar los scripts de caracterización antes de ejecutarlos) | Renombres PEP 8 (`contador_ventas`, `hay_archivo`, `reporte_viejo_csv`, `formatear_moneda`), variables descriptivas en lugar de `temp2`, `aux`, `x`, y constantes `TASA_IVA`, umbrales y tasas de descuento, reglas VIP y `STOCK_MINIMO`. Commit `8b3a458` | Los nombres revelan intención y las reglas de negocio quedan definidas en un solo lugar. Ruff: 14 → 9 | Sí, 20/20; caracterización idéntica (SHA-256) |
| 3  | "Autorizo iniciar exclusivamente la Refactorización #3: mejora de la persistencia y administración segura de archivos [...] No cambies silenciosamente qué errores se capturan o propagan." (P-09 a P-11) | `with open(...)` en `guardar_datos`, `cargar_datos` y `reporte_viejo_csv`; se quitó el modo `"r"` redundante. Se conservó `except Exception` por decisión del usuario. Commit `e57285e` | El archivo se cierra siempre, aunque ocurra una excepción. Acotar a `ValueError` habría cambiado qué errores se propagan, por eso no se hizo. Ruff: 9 → 5 | Sí, 20/20; caracterización idéntica y JSON igual salvo `fecha` |
| 4  | "Autorizo iniciar exclusivamente la Refactorización #4: eliminación de cálculos duplicados y simplificación de lógica de negocio [...]" y después "No autorizo cambiar el tipo de excepción producido por `_es_cliente_vip()`." (P-12, P-13) | Se extrajeron `_descuento_por_volumen` (compartida por `registrar_venta` y `cotizar`) y `_es_cliente_vip` (mismas condiciones y mismo orden); se aplanaron los `if` anidados y `sorted()` reemplazó al ordenamiento de burbuja. Commit `3cbdccd` | Una sola definición del descuento evita que la cotización y la venta diverjan; menos anidamiento y complejidad; `sorted` es estable y conserva los empates. Ruff: 5 → 1 | Sí, 20/20; casos límite 499/500/999/1000 y VIP 200/201 idénticos |
| 5  | "Selecciono la opción (b) para la Refactorización #5: simplificar `menu()` y dividir `registrar_venta()` en funciones auxiliares. [...] Por ahora trabaja exclusivamente en modo planificación." (P-14 a P-20; plan técnico aprobado, Fase A y Fase B validadas por separado) | Fase A: `menu()` dividido en una función por opción y un diccionario de despacho. Fase B: `registrar_venta()` dividida en `_validar_venta`, `_calcular_montos` y `_armar_ticket`. Commit `bc0687c` | Funciones pequeñas con una sola responsabilidad y `registrar_venta` como orquestador legible. Las validaciones niegan la condición original completa para que `float("nan")` conserve su mensaje. Ruff: 1 → 0 | Sí, 20/20; 5 salidas de caracterización idénticas (SHA-256) |

**Resultado final:** 20/20 pruebas pasando y `ruff check src` → `All checks passed!`,
sin modificar `tests/` ni `pyproject.toml`.

## Reflexión final (10-15 líneas)

Responde: ¿Qué tan útil fue Claude Code para detectar y corregir los problemas?
¿Qué propuso la IA que tú no habías notado? ¿En qué casos tuviste que corregir
o rechazar sus sugerencias? ¿Qué aprendiste sobre refactorizar con apoyo de IA?

1. Durante este reto comprendí que Claude Code puede facilitar significativamente el análisis y la refactorización de código heredado.
2. Su principal aportación fue identificar problemas de legibilidad, duplicación y complejidad que inicialmente no había considerado.
3. Entre las mejoras destacaron la centralización de descuentos, el uso de `with open()` y la separación de responsabilidades.
4. Aprendí que mejorar la estructura interna del código no garantiza, por sí solo, conservar su comportamiento funcional.
5. Por ello, consideré indispensable ejecutar las 20 pruebas automatizadas después de cada refactorización.
6. También utilicé pruebas de caracterización y comparaciones SHA-256 para comprobar los resultados antes y después de los cambios.
7. En distintas ocasiones cuestioné propuestas de la IA que podían alterar las validaciones o el tratamiento original de excepciones.
8. Un ejemplo fue conservar `except Exception` y evitar cambios que modificaran el comportamiento ante valores especiales como `NaN`.
9. Asimismo, comprendí la importancia de revisar los scripts de prueba y los resultados generados por la propia inteligencia artificial.
10. La documentación de prompts, decisiones técnicas y commits me permitió mantener la trazabilidad de todo el proceso.
11. Mi principal aprendizaje fue reconocer que la responsabilidad de evaluar y aprobar los cambios sigue perteneciendo al desarrollador.
12. Concluyo que la IA acelera el desarrollo de software cuando se combina con pensamiento crítico, pruebas rigurosas y supervisión humana.
