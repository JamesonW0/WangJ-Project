import numpy as np

rank = np.arange(1, 21)
util_l = np.maximum(0, np.log(11) - np.log(rank))
utility = util_l / (util_l.sum() - 1) / 20
print(utility)