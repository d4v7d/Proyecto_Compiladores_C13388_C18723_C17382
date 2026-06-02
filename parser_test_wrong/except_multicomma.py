x = "abc"
 
try:
    result = int(x)
except ValueError, TypeError:
    print("conversion error")