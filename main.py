import meshTools
#import databaseTools
import Mesh
import os


def getofffiles(path):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if file.endswith('.off') and not file.endswith('_processed.off'):
                files.append(os.path.join(r, file))

    return files


def main():
    # files = getofffiles("dataset")

    # files = ["dataset/Airplane/64.off"]
    # for filepath in files:
    #     with open(filepath, "r") as f:
    #         shape, vertexes, faces = meshTools.read_off(f)
    #     m = Mesh.Mesh(filepath, vertexes, faces)
    #     m.setMeshToCenter()
    #     m.setBoundingBox()
    #     m.normalizeMesh()
    #     m.eigen()
    #     m.changingBase()
    #     m.setBoundingBox()
    #     m.normalizeMesh()
    #     m.flipTest()
    #     m.toFile()
    #     m.toimage()
    #
    meshTools.meshRenderer("dataset/Airplane/64_processed.off")

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