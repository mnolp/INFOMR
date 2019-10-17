import meshTools
import Mesh
import os
import Mesh2D
import database_classes as db_c
import threading


def getofffiles(path):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if file.endswith('.off') and not file.endswith('_processed.off'):
                files.append(os.path.join(r, file))

    return files


def main():
    files = getofffiles("dataset/Hand")
    # files = ["dataset/Airplane/63.off"]

    for filepath in files:
        print(filepath)
        with open(filepath, "r") as f:
            shape, vertexes, faces = meshTools.read_off(f)
        m = Mesh.Mesh(filepath, vertexes, faces)
        m.setMeshToCenter()
        m.eigen()
        m.changingBase()
        m.flipTest()
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
        ))
        db_c.session.commit()


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