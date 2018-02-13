import numpy as np
from math import exp, log

def gaussian_kernel(size, sigma=0.6):
    seq = np.array([[i, j] for i in range(size) for j in range(size)], dtype='int32')
    points = np.array(seq, dtype='float32') + 0.5
    center = np.array([0.5 * size, 0.5 * size])
    d = np.linalg.norm(points-center, axis=1)
    kern1d = 1.0/(sigma * (2*np.pi)**0.5) * np.exp(-1.0 * np.power(d, 2) / (2.0 * sigma**2))
    kern = kern1d.reshape([size, size]) / np.sum(kern1d)
    return kern

def pairwise_distance(X, Y):
    assert len(X.shape) == len(Y.shape)
    N = X.shape[0]
    M = Y.shape[0]
    D = len(X.shape)
    Xe = np.repeat(np.expand_dims(X, axis=0), M, axis=0)
    Ye = np.repeat(np.expand_dims(Y, axis=1), N, axis=1)
    return np.linalg.norm(Xe-Ye, axis=D)

def gaussian_radial_basis(X, beta=2.0):
    PD = pairwise_distance(X, X)
    return np.exp(-0.5 * np.power(PD/beta, 2))

def init_sigma2(X, Y):
    N = float(X.shape[0])
    M = float(Y.shape[0])
    t1 = M * np.trace(np.dot(np.transpose(X), X))
    t2 = N * np.trace(np.dot(np.transpose(Y), Y))
    t3 = 2.0 * np.dot(np.sum(X, axis=1), np.transpose(np.sum(Y, axis=1)))
    return (t1 + t2 -t3)/(M*N*2.0)

def match(PD):
    seq = np.arange(PD.shape[1])
    amin1 = np.argmin(PD, axis=0)
    C = np.array([seq, amin1]).transpose()
    min1 = PD[amin1, seq]
    mask = np.zeros_like(PD)
    mask[amin1, seq] = 1
    masked = np.ma.masked_array(PD, mask)
    min2 = np.amin(masked, axis=0)
    return (C, min2/min1)

def compute(X, Y, T_old, Pm, sigma2, omega):
    N = X.shape[0]
    M = Y.shape[0]
    T = T_old

    Pmxn = np.zeros([M, N])
    for m in range(M):
        for n in range(N):
            xn = X[n, :]
            tm = T[m, :]
            Pmxn[m, n] = (1-omega) * Pm[m, n] * \
                         exp( -(1/(2*sigma2)) * np.power(xn-tm, 2).sum() )

    Pxn = np.sum(Pmxn, axis=0) + omega/N
    Po = Pmxn / np.repeat(Pxn, axis=0)

    Np = np.dot(np.dot(np.ones([1, M]), Po), np.ones([N, 1]))
    P1 = np.dot(Po, np.ones([N, 1]))
    Px = np.diag(Po.transpose().dot(np.ones([M, 1])))
    Py = np.diag(P1)
    tmp = np.trace(np.dot(np.dot(X.transpose(), Px), X)) - \
        2.0 * np.trace(np.dot(np.dot(T.transpose(), Po), X)) + \
        np.trace(np.dot(np.dot(T.transpose(), Py, T)))
    Q = Np * log(sigma2) + tmp/(2.0*sigma2)
    return (Po, P1, Np, tmp, Q)