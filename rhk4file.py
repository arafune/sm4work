import struct
from types import MethodType

class ExtStruct(struct.Struct):
	def __init__(self,fmt):
		super().__init__(fmt)
	
	def unpack_from_file(self,f):
		r = self.unpack(f.read(self.size))
		#print(r)
		return r

	def pack_to_file(self,f,*args):
		f.write(self.pack(*args))

from collections import namedtuple

def getObjectList(f,n,parent):
	return [RHKObject(f,parent) for i in range(n) ]

def writeObjectList(f,os):
	for o in os:
		o.write_header(f)

class RHKObject:
	
	packer = ExtStruct("<III")

	classes = {}
	@classmethod
	def registerObjectType(self,t,c):
		RHKObject.classes[t] = c

	
	def __init__(self,f,parent):
		self.parent = parent
		self.objtype, self.offset, self.size = \
			RHKObject.packer.unpack_from_file(f)
		self.children = []
		if self.objtype in RHKObject.classes:
			objclass = RHKObject.classes[self.objtype]
			if hasattr(objclass,'read'):
				self.read = MethodType(objclass.read, self)
			if hasattr(objclass,'write'):
				self.write = MethodType(objclass.write, self)
			if hasattr(objclass,'size_estimate'):
				self.size_estimate = MethodType(objclass.size_estimate, self)
			if hasattr(objclass,'__str__'):
				self.__str__ = MethodType(objclass.__str__, self)
	
	def read(self,f):
		f.seek(self.offset)
		self.contents = f.read(self.size)
	
	def read_children(self,f):
		for c in self.children:
			print(self.offset,c.objtype,c.size)
			c.read(f)
	
	def write(self,f):
		f.write(self.contents)

	def write_children(self,f):
		for c in self.children:
			c.write(f)
	
	def size_estimate(self):
		return self.size
	
	def recalculate_offset(self, minoffset):
		self.offset = minoffset
		self.size = self.size_estimate()
	
	def __str__(self):
		if self.objtype in RHKObject.classes:
			objclass = RHKObject.classes[self.objtype]
			return RHKObject.classes[self.objtype].__str__(self)
		
		this = "RHKObject of type {0.objtype} @ {0.offset} x{0.size}".format(self)
		if self.children:
			return this + "\n " + "\n ".join(str(c) for c in self.children)
		else:
			return this
	
	# TODO This needs some loving
	def write_header(self,f):
		pass
		
class RHKPageIndexHeader:
	
	# FIXME String not corresponding to definition
	packer = ExtStruct("<IIII")
	
	def read(self,f):
		f.seek(self.offset)
		r = RHKPageIndexHeader.packer.unpack_from_file(f)
		self.pagecount = r[0]
		self.children = getObjectList(f,r[1],self)
		self.reserved = r[2:]
		self.read_children(f)
	
	def write(self,f):
		RHKPageIndexHeader.packer.pack_to_file(f,
			self.pagecount,
			len(self.children),
			*self.reserved)
		writeObjectList(f,self.children)
		self.write_children(f)
		
	def __str__(self):
		return "RHKPageIndexHeader with {0.pagecount} pages @ {0.offset} x{0.size}\n ".format(self) + "\n ".join(str(c) for c in self.children)
	
	def size_estimate(self):
		return RHKPageIndexHeader.packer.size + \
		       sum(c.size_estimate() for c in self.children) + \
		       RHKObject.packer.size*len(self.children)

class RHKPage:
	
	packer = ExtStruct("<16sIIII")
		
	def __init__(self,f):
		self.info = RHKPage.packer.unpack_from_file(f)
		self.children = getObjectList(f,self.info[3],self)
	
	def read(self,f):
		for c in self.children:
			c.read(f)
			
	def __str__(self):
		return "RHKPage:\n " + "\n ".join(str(c) for c in self.children)
		
		
class RHKPageIndexArray:
	
	def read(self,f):
		f.seek(self.offset)
		self.pages = [RHKPage(f) for i in range(self.parent.pagecount)]	
		for page in self.pages:
			page.read(f)
	
	def write(self,f):
		pass

	def size_estimate(self):
		return RHKPageIndexArray.packer.size + \
		       sum(c.size_estimate() for c in self.children) + \
		       RHKObject.packer.size*len(self.children)

	def __str__(self):
		this = "RHKPageIndexArray @ {0.offset} x{0.size}".format(self)
		that = "\n ".join(str(p) for p in self.pages)
		return this + "\n " + that
	
class RHKPageHeader:
	
	packer = ExtStruct("<HHIIIiiiiiiiIii3ff3f4f3iIB3B60B")
	
	def read(self,f):
		f.seek(self.offset)
		self.header = RHKPageHeader.packer.unpack_from_file(f)
		self.strcount = self.header[1]
		self.objcount = self.header[29]
		self.children = getObjectList(f,self.objcount,self)
		self.read_children(f)
	
	def write(self,f):
		RHKPageHeader.packer.pack_to_file(f,self.header)

	def size_estimate(self):
		return RHKPageHeader.packer.size
	
	def __str__(self):
		return "RHKPageHeader @ {0.offset} x{0.size}\n ".format(self) + "\n ".join(str(c) for c in self.children)


