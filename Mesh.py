from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


'''
This should be a struct.
DO NOT create object of type Mesh, use the two below. 
'''
class Mesh:
    def __init__(self, filename, vertexes, faces):
        self.vertexes = vertexes
        self.faces = faces
        self.filename = filename
        self.numberOfVertices = len(vertexes)
        self.numberOfFaces = len(faces)
        self.boundingBoxDimensions = (0, 0, 0)

    ''' 
    This method computes the center of mass of our point cloud.
    Then, it translates every vertex in the mesh by the found value
    in order to set the mesh to the center.
    '''
    def setMeshToCenter(self):
        sumValues = [0, 0, 0]

        for i in range(3):
            for vertex in self.vertexes:
                sumValues[i] += vertex[i]
            sumValues[i] /= len(self.vertexes)

        for i in range(len(self.vertexes)):
            for j in range(3):
                self.vertexes[i][j] -= sumValues[j]
        self.setBoundingBox()


    def setBoundingBox(self):
        minValues, maxValues = [sys.maxsize]*3, [0]*3

        for vertex in self.vertexes:
            for i in range(3):
                if vertex[i] < minValues[i]: minValues[i] = vertex[i]
                if vertex[i] > maxValues[i]: maxValues[i] = vertex[i]

        self.boundingBoxDimensions = (maxValues[0]-minValues[0], maxValues[1]-minValues[1], maxValues[2]-minValues[2])


    def normalizeMesh(self):
        for i in range(len(self.vertexes)):
            for j in range(3):
                self.vertexes[i][j] /= max(self.boundingBoxDimensions)
        self.setBoundingBox()


    def toFile(self):
        with open(self.filename[: self.filename.rfind(".")]+"_processed"+self.filename[self.filename.rfind("."):], "w") as outf:
            outf.write("OFF\n")
            outf.write(str(self.numberOfVertices)+" "+str(self.numberOfFaces)+" 0\n")
            for vertex in self.vertexes:
                s = ""
                for v in range(len(vertex)):
                    if v == 0:
                        s += str(vertex[v])
                    else:
                        s += " "+str(vertex[v])
                outf.write(s+"\n")
            for face in self.faces:
                s = str(len(face))
                for v in face:
                    s += " "+str(v)
                outf.write(s+"\n")

    def meshCrasher(self):
        edgesLength = []
        print(len(self.vertexes))
        for face in self.faces:
            for i in range(3):
                j = 0 if i == 2 else i+1
                edgesLength.append((
                    pow(self.vertexes[face[i]][0] - self.vertexes[face[j]][0], 2) + pow(self.vertexes[face[i]][1] - self.vertexes[face[j]][1], 2) + pow(self.vertexes[face[i]][2] - self.vertexes[face[j]][2], 2),
                    face[i],
                    face[j]
                ))

        edgesLength.sort()
        for i in range(100):
            v1, v2 = self.vertexes[edgesLength[i][1]], self.vertexes[edgesLength[i][2]]
            midpoint = [(v1[0]+v2[0])/2, (v1[1]+v2[1])/2, (v1[2]+v2[2])/2]
            for j in range(len(self.faces)):
                for k in range(3):
                    if self.faces[j][k] == edgesLength[i][2]: self.faces[j][k] = edgesLength[i][1]
            self.vertexes[edgesLength[i][1]] = midpoint
            self.vertexes[edgesLength[i][2]] = -1

        i=0
        while(i<len(self.vertexes)):
            if self.vertexes == -1:
                del self.vertexes[i]
                i-=1
            i+=1

        print(len(self.vertexes))





class TrianglesMesh(Mesh):
    def __init__(self, vertexes, numberOfFaces):
        self.poligonType = 3
        Mesh.__init__(vertexes, numberOfFaces)

    def draw(self):
        glBegin(GL_TRIANGLES)
        # TODO fill draw method
        glEnd()


class QuadsMesh(Mesh):
    def __init__(self, vertexes, numberOfFaces):
        self.poligonType = 4
        Mesh.__init__(vertexes, numberOfFaces)

    def draw(self):
        glBegin(GL_QUADS)
        # TODO fill draw method
        glEnd()