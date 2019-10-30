from sqlalchemy import create_engine, func
from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, composite
import sys
from scipy.spatial import distance
from scipy import stats



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


class Distance(base):
    __tablename__ = "distances"

    mesh1_id = Column(Integer, ForeignKey('meshes.mesh_id'), primary_key=True)
    mesh2_id = Column(Integer, ForeignKey('meshes.mesh_id'), primary_key=True)
    mesh1 = relationship("Mesh", foreign_keys=[mesh1_id])
    mesh2 = relationship("Mesh", foreign_keys=[mesh2_id])
    value = Column(Float)


# session.add(Meshtype(type="Ant", averagevertices=2000, averagepolygons=8000))


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



def main():
    distances = session.query(Distance).all()

    checked = []
    for i, distance in enumerate(distances):
        print(i)
        if not sorted([distance.mesh1_id, distance.mesh2_id]) in checked:
            checked.append(sorted([distance.mesh1_id, distance.mesh2_id]))
        else:
            session.query(Distance).filter(Distance.mesh1_id==distance.mesh1_id and Distance.mesh2_id==distance.mesh2_id).delete()
    session.commit()

if __name__ =='__main__':
    main()