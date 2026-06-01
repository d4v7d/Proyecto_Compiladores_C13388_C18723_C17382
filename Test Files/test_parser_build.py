#!/usr/bin/env python
"""Test parser building to check for warnings/errors."""

import sys
sys.path.insert(0, 'src')

from parser.parser_builder import FanglessParser

parser = FanglessParser(debug=True)
print("Parser built successfully")
