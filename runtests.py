import subprocess
print("Example 1: pizza (paper example)") # T1 
result = subprocess.run('python3 -m refpy.main ref_tests/pizza.py', shell=True, capture_output=True, text=True, executable="/bin/bash")
print(result.stdout)
print("Example 2: points") 
result = subprocess.run(f'python3 -m refpy.main ref_tests/a_little_Java/lession1_basics_points.py', shell=True, capture_output=True, text=True, executable="/bin/bash")
print(result.stdout)
print("Example 3: kebab")
result = subprocess.run('python3 -m refpy.main ref_tests/a_little_Java/lession2_methods_kebabAndshish.py', shell=True, capture_output=True, text=True, executable="/bin/bash")
print(result.stdout)
print("Example 4: pizza (simple)") 
result = subprocess.run('python3 -m refpy.main ref_tests/a_little_Java/lession3_new_pizza.py', shell=True, capture_output=True, text=True, executable="/bin/bash")
print(result.stdout)
print("Example 5: pizza (simple visitor)") 
result = subprocess.run('python3 -m refpy.main ref_tests/a_little_Java/lession4_visitor_pizza.py', shell=True, capture_output=True, text=True, executable="/bin/bash")
print(result.stdout)
print("Example 6: pizza visitor") # T2 
result = subprocess.run('python3 -m refpy.main ref_tests/a_little_Java/lession5_objects_pizza.py', shell=True, capture_output=True, text=True, executable="/bin/bash")
print(result.stdout)
print("Example 7: pizza (abstract)")
result = subprocess.run('python3 -m refpy.main ref_tests/a_little_Java/lession6_abstractVisitor_pizza.py', shell=True, capture_output=True, text=True, executable="/bin/bash")
print(result.stdout)
print("Example 8: tree") # T3 
result = subprocess.run('python3 -m refpy.main ref_tests/a_little_Java/lession7_overloadingAndgenericVisitor_tree.py', shell=True, capture_output=True, text=True, executable="/bin/bash")
print(result.stdout)
print("Example 9: pizza (override)")
result = subprocess.run('python3 -m refpy.main ref_tests/a_little_Java/lession8_override_pizza.py', shell=True, capture_output=True, text=True, executable="/bin/bash")
print(result.stdout)
print("Example 10: geometry") # T4
result = subprocess.run('python3 -m refpy.main ref_tests/a_little_Java/lession9_dataExtensionAndfactory_geometry.py', shell=True, capture_output=True, text=True, executable="/bin/bash")
print(result.stdout)
print("Example 11: list") # T5 
result = subprocess.run('python3 -m refpy.main ref_tests/list.py', shell=True, capture_output=True, text=True, executable="/bin/bash")
print(result.stdout)
print("Example 12: lambda") # T6 
result = subprocess.run('python3 -m refpy.main ref_tests/lambda.py', shell=True, capture_output=True, text=True, executable="/bin/bash")
print(result.stdout)
print("Example 13: stlc") # T7
result = subprocess.run('python3 -m refpy.main ref_tests/stlc.py', shell=True, capture_output=True, text=True, executable="/bin/bash")
print(result.stdout)
print("Example 14: stlc using permutate")
result = subprocess.run('python3 -m refpy.main ref_tests/stlc2.py', shell=True, capture_output=True, text=True, executable="/bin/bash")
print(result.stdout)
