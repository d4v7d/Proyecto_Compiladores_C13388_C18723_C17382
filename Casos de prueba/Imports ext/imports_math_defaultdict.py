import math
from collections import defaultdict

assert math.sqrt(9) == 3.0
d = defaultdict(int)
d["x"] += 1
assert d["x"] == 1
assert d["y"] == 0
