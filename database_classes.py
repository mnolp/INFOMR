from sqlalchemy import create_engine, func
from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, composite
from sqlalchemy.types import ARRAY
import sys

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
    area2D = Column(Float)
    compactness2D = Column(Float)
    rectangularity2D = Column(Float)
    diameter2D = Column(Float)
    eccentricity2D = Column(Float)
    perimeter2D = Column(Float)
    skeletonToPerimeterRatio2D = Column(Float)
    bbox_area = Column(Float)
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

# area
# area_avg = session.query(func.avg(Mesh.area2D)).scalar()
# area_stddev = session.query(func.stddev_samp(Mesh.area2D)).scalar()
# # compactness
# compactness2D = session.query(func.avg(Mesh.compactness2D)).scalar()
# compactness2D = session.query(func.stddev_samp(Mesh.compactness2D)).scalar()
# # rectangularity
# rctn_avg = session.query(func.avg(Mesh.rectangularity2D)).scalar()
# rctn_stddev = session.query(func.stddev_samp(Mesh.rectangularity2D)).scalar()
# # diameter
# dmtr_avg = session.query(func.avg(Mesh.diameter2D)).scalar()
# dmtr_stddev = session.query(func.stddev_samp(Mesh.diameter2D)).scalar()
# # eccentricity
# eccn_avg = session.query(func.avg(Mesh.eccentricity2D)).scalar()
# eccn_stddev = session.query(func.stddev_samp(Mesh.eccentricity2D)).scalar()
# # perimeter
# prmtr_avg = session.query(func.avg(Mesh.perimeter2D)).scalar()
# prmtr_stddev = session.query(func.stddev_samp(Mesh.perimeter2D)).scalar()
# # skeleton to perimeter ratio
# sktprt_avg = session.query(func.avg(Mesh.skeletonToPerimeterRatio2D)).scalar()
# sktprt_stddev = session.query(func.stddev_samp(Mesh.skeletonToPerimeterRatio2D)).scalar()
#
# meshes = session.query(Mesh).all()
#
# for i in range(len(meshes)):
#     meshes[i].area2D = (meshes[i].area2D-area_avg)/area_stddev
#     meshes[i].compactness2D = (meshes[i].compactness2D - compactness2D) / compactness2D
#     meshes[i].rectangularity2D = (meshes[i].rectangularity2D - rctn_avg) / rctn_stddev
#     meshes[i].diameter2D = (meshes[i].diameter2D - dmtr_avg) / dmtr_stddev
#     meshes[i].eccentricity2D = (meshes[i].eccentricity2D - eccn_avg) / eccn_stddev
#     meshes[i].perimeter2D = (meshes[i].perimeter2D - prmtr_avg) / prmtr_stddev
#     meshes[i].skeletonToPerimeterRatio2D = (meshes[i].skeletonToPerimeterRatio2D - sktprt_avg) / sktprt_stddev
# session.commit()

# print("Average: {},\nStandard deviation: {}".format(area_avg, area_stddev))