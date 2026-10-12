# Evidencia de caracterización

Scripts y salidas de referencia usados para comprobar que cada refactorización
conservó el comportamiento observable del programa, además de las 20 pruebas de
`tests/`. El detalle de cada ejecución está en [`docs/bitacora.md`](../bitacora.md).

Estos archivos no forman parte del programa: `ruff check src` solo revisa `src/`
y `pytest` solo recolecta pruebas de `tests/`.

## Contenido

| Archivo | Qué es |
|---|---|
| `caracterizar.py` | Ejercita altas, búsquedas, stock, 24 ventas, cotizaciones, reportes, CSV heredado y persistencia JSON (guardar, cargar, archivo inexistente y corrupto). Escribe archivos temporales solo en el directorio de trabajo que recibe |
| `casos_limite.py` | Límites de descuento (499, 500, 999, 1000), límites VIP (200, 201) y empates en `mas_vendidos`. Solo en memoria |
| `casos_validacion.py` | Orden de validaciones de `registrar_venta` (incluye `nan`, `inf` y código no hashable), `ultimo_error`, stock, folios, claves de la venta y tickets. Solo en memoria |
| `menu_entrada.txt` | Entrada guionizada del menú: altas, ventas, cotización, reportes y salida |
| `menu_entrada_extra.txt` | Entrada guionizada del menú: opciones inválidas (`""`, `" 1"`, `"01"`, `"1 "`, `"x"`, `"9"`), reportes sin datos, errores y venta VIP. La línea `"1 "` termina en un espacio intencional |
| `linea_base_*.txt` | Salidas de referencia generadas antes de modificar el código |

## Salidas de referencia

| Archivo | Generada sobre | SHA-256 |
|---|---|---|
| `linea_base_caracterizacion.txt` | `4cedd85` | `A1968732D884E01470D103D3EF2475175A616FC538A3B2A1C93175DD929C4EF3` |
| `linea_base_menu.txt` | `4cedd85` | `FB264F9C0D47D6A500DFEAFE79C63C738D7A2586CD9C30783C8DAB3FEFC9EFEF` |
| `linea_base_limites.txt` | `e57285e` | `86A96A0740E91613BC7FF0EB2CFDE7FD9DF023A787AE107C6EE0BC3ACEDB817F` |
| `linea_base_menu_extra.txt` | `3cbdccd` | `1BB37F446F107523D0B86E09339F201C0192E44E22B5EC1C3D3010C4BC3D0601` |
| `linea_base_validacion.txt` | `3cbdccd` + Fase A de la #5 (sin cambios en `gestor.py`) | `3D9310C607F690227650D131D7156345552B6FCAE4BD59E19B64CC6772E0A065` |

Cada línea base se generó **antes** de la refactorización que debía validar y se
comparó contra la salida posterior. Todas las comparaciones fueron idénticas.

**Saltos de línea:** las salidas se generaron en Windows, donde Python escribe
CRLF, y los hashes corresponden a esa versión. Con `core.autocrlf=true`, git las
restaura con CRLF en Windows. En Linux o macOS se obtienen con LF y el hash
cambia; ahí compara el contenido con `diff --strip-trailing-cr` en lugar del hash.

## Cómo reproducir (Windows, desde la raíz del repositorio)

Las salidas se escriben en un directorio temporal para no modificar el
repositorio. `main.py` lee y escribe `datos_ejemplo.json` en el directorio
actual, por eso se ejecuta desde una carpeta temporal vacía.

```powershell
$py  = (Resolve-Path .\.venv\Scripts\python.exe).Path
$src = (Resolve-Path .\src).Path
$ev  = (Resolve-Path .\docs\evidencia).Path
$tmp = Join-Path $env:TEMP "la_esquina_evidencia"
New-Item -ItemType Directory -Force "$tmp\trabajo", "$tmp\menu", "$tmp\menu_extra" | Out-Null
$env:PYTHONIOENCODING = "utf-8"

cmd /c "`"$py`" -B `"$ev\caracterizar.py`" `"$src`" `"$tmp\trabajo`" > `"$tmp\caracterizacion.txt`""
cmd /c "`"$py`" -B `"$ev\casos_limite.py`" `"$src`" > `"$tmp\limites.txt`""
cmd /c "`"$py`" -B `"$ev\casos_validacion.py`" `"$src`" > `"$tmp\validacion.txt`""

Push-Location "$tmp\menu"
cmd /c "`"$py`" -B `"$src\main.py`" < `"$ev\menu_entrada.txt`" > `"$tmp\menu.txt`""
Pop-Location
Push-Location "$tmp\menu_extra"
cmd /c "`"$py`" -B `"$src\main.py`" < `"$ev\menu_entrada_extra.txt`" > `"$tmp\menu_extra.txt`""
Pop-Location

fc.exe /b "$ev\linea_base_caracterizacion.txt" "$tmp\caracterizacion.txt"
fc.exe /b "$ev\linea_base_limites.txt"         "$tmp\limites.txt"
fc.exe /b "$ev\linea_base_validacion.txt"      "$tmp\validacion.txt"
fc.exe /b "$ev\linea_base_menu.txt"            "$tmp\menu.txt"
fc.exe /b "$ev\linea_base_menu_extra.txt"      "$tmp\menu_extra.txt"
```

Cada `fc.exe /b` debe responder `FC: no differences encountered`.

- La entrada se redirige con `cmd /c ... < archivo` porque la tubería de
  Windows PowerShell 5.1 convierte el texto a ASCII y cambiaría "Café" por "Caf?".
- `-B` evita crear `__pycache__` dentro de `src/`.
- Los JSON que genera `main.py` y `caracterizar.py` no se incluyen como
  referencia porque contienen la fecha y hora de cada venta. En la bitácora se
  compararon excluyendo solo las líneas `"fecha"`.
