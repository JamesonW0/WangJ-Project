def make(P, Q):
    a = Q[1] - P[1]
    b = P[0] - Q[0]
    c = a * (P[0]) + b * (P[1])
    return a, b, c


# Driver code
if __name__ == '__main__':
    P = [124564, 241]
    Q = [23565, 55554]
    make(P, Q)