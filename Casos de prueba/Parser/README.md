# Parser test cases

Valid parser smoke test:

```bash
python src/main.py "Casos de prueba/Parser/parser_part1.fpy"
```

Invalid syntax cases:

```bash
python src/main.py "Casos de prueba/Parser/invalid/missing_expression.fpy"
python src/main.py "Casos de prueba/Parser/invalid/missing_rparen.fpy"
python src/main.py "Casos de prueba/Parser/invalid/invalid_operator_position.fpy"
python src/main.py "Casos de prueba/Parser/invalid/missing_assignment_target.fpy"
python src/main.py "Casos de prueba/Parser/invalid/double_operator.fpy"
```