#class RHKPageData:
	
	#def read(self,f):
		#pass
	
	#def write(self,f):
		#pass

#class RHKImageDriftHeader:
	
	#packer = ExtStruct()
	
	#def read(self,f):
		#pass
	
	#def write(self,f):
		#pass

#class RHKImageDrift:
	
	#packer = ExtStruct()
	
	#def read(self,f):
		#pass
	
	#def write(self,f):
		#pass

#class RHKSpecDriftHeader:
	
	#packer = ExtStruct()
	
	#def read(self,f):
		#pass
	
	#def write(self,f):
		#pass

#class RHKSpecDriftData:
	
	#packer = ExtStruct()
	
	#def read(self,f):
		#pass
	
	#def write(self,f):
		#pass

#class RHKColorInfo:
	
	#packer = ExtStruct()
	
	#def read(self,f):
		#pass
	
	#def write(self,f):
		#pass

class RHKStringData:
	
	packer = ExtStruct("<H")
	
	def read(self,f):
		f.seek(self.offset)
		self.strings = []
		for ins in range(self.parent.strcount):
			strlen = RHKStringData.packer.unpack_from_file(f)[0]
			self.strings.append( f.read(strlen*2).decode("utf-16") )
	
	def write(self,f):
		for s in self.strings:
			RHKStringData.packer.pack_to_file(f,len(s))
			f.write(s.encode("utf-16"))

	def __str__(self):
		return "RHKStringData @ {0.offset} x{0.size}\n ".format(self)+"\n ".join(self.strings)

#class RHKTipTrackHeader:
	
	#packer = ExtStruct()
	
	#def read(self,f):
		#pass
	
	#def write(self,f):
		#pass

#class RHKTipTrackData:
	
	#packer = ExtStruct()
	
	#def read(self,f):
		#pass
	
	#def write(self,f):
		#pass

#class RHK_PRM:
	
	#packer = ExtStruct()
	
	#def read(self,f):
		#pass
	
	#def write(self,f):
		#pass

#class RHKThumbnail:
	
	#packer = ExtStruct()
	
	#def read(self,f):
		#pass
	
	#def write(self,f):
		#pass

#class RHK_PRMHeader:
	
	#packer = ExtStruct()
	
	#def read(self,f):
		#pass
	
	#def write(self,f):
		#pass

#class RHKThumbnailHeader:
	
	#packer = ExtStruct()
	
	#def read(self,f):
		#pass
	
	#def write(self,f):
		#pass

RHKObject.registerObjectType(1,RHKPageIndexHeader)
RHKObject.registerObjectType(2,RHKPageIndexArray)
RHKObject.registerObjectType(3,RHKPageHeader)
#RHKObject.registerObjectType(4,RHKPageData)
#RHKObject.registerObjectType(5,RHKImageDriftHeader)
#RHKObject.registerObjectType(6,RHKImageDrift)
#RHKObject.registerObjectType(7,RHKSpecDriftHeader)
#RHKObject.registerObjectType(8,RHKSpecDriftData)
#RHKObject.registerObjectType(9,RHKColorInfo)
RHKObject.registerObjectType(10,RHKStringData)
#RHKObject.registerObjectType(11,RHKTipTrackHeader)
#RHKObject.registerObjectType(12,RHKTipTrackData)
#RHKObject.registerObjectType(13,RHK_PRM)
#RHKObject.registerObjectType(14,RHKThumbnail)
#RHKObject.registerObjectType(15,RHK_PRMHeader)
#RHKObject.registerObjectType(16,RHKThumbnailHeader)

class RHK4File:
	
	packer = ExtStruct("<36sIIIII")
	
	def __init__(self,f):
		f.seek(0)
		h_size = struct.unpack("H",f.read(2))[0]
		r = RHK4File.packer.unpack_from_file(f)
		if h_size > RHK4File.packer.size:
			self.header_pad = f.read(h_size - RHK4File.packer.size)
		self.signature = r[0]
		self.pagecount = r[1]
		self.children = getObjectList(f,r[2],self)
		# FIXME ignoring r[3]
		self.reserved = r[4:]
		for c in self.children:
			c.read(f)
			
		# TODO: good place to restructure the data
	
	def write(self,f):
		minoffset = RHK4File.packer.size + RHKObject.packer.size*len(self.children)
		for c in self.children:
			c.recalculate_offset(minoffset)
			minoffset = c.size + c.offset
			
		RHK4File.pack_to_file(f,
			self.signature,
			self.pagecount,
			len(self.children),
			12,
			*self.reserved)
		writeObjectList(f,self.children)
		for c in self.children:
			c.write(f)

if __name__ == "__main__":
	import sys
	filename = sys.argv[1]
	with open(filename,"rb") as f:
		RF = RHK4File(f)
		for c in RF.children:
			print(c)
