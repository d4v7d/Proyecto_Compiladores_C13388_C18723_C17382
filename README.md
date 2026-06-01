# Compilador Fangless Python a C++

Compilador que traduce una versión simplificada de Python a C++, desarrollado con PLY (Python Lex-Yacc). Implementa un lexer completo (100%) y un parser parcial con características principales funcionando.

---

## 📊 Estado del Proyecto

| Componente | Estado | Progreso |
|-----------|--------|----------|
| **Lexer** | ✅ Completo | 168/168 tests (100%) |
| **Parser** | ⚠️ Parcial | 54/54 tests sin considerar elif/else/clases |
| **Documentación** | ⚠️ En progreso | Este README |

---

## 📁 Estructura del Proyecto

```
Proyecto/
├── README.md                          # Este archivo
├── requirements.txt                   # Dependencias
├── src/
│   ├── main.py                        # Punto de entrada
│   ├── lexer/
│   │   ├── __init__.py
│   │   ├── token_definitions.py       # Tokens y palabras clave
│   │   ├── lexer_rules.py             # Reglas del lexer
│   │   └── lexer_builder.py           # Clase FanglessLexer
│   └── parser/
│       ├── __init__.py
│       ├── grammar_rules.py           # Reglas gramaticales (PLY)
│       ├── ast_nodes.py               # Nodos del AST
│       ├── parser_builder.py          # Clase FanglessParser
│       ├── parser_errors.py           # Manejo de errores
│       └── precedence.py              # Precedencia de operadores
├── Casos de prueba/                   # Pruebas del lexer por categoría
├── Casos de prueba extra/             # Pruebas adicionales
├── Casos de prueba incorrectos/       # Casos con errores esperados
└── Test Files/                        # Tests del parser
    ├── test_parser_batch.py           # Suite principal
    └── test_*.py                      # Tests individuales

---

## ✅ Características Completadas

### Lexer (100%)
- ✅ Identificadores, números (int/float), strings, booleanos
- ✅ Palabras clave: if, else, elif, while, for, def, return, break, continue, pass, try, except, finally, raise, class, and, or, not, True, False
- ✅ Operadores: aritméticos, comparación, asignación, lógicos
- ✅ Delimitadores: paréntesis, corchetes, llaves, dos puntos, coma, punto
- ✅ Indentación: tokens INDENT/DENT para bloques
- ✅ Comentarios: línea única (#)
- ✅ Escape sequences: \n, \t, \\, \", \'

### Parser - Control de Flujo
- ✅ **If statements** (sin elif/else)
- ✅ **While loops**
- ✅ **For loops** con iteración
- ✅ **Break, Continue, Pass**

### Parser - Funciones
- ✅ Definición de funciones: `def nombre(param1, param2=default):`
- ✅ Parámetros posicionales y con valores por defecto
- ✅ Llamadas de función con argumentos

### Parser - Expresiones
- ✅ Operadores aritméticos: +, -, *, /, //, %, **
- ✅ Operadores de comparación: ==, !=, <, >, <=, >=
- ✅ Operadores lógicos: and, or, not
- ✅ Operadores unarios: -, +
- ✅ Precedencia correcta
- ✅ Expresiones agrupadas con paréntesis

### Parser - Asignaciones
- ✅ Asignación simple: `x = valor`
- ✅ Asignación compuesta: `+=`, `-=`, `*=`, `/=`, `//=`, `%=`, `**=`

### Parser - Estructuras de Datos
- ✅ **Listas**: Creación `[1, 2, 3]`, acceso `lista[0]`
- ⚠️ **Tuplas, Diccionarios, Conjuntos**: Sin soporte

### Parser - Manejo de Excepciones
- ✅ `try-except` genérico
- ✅ `try-except` tipado: `except ValueError`
- ✅ `except ... as var`: `except ValueError as e`
- ✅ `try-finally`
- ✅ `try-except-finally`
- ✅ `raise` statements

### Parser - I/O y Tipos
- ✅ `print()` e `input()`
- ✅ Enteros, Flotantes, Strings, Booleanos
- ✅ Acceso a atributos: `objeto.atributo`
- ✅ `return` con/sin valor

---

## ❌ Características Pendientes

