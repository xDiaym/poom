#cython: language_level=3
from libc.math cimport sqrt


cdef float frac(float x):
    return x - <int> x

cdef int sign(float x):
    return 1 if x >= 0 else -1

cdef Vec2f sub(Vec2f u, Vec2f v):
    return Vec2f(u.x - v.x, u.y - v.y)

cdef float magnitude(Vec2f v):
    return sqrt(v.x ** 2 + v.y ** 2)
