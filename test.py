import lib.posix_ipc as pos
import os
import mmap
from ctypes import *
from _multiprocessing import address_of_buffer


class LinkedMem(Structure):
  _fields_ = [("uiVersion", c_uint32),
              ("uiTick", c_uint32),
              #
              ("fAvatarPosition", c_float * 3),
              ("fAvatarFront", c_float * 3),
              ("fAvatarTop", c_float * 3),
              ("name", c_wchar_p * 256),
              ("fCameraPosition", c_float * 3),
              ("fCameraFront", c_float * 3),
              ("fCameraTop", c_float * 3),
              ("identity", c_wchar_p * 256),
              #
              ("context_len", c_uint32),
              #
              ("context", c_ubyte * 256),
              ("description", c_wchar_p * 2048)]


class Test:
  
  _map = None
  _lm = LinkedMem()

  def start(self):
    self.open()
    while True:
      self.set()
    self.close()

  def open(self):
    _name = "/MumbleLink." + str(os.getuid())
    _mem = pos.SharedMemory(_name, flags=0, size=sizeof(LinkedMem))   #flag 0 means access
    print _mem.name
    self._map = mmap.mmap(_mem.fd, _mem.size)
    _mem.close_fd()
    addr, size = address_of_buffer(self._map)
    assert size == sizeof(LinkedMem)
    self._lm = LinkedMem.from_address(addr)
    self._lm.uiTick = 0
  
  def set(self):
    
    name_str = 'test'
    self._lm.name = (c_wchar_p * 256)(*[c_wchar_p(ord(c)) for c in name_str[:len(name_str)]])
     
    desc_str = "TestLink is a test of the Link plugin."
    self._lm.description = (c_wchar_p * 2048)(*[c_wchar_p(ord(c)) for c in desc_str[:len(desc_str)]])
    
    self._lm.uiVersion =  c_uint32(2);
      
    self._lm.uiTick = self._lm.uiTick + 1

  #Left handed coordinate system.
  #X positive towards "right".
  #Y positive towards "up".
  #Z positive towards "front".
  #1 unit = 1 meter

  #  // Unit vector pointing out of the avatars eyes (here Front looks into scene).
    self._lm.fAvatarFront[0] = c_float(0.0);
    self._lm.fAvatarFront[1] = c_float(0.0);
    self._lm.fAvatarFront[2] = c_float(1.0);

  #  // Unit vector pointing out of the top of the avatars head (here Top looks straight up).
    self._lm.fAvatarTop[0] = c_float(0.0);
    self._lm.fAvatarTop[1] = c_float(1.0);
    self._lm.fAvatarTop[2] = c_float(0.0);

  #  // Position of the avatar (here standing slightly off the origin)
    self._lm.fAvatarPosition[0] = c_float(-80.1);
    self._lm.fAvatarPosition[1] = c_float(0.0);
    self._lm.fAvatarPosition[2] = c_float(0.1);

  #  // Same as avatar but for the camera.
    self._lm.fCameraPosition[0] = c_float(0.0);
    self._lm.fCameraPosition[1] = c_float(0.0);
    self._lm.fCameraPosition[2] = c_float(0.0);

    self._lm.fCameraFront[0] = c_float(0.0);
    self._lm.fCameraFront[1] = c_float(0.0);
    self._lm.fCameraFront[2] = c_float(1.0);

    self._lm.fCameraTop[0] = c_float(0.0);
    self._lm.fCameraTop[1] = c_float(1.0);
    self._lm.fCameraTop[2] = c_float(0.0);

  #  #Identifier which uniquely identifies a certain player in a context (e.g. the ingame Name).
    ident_str = 'A1'
    self._lm.identity = (c_wchar_p * 256)(*[c_wchar_p(ord(c)) for c in ident_str[:len(ident_str)]])

  #  #Context should be equal for players which should be able to hear each other positional and
  #  #differ for those who shouldn't (e.g. it could contain the server+port and team)
    context_str = 'A'
    self._lm.context = (c_ubyte * 256)(*[c_ubyte(ord(c)) for c in context_str[:len(context_str)]])
    #print ''.join(map(chr, self._lm.context))
    self._lm.context_len = len(context_str);

  def close(self):
    self._map.close()

t = Test()
t.start() 
