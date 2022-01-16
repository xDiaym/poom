#cython: language_level=3


cdef float frac(float x)
cdef int sign(float x)
cdef float angle_diff(float alpha, float beta)

cdef struct Vec2i:
    int x
    int y

cdef struct Vec2f:
    float x
    float y

cdef Vec2f sub(Vec2f u, Vec2f v)
cdef float magnitude(Vec2f v)
