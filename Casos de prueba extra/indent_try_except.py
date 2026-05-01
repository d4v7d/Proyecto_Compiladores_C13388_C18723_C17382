# Try/Except con múltiples niveles
try:
    a = 10
    try:
        b = a / 0
    except ZeroDivisionError:
        b = 0
    finally:
        c = 1
except Exception:
    d = 2
