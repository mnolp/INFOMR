import meshTools
import Mesh
import os
import Mesh2D
import database_classes as db_c
from sqlalchemy import func
import time
from scipy.spatial import distance
from scipy.stats import wasserstein_distance


def getofffiles(path):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if file.endswith('.off') and not file.endswith('_processed.off'):
                files.append(os.path.join(r, file))

    return files

def getpngfiles(path):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if file.endswith('.png'):
                files.append(os.path.join(r, file))

    return files


def add_mesh(filepath, m, m2D):
    db_c.session.add(db_c.Mesh(
        filename=filepath,
        meshtype_id=db_c.session.query(db_c.Meshtype.meshtype_id).filter(
            db_c.Meshtype.type == filepath[
                                  filepath[:filepath.rfind('/')].rfind('/') + 1: filepath.rfind('/')]).first()[
            0],
        area2D=m2D.area,
        compactness2D=m2D.compactness,
        rectangularity2D=m2D.rectangularity,
        diameter2D=m2D.diameter,
        eccentricity2D=m.eigenvalues[0] / m.eigenvalues[1],
        perimeter2D=m2D.perimeter,
        skeletonToPerimeterRatio2D=m2D.skeleton_length / m2D.perimeter,
        bbox_area=abs(m2D.bounding_box[0]*m2D.bounding_box[1])
    ))
    db_c.session.commit()

def update_mesh(filepath, m):
    m2D = Mesh2D.Mesh2D(
        filepath[: filepath.rfind('/')] + filepath[filepath.rfind('/'): filepath.rfind('.')] + "_silhouette.png")

    q = db_c.session.query(db_c.Mesh).filter(db_c.Mesh.filename == filepath).first()
    q.area2D = m2D.area
    q.compactness2D = m2D.compactness
    q.rectangularity2D = m2D.rectangularity
    q.diameter2D = m2D.diameter
    q.eccentricity2D = m.eigenvalues[0] / m.eigenvalues[1]
    q.perimeter2D = m2D.perimeter
    q.skeletonToPerimeterRatio2D = m2D.skeleton_length / m2D.perimeter
    q.bbox_area = float(m2D.bounding_box[0] * m2D.bounding_box[1])

    db_c.session.commit()





def matching_std(filepath):
    # area
    area_avg = db_c.session.query(func.avg(db_c.Mesh.area2D)).scalar()
    area_stddev = db_c.session.query(func.stddev(db_c.Mesh.area2D)).scalar()
    # perimeter
    perimeter_avg = db_c.session.query(func.avg(db_c.Mesh.perimeter2D)).scalar()
    perimeter_stddev = db_c.session.query(func.stddev(db_c.Mesh.perimeter2D)).scalar()
    # rectangularity
    rectangularity_avg = db_c.session.query(func.avg(db_c.Mesh.rectangularity2D)).scalar()
    rectangularity_stddev = db_c.session.query(func.stddev(db_c.Mesh.rectangularity2D)).scalar()
    # compactness
    compactness_avg = db_c.session.query(func.avg(db_c.Mesh.compactness2D)).scalar()
    compactness_stddev = db_c.session.query(func.stddev(db_c.Mesh.compactness2D)).scalar()
    # diameter
    diameter_avg = db_c.session.query(func.avg(db_c.Mesh.diameter2D)).scalar()
    diameter_stddev = db_c.session.query(func.stddev(db_c.Mesh.diameter2D)).scalar()
    # eccentricity
    eccentricity_avg = db_c.session.query(func.avg(db_c.Mesh.eccentricity2D)).scalar()
    eccentricity_stddev = db_c.session.query(func.stddev(db_c.Mesh.eccentricity2D)).scalar()
    # skeletonToPerimeterRatio
    skeletonToPerimeterRatio_avg = db_c.session.query(func.avg(db_c.Mesh.skeletonToPerimeterRatio2D)).scalar()
    skeletonToPerimeterRatio_stddev = db_c.session.query(func.stddev(db_c.Mesh.skeletonToPerimeterRatio2D)).scalar()
    # bbox_area
    bbox_area_avg = db_c.session.query(func.avg(db_c.Mesh.bbox_area)).scalar()
    bbox_area_stddev = db_c.session.query(func.stddev(db_c.Mesh.bbox_area)).scalar()

    m2D = db_c.session.query(db_c.Mesh).filter(db_c.Mesh.filename==filepath).first()
    meshes = db_c.session.query(db_c.Mesh).all()

    distances = []
    files = []
    for i, mesh in enumerate(meshes):

        u = [(mesh.area2D-area_avg)/area_stddev,
             (mesh.perimeter2D-perimeter_avg)/perimeter_stddev,
             (mesh.rectangularity2D-rectangularity_avg)/rectangularity_stddev,
             (mesh.diameter2D-diameter_avg)/diameter_stddev,
             (mesh.skeletonToPerimeterRatio2D-skeletonToPerimeterRatio_avg)/skeletonToPerimeterRatio_stddev,
             (mesh.eccentricity2D-eccentricity_avg)/eccentricity_stddev,
             (mesh.compactness2D-compactness_avg)/compactness_stddev]

        v = [(m2D.area2D-area_avg)/area_stddev,
             (m2D.perimeter2D-perimeter_avg)/perimeter_stddev,
             (m2D.rectangularity2D-rectangularity_avg)/rectangularity_stddev,
             (m2D.diameter2D-diameter_avg)/diameter_stddev,
             (m2D.skeletonToPerimeterRatio2D-skeletonToPerimeterRatio_avg)/skeletonToPerimeterRatio_stddev,
             (m2D.eccentricity2D-eccentricity_avg)/eccentricity_stddev,
             (m2D.compactness2D-compactness_avg)/compactness_stddev]

        distances.append(distance.euclidean(u, v))
        files.append(mesh.filename)

    for i in range(30):
        max_dist = distances.index(min(distances))
        print ("File: {}, Distance: {}".format(files[max_dist], distances[max_dist]))

        del distances[max_dist]
        del files[max_dist]



def main():
    # files = getofffiles("dataset/")
    files = ["dataset/Plier/201.off"]
    #
    for n, filepath in enumerate(files, 1):
        start_time = time.time()

        # print ("Number {} out of {}, file: {}".format(n, len(files), filepath))
        # with open(filepath, "r") as f:
        #     shape, vertexes, faces = meshTools.read_off(f)
        # m = Mesh.Mesh(filepath, vertexes, faces)
        # m.setMeshToCenter()
        # m.eigen()
        # m.changingBase()
        # m.setBoundingBox()
        # m.normalizeMesh()
        # m.flipTest()
        # processed_file = m.toFile()
        # filepath2D = m.toimage()
        # update_mesh(filepath, m)

        # meshTools.meshRenderer(processed_file, m.eigenvectors)
        matching_std(filepath)
        print("Elapsed time: {}".format(time.time()-start_time))


    # m2D2 = Mesh2D.Mesh2D("dataset/Airplane/80_silhouette.png")
    #
    # print(m2D1.area)
    # print(m2D2.area)




if __name__ == "__main__":
    main()