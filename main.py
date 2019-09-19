import meshTools
import databaseTools

def main():
    # meshTools.meshRenderer()
    # a, b = databaseTools.claReader("benchmark/classification/v1/base/train.cla")
    # with open("out.txt", "w") as f:
    #     for i in range(1815):
    #         label = databaseTools.assignModelToClass(a, b, str(i))
    #         if label != None:
    #             f.write(str(i)+" "+label+"\n")
    databaseTools.data_analysis()

if __name__ == "__main__":
    main()