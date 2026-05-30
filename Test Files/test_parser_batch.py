#!/usr/bin/env python3
"""Quick parser batch test to validate implementation."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from parser.parser_builder import FanglessParser

def test_parser_on_directory(test_dir):
    """Test parser on all .py files in a directory."""
    parser = FanglessParser()
    passed = 0
    failed = 0
    errors = []
    
    test_path = Path(test_dir)
    if not test_path.exists():
        print(f"Test directory not found: {test_dir}")
        return passed, failed, errors
    
    py_files = sorted(test_path.glob("*.py"))
    
    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # Ensure file ends with newline (required for proper lexing)
            if source and not source.endswith('\n'):
                source += '\n'
            
            ast = parser.parse(source)
            
            if parser.errors:
                failed += 1
                errors.append((py_file.name, parser.errors[0]))
            else:
                passed += 1
                print(f"✓ {py_file.name}")
        except Exception as e:
            failed += 1
            errors.append((py_file.name, str(e)))
    
    return passed, failed, errors

def main():
    print("=== PARSER BATCH TEST ===\n")
    
    test_categories = [
        ("Condicionales", "Casos de prueba/Condicionales"),
        ("For Loops", "Casos de prueba/For"),
        ("While Loops", "Casos de prueba/While"),
        ("Functions", "Casos de prueba/Argumentos de funcion"),
    ]
    
    total_passed = 0
    total_failed = 0
    all_errors = []
    
    for category_name, category_path in test_categories:
        print(f"\n--- {category_name} ---")
        passed, failed, errors = test_parser_on_directory(category_path)
        total_passed += passed
        total_failed += failed
        all_errors.extend([(category_name, f, e) for f, e in errors])
        
        print(f"  Passed: {passed}, Failed: {failed}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total Passed: {total_passed}")
    print(f"Total Failed: {total_failed}")
    print(f"Success Rate: {100*total_passed/(total_passed+total_failed):.1f}%")
    
    if all_errors:
        print(f"\n=== FAILURES ===")
        for category, filename, error in all_errors[:10]:
            print(f"\n[{category}] {filename}:")
            print(f"  {str(error)[:100]}...")

if __name__ == "__main__":
    main()

