# Guía de Usuario Unificada
## Compilador Fangless Python → C++

Esta guía reúne en un solo documento cómo instalar, usar, probar y presentar el proyecto. Está pensada para estudiantes, evaluadores y cualquier persona que quiera ejecutar el compilador sin revisar varios archivos por separado.

---

## 1. ¿Qué es este proyecto?

Fangless Python es un compilador simplificado que lee código con sintaxis parecida a Python, lo analiza y puede **transpilarlo a C++** con tipado dinámico mediante la clase `PyValue`.

El flujo completo es:

```text
archivo fuente → lexer → tokens → parser → AST → transpilador → C++ → g++ → ejecutable
```

El proyecto se divide en tres etapas:

| Etapa | Qué hace | Herramienta principal |
|-------|----------|------------------------|
| 1–2 | Análisis léxico y sintáctico (tokens + AST) | `src/main.py` |
| 3 | Generación de código C++ | `src/transpile.py` o `src/main.py --codegen` |
| Extra | Benchmarks y demostraciones | `benchmarks/` y `demos/` |

---

## 2. Requisitos

- **Python 3.8 o superior**
- **PLY** (biblioteca de lexer/parser)
- **matplotlib** (solo para gráficos de benchmarks)
- **Compilador C++17** en el PATH (`g++` recomendado)

### Instalación

Desde la raíz del proyecto:

```bash
pip install -r requirements.txt
```

En Windows, si `python` no funciona, usa `py` en su lugar:

```bash
py -m pip install -r requirements.txt
```

---

## 3. Estructura del proyecto

```text
src/
  main.py              # Entrada principal (lexer, parser, codegen)
  transpile.py         # CLI solo para transpilar a C++
  lexer/               # Análisis léxico
  parser/              # Gramática y AST
  codegen/             # Runtime PyValue y emisor C++

benchmarks/
  fangless/            # Programas Fangless para medir rendimiento
  handwritten_cpp/     # Referencia C++ nativa
  results/             # CSV, gráficos, informes PDF

demos/
  demo_*.py            # 5 programas para defensa/presentación
  run_demos.py         # Ejecuta demos automáticamente

tests/
  runtime/             # Prueba del runtime C++
  codegen/             # Pruebas end-to-end del transpilador
  transpile/           # Pruebas de errores de transpilación

Casos de prueba/       # Casos del parser (por categoría)
Test Files/            # Scripts de prueba adicionales
```

---

## 4. Uso básico: lexer y parser

Para ver los **tokens** y el **árbol sintáctico (AST)** de un archivo:

```bash
py src/main.py "Casos de prueba/Parser/parser_part1.fpy"
```

### Ejemplo de salida

Para el código `x = 5 + 3`, el AST se muestra así:

```text
Program
└── Assignment (=)
    ├── Identifier (x)
    └── BinaryOperation (+)
        ├── IntegerLiteral (5)
        └── IntegerLiteral (3)
```

### Comportamiento ante errores

- Si hay **error léxico**, el parser no se ejecuta.
- Si hay **error de sintaxis**, se muestra línea, columna y token cuando es posible.
- Si el archivo termina de forma incompleta, se reporta fin de entrada inesperado.

Ejemplos de errores detectados:

| Código problemático | Tipo de error |
|---------------------|---------------|
| `x = "bad\q"` | Secuencia de escape inválida |
| `x =` | Expresión incompleta |
| `x = * 5` | Operador mal ubicado |

---

## 5. Transpilación a C++

### Opción A: CLI dedicado

```bash
py src/transpile.py "Test Files/test_function.py" "Test Files/test_function.cpp"
g++ -std=c++17 "Test Files/test_function.cpp" -o "Test Files/test_function.exe"
Test Files\test_function.exe
```

### Opción B: Todo en un comando (recomendado para demos)

```bash
py src/main.py --codegen --compile --run --output salida.cpp "Test Files/test_function.py"
```

Flags disponibles:

| Flag | Descripción |
|------|-------------|
| `--codegen` | Genera C++ en lugar de mostrar el AST |
| `--output archivo.cpp` | Guarda el C++ en un archivo |
| `--compile` | Compila con `g++` |
| `--run` | Ejecuta el programa compilado |

### ¿Qué genera el transpilador?

- Un archivo `.cpp` **autocontenido** con el runtime `PyValue` embebido.
- Funciones de usuario como `PyValue nombre(PyValue arg, ...)`.
- El código global dentro de `int main()`.
- Condiciones con `py_truthy()` para respetar la semántica de Python.

---

## 6. Demostraciones para defensa

En `demos/` hay 5 programas listos para presentar en vivo.

### Validación completa antes de la defensa

```bash
py demos/run_demos.py --full
py tests/transpile/run_transpile_error_tests.py
```

Esto ejecuta: prueba del runtime, suite de codegen, las 5 demos y pruebas de errores.

