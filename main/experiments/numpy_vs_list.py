import time

import numpy as np

start_time = time.time()
l = np.random.randn(1000000).astype(np.float32)
l2 = np.random.randn(1000000).astype(np.float32)
l3 = l + l2
end_time = time.time()
print(end_time - start_time)
'''
start = time.time()
l = []
l2 = []
for i in range(100000):
    l.append(random.random())
    l2.append(random.random())

l3 = l + l2
end = time.time()

print(end-start)
'''
