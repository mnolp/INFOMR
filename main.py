import meshTools
import databaseTools
import Mesh


def main():
    filepath = "dataset/Airplane/61.off"
    # meshTools.meshRenderer()
    with open(filepath, "r") as f:
        shape, vertexes, faces = meshTools.read_off(f)
    m = Mesh.Mesh(filepath, vertexes, faces)
    m.meshCrasher()
    # m.setMeshToCenter()
    # m.normalizeMesh()
    # m.toFile()

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