### Tabla de demos

| # | Archivo | Qué demuestra | Salida esperada |
|---|---------|---------------|-----------------|
| 1 | `demo_dynamic_typing.py` | Tipado dinámico con `PyValue` | `True` |
| 2 | `demo_functions.py` | `def`, parámetros, `return` y llamadas | `16` |
| 3 | `demo_control_flow.py` | `if`/`elif`/`else`, `while`, `for`, `break`/`continue` | `large` y luego `22` |
| 4 | `demo_lists.py` | Listas, `.append()`, índices, `len()` | `10 30 3` |
| 5 | `demo_fibonacci.py` | Fibonacci recursivo (estilo benchmark) | `55` |

### Ejecutar una demo individual

```bash
py demos/run_demos.py --demo demo_functions
```

### Demo en vivo (una sola línea)

```bash
py src/main.py --codegen --compile --run --output demos/build/demo.cpp demos/demo_functions.py
```

### Flujo sugerido para defensa (5–7 minutos)

1. Mostrar el pipeline: fuente → AST → C++ → ejecutable.
2. Demo 1: explicar `PyValue` y cambio de tipos en tiempo de ejecución.
3. Demo 2: mostrar funciones generadas en C++.
4. Demo 3: resaltar `py_truthy()` en condiciones.
5. Demo 4: operaciones con listas.
6. Demo 5: conectar con los benchmarks de Fibonacci.
7. Abrir `benchmarks/results/Informe_Benchmarks.pdf` o los gráficos PNG.

---

## 7. Benchmarks de rendimiento

Los benchmarks comparan **tres implementaciones** del mismo algoritmo:

| Implementación | Descripción |
|----------------|-------------|
| Python original | Código Fangless ejecutado con CPython |
| C++ generado | Mismo código transpilado y compilado con `g++ -O2` |
| C++ a mano | Referencia nativa en `benchmarks/handwritten_cpp/` |

### Algoritmos medidos

| Benchmark | Archivo | Tamaños de entrada | Qué mide |
|-----------|---------|-------------------|----------|
| Fibonacci recursivo | `fib_recursive.py` | n = 1..34 | Llamadas recursivas y crecimiento exponencial |
| Fibonacci iterativo | `fib_iterative.py` | n = 1..50 | Bucles aritméticos (repetido 100 000 veces) |
| Ordenamiento burbuja | `bubble_sort.py` | n = 100..1000 | Bucles anidados y acceso a listas |

> **Nota:** El PDF pide Fibonacci recursivo hasta n=50, pero valores mayores a 34 son inviables por costo exponencial. La versión iterativa sí cubre n=1..50.

### Cómo ejecutar

Prueba rápida:

```bash
py benchmarks/run_benchmarks.py --quick --samples 1
```

Ejecución completa (para el informe):

```bash
py benchmarks/run_benchmarks.py --samples 5
py benchmarks/plot_results.py
py benchmarks/generate_report.py
py benchmarks/generate_informe_pdf.py
```

### Archivos generados

| Archivo | Contenido |
|---------|-----------|
| `benchmarks/results/benchmark_results.csv` | Tiempos y checksums |
| `benchmarks/results/fib_recursive.png` | Gráfico Fibonacci recursivo |
| `benchmarks/results/fib_iterative.png` | Gráfico Fibonacci iterativo |
| `benchmarks/results/bubble_sort.png` | Gráfico ordenamiento burbuja |
| `benchmarks/results/PERFORMANCE_ANALYSIS.md` | Análisis detallado en inglés |
| `benchmarks/results/Informe_Benchmarks.pdf` | Informe en español con gráficos |

---

## 8. Pruebas automatizadas

### Suite recomendada (validación completa)

```bash
py tests/runtime/run_runtime_smoke_test.py
py tests/codegen/run_codegen_tests.py
py tests/transpile/run_transpile_error_tests.py
py demos/run_demos.py --full
```

### Qué valida cada suite

| Comando | Qué prueba |
|---------|------------|
| `run_runtime_smoke_test.py` | Runtime `PyValue` en C++ aislado |
| `run_codegen_tests.py` | 21 casos: parse → C++ → compilar → ejecutar |
| `run_transpile_error_tests.py` | 6 casos de error con línea y columna |
| `demos/run_demos.py --full` | Las 5 demos de defensa |

### Pruebas del parser

```bash
py "Test Files/test_parser_batch.py"
```

También puedes probar archivos individuales:

```bash
py src/main.py "Casos de prueba/Parser/try_except_basic.fpy"
py src/main.py "Casos de prueba/Parser/method_calls_required.fpy"
py src/main.py "Casos de prueba extra/indent_if_elif_else.py"
```

---

## 9. Características soportadas

### Análisis léxico (lexer)

