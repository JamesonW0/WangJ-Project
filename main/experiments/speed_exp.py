import time
import numpy as np
import numba

D = np.random.random([30,12])
E = np.random.random([12,26])

total = 0


@numba.jit
def matmulti(A,B):
    return np.dot(A,B)


for i in range(1000):
    start = time.time()
    matmulti(D,E)
    end = time.time()
    total += end - start

print(total/100)