### 🔴 CRÍTICAS (Enunciado las requiere)

#### 1. **Elif/Else Chains** (~10-15% del proyecto)
```python
# ❌ No soportado:
if x > 0:
    print("positivo")
elif x < 0:
    print("negativo")
else:
    print("cero")
```
**Bloqueador técnico**: Conflicto entre tokens DENT y análisis LR(1) de PLY.  
**Solución propuesta**: Fusión de tokens a nivel léxico.

#### 2. **Clases y OOP** (~25-30% del proyecto)
```python
# ❌ No soportado:
class MiClase:
    def __init__(self, valor):
        self.valor = valor
    def metodo(self):
        return self.valor
```
**Lo que falta**: class, herencia, métodos, atributos, self implícito.

#### 3. **Estructuras Avanzadas** (~15-20%)
- ❌ **Tuplas**: `(1, 2, 3)` y desempaquetado
- ❌ **Diccionarios**: `{key: value}` y acceso
- ❌ **Conjuntos**: `{1, 2, 3}` y operaciones

### 🟡 IMPORTANTES

#### 4. **Métodos de Estructuras de Datos**
- ❌ Strings: `lower()`, `upper()`, `find()`, `replace()`, `split()`, `join()`
- ❌ Listas: `append()`, `remove()`, `index()`, `sort()`, `reverse()`
- ❌ Diccionarios: `get()`, `keys()`, `values()`, `items()`
- ❌ Conjuntos: `add()`, `remove()`, `union()`, `intersection()`

#### 5. **Slicing** (~5-10%)
- ❌ `texto[1:3]`, `lista[0:2]`, `texto[::2]`

#### 6. **Desempaquetado**
- ❌ `a, b = 1, 2`
- ❌ `x, y = func()`

---

## 🚀 Instalación y Uso

### Requisitos
```
Python 3.8+
PLY 3.11
```

### Instalar
```bash
pip install -r requirements.txt
```

### Ejecutar Lexer
```bash
python src/main.py archivo.py
```

### Ejecutar Parser Tests
```bash
python Test\ Files/test_parser_batch.py
```

**Resultado**:
```
=== PARSER BATCH TEST ===
--- Condicionales ---
✓ test_1.py
...
Success Rate: 100.0%
```

---

## 📊 Resultados de Tests

### Lexer: ✅ 100% (168/168)
Todos los casos de prueba pasan.

### Parser: ⚠️ 100% (54/54 tests reportados)
**Nota**: Los tests pasan porque ignoran características no implementadas.
- Condicionales: 16/16 ✅ (sin elif/else)
- For: 20/20 ✅
- While: 6/6 ✅
- Funciones: 12/12 ✅

---

## Estructura del proyecto

```
Proyecto/
│
├── src/
│   ├── main.py                  # Punto de entrada. Lee archivo y muestra tokens
│   └── lexer/
│       ├── __init__.py
│       ├── token_definitions.py # Lista de tokens y patrones simples
│       ├── lexer_rules.py       # Reglas complejas con lógica
│       └── lexer_builder.py     # Clase FanglessLexer — ensambla y ejecuta el lexer
│
├── Casos de prueba/                       # Casos de prueba con entrada válida
└── casos de prueba incorrectos/           # Casos de prueba con errores léxicos esperados

```

---

## Requisitos

- Python 3.8 o superior
- PLY 3.11

---

## Instalación

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd proyecto

# Instalar dependencias
pip install ply
```

---

## Uso

```bash
python src/main.py <archivo>
```

### Ejemplo

Dado el archivo `ejemplo.py`:

```python
def suma(a, b):
    return a + b
