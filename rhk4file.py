import struct
struct.Struct.unpack_from_file = lambda (self,f) : self.unpack(f.read(self.size))
struct.Struct.pack_to_file = lambda (self,f,*args) : f.write(self.pack(*args))

from collections import namedtuple

def getObjectList(f,n,parent):
  return [RHKObject(f,parent) for i in range(n) ]

def writeObjectList(f,os):
  for o in os:
    o.write_header(f)

class RHKObject:
  
  packer = struct.Struct("<III")

  classes = {}
  @classmethod
  def registerObjectType(t,c):
    RHKObject.classes[t] = c

  
  def __init__(self,parent,f):
    self.parent = parent
    self.objtype, self.offset, self.size = \
      RHKObject.packer.unpack(f.read(RHKObject.packer.size))
    self.children = []
    if self.objtype in RHKObject.classes:
      objclass = RHKObject.classes[self.objtype]
      self.read = objclass.read
      self.write = objclass.write 
  
  def read(self,f):
    f.seek(self.offset)
    self.contents = f.read(self.size)
  
  def read_children(self,f):
    for c in self.children:
      c.read(f)
  
  def write(self,f):
    f.write(self.contents)

  def read_children(self,f):
    for c in self.children:
      c.write(f)
  
  # TODO This needs some loving
  def write_header(self,f):
    pass
    
class RHKPageIndexHeader:
  
  # FIXME String not corresponding to definition
  packer = struct.Struct("<IIII")
  
  def read(self,f):
    f.seek(self.offset)
    r = RHKPageIndexHeader.packer.unpack_from_file(f)
    self.pagecount = r[0]
    self.children = getObjectList(f,r[1],self)
    self.reserved = r[2:]
    self.read_children(f)
  
  def write(self,f):
    RHKPageIndexHeader.packer.pack_to_file(f,self.pagecount,len(self.children),*self.reserved)
    writeObjectList(f,self.children)
    self.write_children(f)
    
class RHKPageIndexArray:
  
  packer = struct.Struct("<16sIIII")
  
  def read(self,f):
    self.pages = [RHKPageIndexArray.packer.unpack_from_file(f) for i in range(self.parent.pagecount)]
    self.children = getObjectList(f,len(self.pages),self)
    self.read_children(f)
  
  def write(self,f):
    pass
  
class RHKPageHeader:
  
  packer = struct.Struct("<HHIIIiiiiiiiIii3ff3f4f3iIB3B60B")
  
  def read(self,f):
    pass
  
  def write(self,f):
    pass

class RHKPageData:
  
  packer = struct.Struct()
  
  def read(self,f):
    pass
  
  def write(self,f):
    pass

class RHKImageDriftHeader:
  
  packer = struct.Struct()
  
  def read(self,f):
    pass
  
  def write(self,f):
    pass

class RHKImageDrift:
  
  packer = struct.Struct()
  
  def read(self,f):
    pass
  
  def write(self,f):
    pass

class RHKSpecDriftHeader:
  
  packer = struct.Struct()
  
  def read(self,f):
    pass
  
  def write(self,f):
    pass

class RHKSpecDriftData:
  
  packer = struct.Struct()
  
  def read(self,f):
    pass
  
  def write(self,f):
    pass

class RHKColorInfo:
  
  packer = struct.Struct()
  
  def read(self,f):
    pass
  
  def write(self,f):
    pass

class RHKStringData:
  
  packer = struct.Struct()
  
  def read(self,f):
    pass
  
  def write(self,f):
    pass

class RHKTipTrackHeader:
  
  packer = struct.Struct()
  
  def read(self,f):
    pass
  
  def write(self,f):
    pass

class RHKTipTrackData:
  
  packer = struct.Struct()
  
  def read(self,f):
    pass
  
  def write(self,f):
    pass

class RHK_PRM:
  
  packer = struct.Struct()
  
  def read(self,f):
    pass
  
  def write(self,f):
    pass

class RHKThumbnail:
  
  packer = struct.Struct()
  
  def read(self,f):
    pass
  
  def write(self,f):
    pass

class RHK_PRMHeader:
  
  packer = struct.Struct()
  
  def read(self,f):
    pass
  
  def write(self,f):
    pass

class RHKThumbnailHeader:
  
  packer = struct.Struct()
  
  def read(self,f):
    pass
  
  def write(self,f):
    pass

RHKObject.registerObjectType(1,RHKPageIndexHeader)
RHKObject.registerObjectType(2,RHKPageIndexArray)
RHKObject.registerObjectType(3,RHKPageHeader)
RHKObject.registerObjectType(4,RHKPageData)
#RHKObject.registerObjectType(5,RHKImageDriftHeader)
#RHKObject.registerObjectType(6,RHKImageDrift)
#RHKObject.registerObjectType(7,RHKSpecDriftHeader)
#RHKObject.registerObjectType(8,RHKSpecDriftData)
#RHKObject.registerObjectType(9,RHKColorInfo)
#RHKObject.registerObjectType(10,RHKStringData)
#RHKObject.registerObjectType(11,RHKTipTrackHeader)
#RHKObject.registerObjectType(12,RHKTipTrackData)
#RHKObject.registerObjectType(13,RHK_PRM)
#RHKObject.registerObjectType(14,RHKThumbnail)
#RHKObject.registerObjectType(15,RHK_PRMHeader)
#RHKObject.registerObjectType(16,RHKThumbnailHeader)

class RHK4File:
  
  packer = struct.Struct("<36sIIIII")
  
  def __init__(self,f):
    f.seek(0)
    r = RHK4File.packer.unpack_from_file(f)
    self.signature = r[0]
    self.pagecount = r[1]
    self.children = getObjectList(f,r[2],self)
    # FIXME ignoring r[3]
    self.reserved = r[4:]
    for c in self.children:
      c.read(f)
      
    # TODO: good place to restructure the data
  
  def write(self,f):
    RHK4File.pack_to_file(f,
      self.signature,
      self.pagecount,
      len(self.children),
      12,
      *self.reserved)
    writeObjectList(f,self.children)
    for c in self.children:
      c.write(f)