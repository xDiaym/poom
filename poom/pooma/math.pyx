#cython: language_level=3
from libc.math cimport M_PI, fmod, sqrt


cdef float frac(float x):
    return x - <int> x

cdef int sign(float x):
    return 1 if x >= 0 else -1

cdef Vec2f sub(Vec2f u, Vec2f v):
    return Vec2f(u.x - v.x, u.y - v.y)

cdef float angle_diff(float alpha, float beta):
    cdef float diff = fmod(alpha - beta, 2 * M_PI)
    if diff > M_PI:
        diff -= 2 * M_PI
    elif diff < -M_PI:
        diff += 2 * M_PI
    return diff

cdef float magnitude(Vec2f v):
    return sqrt(v.x ** 2 + v.y ** 2)