- Identificadores, enteros, flotantes, cadenas, booleanos
- Palabras clave y operadores
- Comentarios con `#`
- Indentación (`INDENT` / `DENT`, equivalente a `DEDENT`)
- Secuencias de escape: `\n`, `\t`, `\\`, `\"`, `\'`

### Análisis sintáctico (parser)

- Asignaciones simples y compuestas
- Expresiones aritméticas, relacionales y lógicas
- `if` / `elif` / `else`, `while`, `for`
- `break`, `continue`, `pass`
- Funciones, clases, herencia simple
- Listas, tuplas, diccionarios, conjuntos (sintaxis)
- Indexación, slicing, llamadas a métodos
- `print()`, `input()`, conversiones `int()`, `float()`, `str()`, `bool()`
- `try` / `except` (sintaxis)

### Transpilación a C++ (Etapa 3)

| Característica | Estado |
|----------------|--------|
| Tipado dinámico (`PyValue`) | ✅ |
| Funciones con parámetros y `return` | ✅ |
| Parámetros por defecto | ✅ |
| Funciones anidadas | ✅ |
| `if` / `elif` / `else` con `py_truthy()` | ✅ |
| `while`, `for`, `break`, `continue` | ✅ |
| Operadores aritméticos, lógicos y de comparación | ✅ |
| Listas, indexación, `.append()` | ✅ |
| Tuplas y slicing (listas y cadenas) | ✅ |
| Métodos de cadena (`.lower()`, `.upper()`, `.strip()`) | ✅ |
| Clases básicas (`__init__`, métodos, atributos) | ✅ |
| `try` / `except` | ✅ |
| Diccionarios, conjuntos, `raise` | ❌ |
| `*args` / `**kwargs` | ❌ |

### Funciones integradas (builtins)

`print`, `len`, `int`, `float`, `str`, `bool`, `range`, `input`

---

## 10. Limitaciones conocidas

Menciona estas limitaciones de forma proactiva en la defensa:

- **Diccionarios y conjuntos** se parsean pero no se transpilan aún.
- **`raise`** y `try-finally` completo no están implementados.
- **`*args` / `**kwargs`** no están soportados.
- El **C++ generado** usa el runtime `PyValue`; por eso es más lento que el C++ escrito a mano.
- **Fibonacci recursivo** en benchmarks solo llega a n=34 por costo exponencial.
- No hay soporte para: lambdas, comprehensions, decoradores, `async`/`await`, imports, f-strings, `with`, generadores.

---

## 11. Solución de problemas

### `g++` no encontrado

Instala un compilador C++17 y verifica que esté en el PATH:

```bash
g++ --version
```

En Windows, MinGW-w64 o el compilador de Visual Studio Build Tools funcionan.

### `ModuleNotFoundError: No module named 'ply'`

```bash
py -m pip install -r requirements.txt
```

### Error de compilación del C++ generado

1. Verifica que usas `-std=c++17`.
2. Revisa si el programa usa una característica no transpilada (ver sección 10).
3. Ejecuta `py tests/codegen/run_codegen_tests.py` para aislar el problema.

### Error de transpilación con línea y columna

El mensaje indica qué construcción no está soportada. Ejemplo:

```text
Transpile error: unsupported construct at line 5, column 3
```

### Los benchmarks tardan mucho

Usa la prueba rápida:

```bash
py benchmarks/run_benchmarks.py --quick --samples 1
```

O ejecuta solo algunos algoritmos:

```bash
py benchmarks/run_benchmarks.py --algorithms fib_iterative,bubble_sort --samples 3
```

---

## 12. Referencia rápida de comandos

```bash
# Ver tokens y AST
py src/main.py archivo.py

# Transpilar, compilar y ejecutar
py src/main.py --codegen --compile --run --output out.cpp archivo.py

# Solo transpilar
py src/transpile.py archivo.py salida.cpp

# Validación completa del proyecto
py tests/runtime/run_runtime_smoke_test.py
py tests/codegen/run_codegen_tests.py
py tests/transpile/run_transpile_error_tests.py
py demos/run_demos.py --full

# Benchmarks e informe
py benchmarks/run_benchmarks.py --samples 5
py benchmarks/generate_informe_pdf.py
```

---

## 13. Documentos relacionados

| Archivo | Contenido |
|---------|-----------|
| `README.md` | Resumen técnico del proyecto (inglés) |
| `src/codegen/README.md` | Detalle del transpilador y matriz de características |
| `benchmarks/README.md` | Metodología de benchmarks |
| `demos/DEFENSE_CHECKLIST.md` | Checklist corto para defensa |
| `benchmarks/results/Informe_Benchmarks.pdf` | Informe visual en español |
| `Tarea Programada 3 compiladores.pdf` | Especificación oficial de la tarea |

---

*Última actualización: julio 2026 — Proyecto Compiladores (C13388, C18723, C17382)*
