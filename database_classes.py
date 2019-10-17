from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, composite
from sqlalchemy.types import ARRAY

db = create_engine("postgres://Tiziano:Tnatali93@localhost/infomr")
base = declarative_base()

# create a configured "Session" class
Session = sessionmaker(bind=db)

# create a Session
session = Session()


class vec3f(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __composite_values__(self):
        return self.x, self.y, self.z

    def __repr__(self):
        return "Point(x=%r, y=%r, z=%r)" % (self.x, self.y, self.z)

    def __eq__(self, other):
        return isinstance(other, vec3f) and \
            other.x == self.x and \
            other.y == self.y and \
            other.z == self.z

    def __ne__(self, other):
        return not self.__eq__(other)


class Mesh(base):
    __tablename__ = "meshes"
    mesh_id = Column(Integer, primary_key=True)
    meshtype_id = Column(Integer, ForeignKey("meshtypes.meshtype_id"))
    filename = Column(String(50))
    area2D = Column(Integer)
    compactness2D = Column(Float)
    rectangularity2D = Column(Float)
    diameter2D = Column(Float)
    eccentricity2D = Column(Float)
    perimeter2D = Column(Integer)
    skeletonToPerimeterRatio2D = Column(Float)
    eigenvectors = relationship('Eigenvector')
    vertices = relationship('Vertex')


class Vertex(base):
    __tablename__ = "vertices"
    id = Column(Integer, primary_key=True)
    mesh_id = Column(Integer, ForeignKey('meshes.mesh_id'))
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
    pos = composite(vec3f, x, y, z)


class Polygon(base):
    __tablename__ = "triangular_polygons"
    vertex1_id = Column(Integer, ForeignKey('vertices.vertex_id'), primary_key=True)
    vertex2_id = Column(Integer, ForeignKey('vertices.vertex_id'), primary_key=True)
    vertex3_id = Column(Integer, ForeignKey('vertices.vertex_id'), primary_key=True)


class Eigenvector(base):
    __tablename__ = "eigenvectors"
    eigen_id = Column(Integer, primary_key=True)
    eigen_value = Column(Float)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
    mesh_id = Column(Integer, ForeignKey('meshes.mesh_id'))
    direction = composite(vec3f, x, y, z)


class Meshtype(base):
    __tablename__ = "meshtypes"

    meshtype_id = Column(Integer, primary_key=True)
    type = Column(String(50))
    averagevertices = Column(Integer)
    averagepolygons = Column(Integer)
    mesh = relationship("Mesh")

# session.add(Meshtype(type="Ant", averagevertices=2000, averagepolygons=8000))

q2 = session.query(Mesh).all()
q = session.query(Mesh.mesh_id).join(Meshtype).filter(Meshtype.type == 'Airplane').all()
print(q2)
# mesh = session.query(Mesh).filter(Mesh.meshtype_id in ).all()
# print(mesh[0].mesh_id)