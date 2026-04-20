# Proyecto_Compiladores_C13388_C18723_C17382
# Analizador Léxico

Implementación de un analizador léxico (*lexer*) construido con PLY. El lexer transforma código en una secuencia de tokens clasificados, incluyendo manejo de indentación sensible al contexto usando los tokens `INDENT` y `DENT`.

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