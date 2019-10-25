import meshTools
import Mesh
import os
import Mesh2D
import database_classes as db_c
from sqlalchemy import func
import time
from scipy.spatial import distance


def getofffiles(path):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if file.endswith('.off') and not file.endswith('_processed.off'):
                files.append(os.path.join(r, file))

    return files


def add_mesh(filepath, m2D):
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
    ))
    db_c.session.commit()

def standardise_database():
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


    meshes = db_c.session.query(db_c.Mesh).all()
    for mesh in meshes:
        mesh.area2D = (mesh.area2D-area_avg)/area_stddev
        mesh.perimeter2D = (mesh.perimeter2D - perimeter_avg) / perimeter_stddev
        mesh.eccentricity2D = (mesh.eccentricity2D - eccentricity_avg) / eccentricity_stddev
        mesh.compactness2D = (mesh.compactness2D - compactness_avg) / compactness_stddev
        mesh.rectangularity2D = (mesh.rectangularity2D - rectangularity_avg) / rectangularity_stddev
        mesh.diameter2D = (mesh.diameter2D - diameter_avg) / diameter_stddev
        mesh.skeletonToPerimeterRatio2D = (mesh.skeletonToPerimeterRatio2D - skeletonToPerimeterRatio_avg) / skeletonToPerimeterRatio_stddev
        mesh.bbox_area = (mesh.bbox_area-bbox_area_avg)/bbox_area_stddev

def main():
    start_time = time.time()
    files = getofffiles("dataset")
    # files = ["dataset/Airplane/61.off"]

    for n, filepath in enumerate(files, 1):
        print ("Number {} out of {}, file: {}".format(n, len(files), filepath))
        with open(filepath, "r") as f:
            shape, vertexes, faces = meshTools.read_off(f)
        m = Mesh.Mesh(filepath, vertexes, faces)
        m.setMeshToCenter()
        m.eigen()
        m.changingBase()
        # m.flipTest()
        m.setBoundingBox()
        m.normalizeMesh()
        processed_file = m.toFile()
        filepath2D = m.toimage()

        m2D = Mesh2D.Mesh2D(filepath2D)

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

    # standardise_database()


    # m2D = db_c.session.query(db_c.Mesh).filter(db_c.Mesh.filename==filepath).first()
    # meshes = db_c.session.query(db_c.Mesh).all()
    #
    # distances = []
    # files = []
    # for i, mesh in enumerate(meshes):
    #
    #     u = [mesh.area2D,
    #          mesh.perimeter2D,
    #          mesh.rectangularity2D,
    #          mesh.diameter2D,
    #          mesh.skeletonToPerimeterRatio2D,
    #          mesh.eccentricity2D,
    #          mesh.compactness2D]
    #
    #     v = [m2D.area2D,
    #          m2D.perimeter2D,
    #          m2D.rectangularity2D,
    #          m2D.diameter2D,
    #          m2D.skeletonToPerimeterRatio2D,
    #          m2D.eccentricity2D,
    #          m2D.compactness2D]
    #
    #     distances.append(distance.euclidean(u, v))
    #     files.append(mesh.filename)
    #
    # for i in range(10):
    #     max_dist = distances.index(min(distances))
    #     print ("File: {}, Distance: {}".format(files[max_dist], distances[max_dist]))
    #
    #     del distances[max_dist]
    #     del files[max_dist]
    #
    # print("Elapsed time: {}".format(time.time()-start_time))
    #



    # area, perimeter = feature_extraction.get_area_perimeter("dataset/Airplane/62_silhouette.png")
    # print ("Area: {}\nPerimeter: {}".format(area, perimeter))

    # meshTools.meshRenderer("dataset/Airplane/62_processed.off", m.eigenvectors)

    # a, b = databaseTools.claReader("benchmark/classification/v1/base/train.cla")
    # with open("out.txt", "w") as f:
    #     for i in range(1815):
    #         label = databaseTools.assignModelToClass(a, b, str(i))
    #         if label != None:
    #             f.write(str(i)+" "+label+"\n")
    # databaseTools.data_analysis()
    # meshTools.meshReducer("dataset/Airplane/61.off")


if __name__ == "__main__":
    main()