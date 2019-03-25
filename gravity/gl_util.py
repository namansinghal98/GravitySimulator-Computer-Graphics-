import ctypes
import numpy as np
from OpenGL.GL import *


def print_gl_version():
    version_str = str(glGetString(GL_VERSION), 'utf-8')
    shader_version_str = str(glGetString(GL_SHADING_LANGUAGE_VERSION), 'utf-8')
    print('Loaded OpenGL {} with GLSL {}'.format(version_str, shader_version_str))

class BufferObject(object):
    """ Helper class ---->(for)  OpenGL buffer object.  """

    def __init__(self, target):
        """  Creating a buffer. (target: [enum] - OpenGL buffer target) """
        self.target = target
        self._buf_id = glGenBuffers(1)

    def __enter__(self):
        """ Buffer binding manager """
        glBindBuffer(self.target, self._buf_id)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Buffer unbinding manager"""
        glBindBuffer(self.target, 0)

        return False

class ConstBufferObject(BufferObject):
    """  Helper class --->(for) a constant data buffer  """
    def __init__(self, usage, target, data):
        """ Generates a new buffer.  ( usage: [enum], buffer usage  ;target: [enum], buffer target ;data: [np.ndarray], data for initializing buffer """
        super().__init__(target)
        self.usage = usage
        self.data = data
        self.dtype = data.dtype
        self.length = len(data)

        with self:                                              # bind the buffer and buffer the given data
            glBufferData(self.target, self.data.nbytes, self.data, self.usage)

class MappedBufferObject(BufferObject):
    """  Helper class --->(for) memory-mapped storage buffer   """

    def __init__(self, target, dtype, length, flags):
        """ Generates a new buffer.  ( target: [enum], buffer target ; dtype: [np.dtype], datatype of mapped array
        ;length: [int] (+ve), no. of elements to allocate  ;flags: [int], flags to pass to glBufferStorage and glMapBufferRange"""
        super().__init__(target)
        self.dtype = dtype
        self.length = length
        self.flags = flags

        with self:
            """binding the buffer"""
            data_size = self.dtype.itemsize * self.length
            glBufferStorage(self.target, data_size, None, self.flags)
            """Initializing empty buffer storage"""
            ptr = glMapBufferRange(self.target, 0, data_size, self.flags)
            """ Pointer to mapped memory for buffer"""

            arr_type = ctypes.c_float * (data_size // ctypes.sizeof(ctypes.c_float))
            """Creating array from pointer"""
            self.data = np.ctypeslib.as_array(arr_type.from_address(ptr))
            self.data = self.data.view(dtype=self.dtype, type=np.ndarray)

_gl_sync_obj = None

def gl_lock():
    """  Craeting a lock  (can be waited upon for GPU commands to finish)"""
    global _gl_sync_obj
    if _gl_sync_obj:
        glDeleteSync(_gl_sync_obj)

    _gl_sync_obj = glFenceSync(GL_SYNC_GPU_COMMANDS_COMPLETE, 0)

def gl_wait():
    """ For waiting on the lock"""
    global _gl_sync_obj
    if _gl_sync_obj:
        while True:
            wait_ret = glClientWaitSync(_gl_sync_obj, GL_SYNC_FLUSH_COMMANDS_BIT, 1)
            if wait_ret in (GL_ALREADY_SIGNALED, GL_CONDITION_SATISFIED):
                return

def gl_sync():
    """Syncs by waiting for commands to complete  """
    gl_lock()
    gl_wait()

def setup_vbo_attrs(vbo, shader, attr_prefix=None, divisor=0):
    """Creating shader attrib. for VBO  (vbo: [BufferObject]  ;shader:  shader reference,  ;
    attr_prefix: [str], the name prefix for attr. in shader source ;divisor: [int], the instancing divisor (should be 1 if these attributes should be used per-instance) ) """
    glBindBuffer(GL_ARRAY_BUFFER, vbo._buf_id)
    """Binding buffer as an array"""

    for prop, (sub_dtype, offset) in vbo.dtype.fields.items():
        """prop: name of the field ; sub_dtype:type of field ; offset:offset in each elem."""

        if attr_prefix is not None:
            """getting location of the attr."""
            prop = attr_prefix + prop
        loc = glGetAttribLocation(shader, prop)
        if loc == -1:
            print(' !!!----WARNING---!!!: Shader var. {:s} could not be found'.format(prop))
            continue

        size = int(np.prod(sub_dtype.shape))
        stride = vbo.dtype.itemsize
        offset = ctypes.c_void_p(offset)
        """Converitng poffset to void pointer"""

        glEnableVertexAttribArray(loc)
        """Binding attributes"""
        glVertexAttribPointer(
            index=loc,
            size=size,
            type=GL_FLOAT,
            normalized=GL_FALSE,
            stride=stride,
            pointer=offset)
        glVertexAttribDivisor(loc, divisor)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    """Unbinding buffer"""
