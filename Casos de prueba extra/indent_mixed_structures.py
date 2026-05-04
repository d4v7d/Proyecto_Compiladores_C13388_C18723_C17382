# Mezcla de estructuras complejas
class Calculator:
    def calculate(self, data):
        result = []
        for item in data:
            if item > 0:
                try:
                    value = 100 / item
                except ZeroDivisionError:
                    value = 0
                finally:
                    result.append(value)
        return result
    
    def filter_results(self, results):
        return [x for x in results if x > 0]
