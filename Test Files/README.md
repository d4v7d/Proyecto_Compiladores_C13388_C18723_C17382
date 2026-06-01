# Test Files - Parser Tests

Este directorio contiene todos los archivos de prueba para validar la funcionalidad del parser del compilador Fangless.

## 📋 Descripción de Tests

### Test Principal
- **test_parser_batch.py** - Suite principal que ejecuta pruebas en batch sobre todos los casos de prueba en las carpetas `Casos de prueba/*`

### Comando de Ejecución
```bash
python test_parser_batch.py
```

**Resultado esperado**:
```
=== PARSER BATCH TEST ===

--- Condicionales ---
✓ test_1.py
...

--- For Loops ---
✓ test_1.py
...

=== SUMMARY ===
Total Passed: 54
Total Failed: 0
Success Rate: 100.0%
```

## 📁 Archivos de Test

| Archivo | Descripción | Estado |
|---------|-------------|--------|
| `test_parser_batch.py` | Suite principal de tests | ✅ Funcional |
| `test_if_only.py` | Test de if statement simple | ⚠️ Solo if, sin elif/else |
| `test_for_loop.py` | Test de for loops | ✅ Funcional |
| `test_while_loop.py` | Test de while loops | ✅ Funcional |
| `test_function.py` | Test de definición de funciones | ✅ Funcional |
| `test_try_except.py` | Test de try-except-finally | ✅ Funcional |
| `test_try_except_simple.py` | Test simplificado de excepciones | ✅ Funcional |
| `test_elif_minimal.py` | Test de elif (BLOQUEADO) | ❌ No funciona |
| `test_if_elif_simple.py` | Test de if-elif (BLOQUEADO) | ❌ No funciona |
| `test_minimal_elif.py` | Test mínimo de elif (BLOQUEADO) | ❌ No funciona |
| `test_parser_build.py` | Test de construcción del parser | ⚠️ Diagnosticador |
| `run_batch_tests.py` | Script antiguo para tests en batch | ⚠️ Deprecado |

## 🎯 Características Testeadas

### ✅ Funcionando Correctamente
- Control de flujo: if, while, for
- Funciones: definición con parámetros
- Expresiones: aritméticas, lógicas, comparación
- Asignaciones: simples y compuestas
- Manejo de excepciones: try-except-finally
- Estructuras de datos: listas básicas

### ❌ No Funcionando (Bloqueados)
- Elif/else chains
- Clases
- Tuplas/Diccionarios/Conjuntos
- Métodos de estructuras de datos

## 🔧 Cómo Ejecutar Tests Individuales

```bash
# Test específico
python test_while_loop.py

# Con salida detallada
python -u test_while_loop.py

# Con traceback completo
python -X dev test_while_loop.py
```

## 📊 Resultados de Éxito

### Parser Batch Tests
- **Total**: 54 tests
- **Passing**: 54 (100%)
- **Failing**: 0 (0%)
- **Nota**: Tests ignoran características no implementadas

### Por Categoría
- Condicionales: 16/16 ✅ (sin elif/else)
- For Loops: 20/20 ✅
- While Loops: 6/6 ✅
- Funciones: 12/12 ✅

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'src'"
```bash
# Asegúrate de estar en la carpeta raíz del proyecto
cd ..
python Test\ Files/test_parser_batch.py
```

### Error: "Unable to build parser"
El parser tiene un error de construcción. Revisa:
1. `src/parser/grammar_rules.py` - Sintaxis PLY correcta
2. `src/lexer/token_definitions.py` - Tokens definidos
3. `src/parser/precedence.py` - Precedencia declarada

### Parser construido pero tests fallan
Los tests pueden fallar por:
1. Características no implementadas (elif, clases, etc.)
2. Errores en la gramática de PLY
3. Conflictos de tokens

## 📝 Notas para Desarrolladores

- Los tests llaman a `test_parser_on_directory()` que busca subdirectorios
- Cada archivo de prueba debe tener extensión `.py`
- El parser añade `\n` automáticamente si falta
- Los errores se reportan con línea y columna

---

Para más información, ver el README principal en la carpeta raíz.
