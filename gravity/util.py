# -*- coding: utf-8 -*-

import numpy as np
from pyrr import Vector3


def rand_spherical(r):
    """Creating a random vector using a sphere of given radius (radius) return:vector3"""
    r1, r2, r3 = np.random.random(3)
    r1 *= 2 * np.pi
    r2_sqrt = 2 * np.sqrt(r2 * (1 - r2))
    r3 *= r
    x = r3 * np.cos(r1) * r2_sqrt
    y = r3 * np.sin(r1) * r2_sqrt
    z = r3 * (1 - 2 * r2)
    return Vector3([x, y, z])

def from_spherical(r, t, p):
    """Creating cartesian coord. vector (r:[float] radius ; t:[float] theta(radians) ; p:[float] phi (radians))  return: vector3"""
    if not r: return Vector3()
    sin_p = np.sin(p)
    x = r * np.cos(t) * sin_p
    y = r * np.sin(t) * sin_p
    z = r * np.cos(p)
    return Vector3([x, y, z])

def to_spherical(v):
    """Compute sph. coord. returns: r,t,p"""
    if not v.any(): return 0, 0, 0
    r = v.length
    t = np.arctan2(v.y, v.x)
    p = np.arccos(v.z / r)
    return r, t, p

def lerp(x, old_min, old_max, new_min, new_max):
    """ Linear interpolation betn. givrn range."""
    return (x - old_min) / (old_max - old_min) * (new_max - new_min) + new_min
