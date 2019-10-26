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
    m2D = session.query(Mesh).filter(Mesh.filename=='dataset/Armadillo/281.off').first()
    meshes = session.query(Mesh).all()

    distances = []
    files = []
    # area
    area_avg = session.query(func.avg(Mesh.area2D)).scalar()
    area_stddev = session.query(func.stddev_samp(Mesh.area2D)).scalar()
    # compactness
    compactness_avg = session.query(func.avg(Mesh.compactness2D)).scalar()
    compactness_stddev = session.query(func.stddev_samp(Mesh.compactness2D)).scalar()
    # rectangularity
    rectangularity_avg = session.query(func.avg(Mesh.rectangularity2D)).scalar()
    rectangularity_stddev = session.query(func.stddev_samp(Mesh.rectangularity2D)).scalar()
    # diameter
    diameter_avg = session.query(func.avg(Mesh.diameter2D)).scalar()
    diameter_stddev = session.query(func.stddev_samp(Mesh.diameter2D)).scalar()
    # eccentricity
    eccentricity_avg = session.query(func.avg(Mesh.eccentricity2D)).scalar()
    eccentricity_stddev = session.query(func.stddev_samp(Mesh.eccentricity2D)).scalar()
    # perimeter
    perimeter_avg = session.query(func.avg(Mesh.perimeter2D)).scalar()
    perimeter_stddev = session.query(func.stddev_samp(Mesh.perimeter2D)).scalar()
    # skeleton to perimeter ratio
    skeletonToPerimeterRatio_avg = session.query(func.avg(Mesh.skeletonToPerimeterRatio2D)).scalar()
    skeletonToPerimeterRatio_stddev = session.query(func.stddev_samp(Mesh.skeletonToPerimeterRatio2D)).scalar()
    # bbox area
    bbox_area_avg = session.query(func.avg(Mesh.bbox_area)).scalar()
    bbox_area_stddev = session.query(func.stddev(Mesh.bbox_area)).scalar()

    for i, mesh in enumerate(meshes):

        u = [(mesh.area2D-area_avg)/area_stddev,
             (mesh.perimeter2D-perimeter_avg)/perimeter_stddev,
             (mesh.rectangularity2D-rectangularity_avg)/rectangularity_stddev,
             (mesh.diameter2D-diameter_avg)/diameter_stddev,
             (mesh.skeletonToPerimeterRatio2D-skeletonToPerimeterRatio_avg)/skeletonToPerimeterRatio_stddev,
             (mesh.eccentricity2D-eccentricity_avg)/eccentricity_stddev,
             (mesh.compactness2D-compactness_avg)/compactness_stddev,
             (mesh.bbox_area-bbox_area_avg)/bbox_area_stddev]

        v = [(m2D.area2D - area_avg) / area_stddev,
             (m2D.perimeter2D - perimeter_avg) / perimeter_stddev,
             (m2D.rectangularity2D - rectangularity_avg) / rectangularity_stddev,
             (m2D.diameter2D - diameter_avg) / diameter_stddev,
             (m2D.skeletonToPerimeterRatio2D - skeletonToPerimeterRatio_avg) / skeletonToPerimeterRatio_stddev,
             (m2D.eccentricity2D - eccentricity_avg) / eccentricity_stddev,
             (m2D.compactness2D - compactness_avg) / compactness_stddev,
             (m2D.bbox_area - bbox_area_avg) / bbox_area_stddev]

        distances.append(distance.euclidean(u, v))
        files.append(mesh.filename)

    for i in range(20):
        max_dist = distances.index(min(distances))
        print ("Distance: {}, File: {}".format(distances[max_dist], files[max_dist]))

        del distances[max_dist]
        del files[max_dist]

    list_meshes = session.query(Mesh.filename).all()

if __name__ =='__main__':
    main()