import math
import numpy as np

a = np.array([7, 5])
b = np.array([1,0])

c = a.dot(b)
print(c)
d = math.sqrt(a[0]**2 + a[1]**2)
e = math.sqrt(b[0]**2 + b[1]**2)

r = math.acos(c/(d*e))
r = math.degrees(r)
print(r)