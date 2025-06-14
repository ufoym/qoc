#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QOC Example File - Python
Used to demonstrate QOC (Quanta of Code) analysis functionality
"""

def fibonacci(n):
    """Calculate Fibonacci sequence"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    """Simple calculator class"""
    
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        """Addition operation"""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def multiply(self, a, b):
        """Multiplication operation"""
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result

    def get_history(self):
        """Get calculation history"""
        return self.history

# Usage example
calc = Calculator()

# Some calculations
results = []
results.append(calc.add(10, 5))
results.append(calc.multiply(3, 4))

print("Calculation results:", results)
print("History:", calc.get_history())

# Calculate Fibonacci numbers
for i in range(8):
    print(f"fibonacci({i}) = {fibonacci(i)}")

# Conditional logic example
def grade_system(score):
    """Grade system example"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"  
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

# Loop example
grades = []
for score in [95, 87, 76, 63, 52]:
    grade = grade_system(score)
    grades.append((score, grade))
    print(f"Score: {score}, Grade: {grade}")

# Complex data structures
data = {
    'students': [
        {'name': 'Alice', 'scores': [95, 87, 92]},
        {'name': 'Bob', 'scores': [78, 85, 80]},
        {'name': 'Charlie', 'scores': [88, 92, 85]}
    ],
    'subjects': ['Math', 'Science', 'English']
}

# Process data
for student in data['students']:
    avg_score = sum(student['scores']) / len(student['scores'])
    print(f"{student['name']}: Average score = {avg_score:.1f}")
    
# Exception handling example
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error occurred: {e}")
finally:
    print("Cleanup completed") 