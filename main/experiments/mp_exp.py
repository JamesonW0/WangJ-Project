import multiprocessing as mp
import numpy as np

cores = mp.cpu_count() - 1


def get_reward(size):
    array_1 = np.random.randn(size).astype(np.float32)
    array_1.reshape((1, size))
    array_2 = np.random.randn(size).astype(np.float32)
    array_2.reshape((size, 1))
    return np.dot(array_1, array_2)


if __name__ == '__main__':
    pool = mp.Pool(processes=cores)
    jobs = [pool.apply_async(get_reward, (index,)) for index in range(200)]
    result = rewards = np.array([j.get() for j in jobs])