```

Se ejecuta:

```bash
python src/main.py ejemplo.fpy
```

Salida del ejemplo:

```
Type: DEF                  Value: def        Line: 1
Type: IDENTIFIER           Value: suma       Line: 1
Type: LPAREN               Value: (          Line: 1
Type: IDENTIFIER           Value: a          Line: 1
Type: COMMA                Value: ,          Line: 1
Type: IDENTIFIER           Value: b          Line: 1
Type: RPAREN               Value: )          Line: 1
Type: COLON                Value: :          Line: 1
Type: INDENT               Value:            Line: 2
Type: RETURN               Value: return     Line: 2
Type: IDENTIFIER           Value: a          Line: 2
Type: PLUS                 Value: +          Line: 2
Type: IDENTIFIER           Value: b          Line: 2
Type: DENT                 Value:            Line: 3
```

---

## Tokens reconocidos

### Literales

| Token        |          Descripción                          | Ejemplo           |
|--------------|-----------------------------------------------|-------------------|
| `INTEGER`    | Secuencia de dígitos decimales                | `42`, `0`, `1000` |
| `FLOAT`      | Dígitos, punto decimal, más dígitos           | `3.14`, `0.5`     |
| `STRING`     | Cadena entre `"..."` o `'...'` con escapes    | `"hola"`, `'\n'`  |
| `IDENTIFIER` | Letra o `_`, seguido de alfanuméricos o `_`   | `x`, `mi_var`     |

### Palabras reservadas

| Token      | Lex        | Token      | Lex        |
|------------|------------|------------|------------|
| `IF`       | `if`       | `FOR`      | `for`      |
| `ELSE`     | `else`     | `BREAK`    | `break`    |
| `ELIF`     | `elif`     | `CONTINUE` | `continue` |
| `WHILE`    | `while`    | `PASS`     | `pass`     |
| `DEF`      | `def`      | `RETURN`   | `return`   |
| `CLASS`    | `class`    | `TRUE`     | `True`     |
| `AND`      | `and`      | `FALSE`    | `False`    |
| `OR`       | `or`       | `NOT`      | `not`      |

### Operadores aritméticos

| Token          | Lex    |
|----------------|--------|
| `PLUS`         | `+`    |
| `MINUS`        | `-`    |
| `TIMES`        | `*`    |
| `DIVIDE`       | `/`    |
| `FLOOR_DIVIDE` | `//`   |
| `MODULO`       | `%`    |
| `POWER`        | `**`   |

### Operadores de comparación

| Token | Lex    | Token | Lex    |
|-------|--------|-------|--------|
| `EQ`  | `==`   | `LT`  | `<`    |
| `NE`  | `!=`   | `GT`  | `>`    |
| `LE`  | `<=`   | `GE`  | `>=`   |

### Operadores de asignación

| Token                | Lex    |
|----------------------|--------|
| `ASSIGN`             | `=`    |
| `PLUS_ASSIGN`        | `+=`   |
| `MINUS_ASSIGN`       | `-=`   |
| `TIMES_ASSIGN`       | `*=`   |
| `DIVIDE_ASSIGN`      | `/=`   |
| `MOD_ASSIGN`         | `%=`   |
| `FLOOR_DIVIDE_ASSIGN`| `//=`  |
| `POWER_ASSIGN`       | `**=`  |

### Delimitadores

| Token      | Lex    | Token      | Lex    |
|------------|--------|------------|--------|
| `LPAREN`   | `(`    | `RBRACKET` | `]`    |
| `RPAREN`   | `)`    | `LBRACE`   | `{`    |
| `LBRACKET` | `[`    | `RBRACE`   | `}`    |
| `COLON`    | `:`    | `DOT`      | `.`    |
| `COMMA`    | `,`    | `PIPE`     | `\|`   |

### Tokens de indentación

| Token    | Descripción                                               |
|----------|-----------------------------------------------------------|
| `INDENT` | Cuando el nivel de indentación aumenta            |
| `DENT`   | Cuando el nivel de indentación disminuye          |

---

## Manejo de indentación

El lexer usa un mecanismo de pila para rastrear los niveles de indentación. La regla `t_newline` captura el patrón `\n[ \t]*` lo que incluye los espacios o tabs que siguen al salto de línea.

---

## Manejo de errores

Los errores léxicos son **no fatales**: el lexer registra el error y continúa el análisis (*modo de pánico*). Esto permite detectar múltiples errores en una sola pasada.

Los errores se acumulan en `lexer.errors` y actualmente se imprimen al final si los hay.

```
Lexical error: illegal character '@' at line 5
Lexical error: illegal character '$' at line 12
```

---

## Casos de prueba

Ver las carpetas `Casos de prueba` y `Casos de prueba incorrectos` para ejemplos de entradas válidas e inválidas.