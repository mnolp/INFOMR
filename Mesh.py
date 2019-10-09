from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
from PIL import Image
import cv2
import glfw

# DISPLAY_WIDTH = 2000
# DISPLAY_HEIGHT = 2000


'''
This should be a struct.
DO NOT create object of type Mesh, use the two below. 
'''
class Mesh:
    def __init__(self, filename, vertices, faces):
        self.vertices = vertices
        self.faces = faces
        self.filename = filename
        self.numberOfVertices = len(vertices)
        self.numberOfFaces = len(faces)
        self.boundingBoxDimensions = (0, 0, 0)
        self.centerOfMass = (0, 0, 0)
        self.eigenvectors = []

    ''' 
    This method computes the center of mass of our point cloud.
    Then, it translates every vertex in the mesh by the found value
    in order to set the mesh to the center.
    '''
    def setMeshToCenter(self):
        sumValues = [0, 0, 0]

        for i in range(3):
            for vertex in self.vertices:
                sumValues[i] += vertex[i]
            sumValues[i] /= len(self.vertices)

        self.centerOfMass = (sumValues[0], sumValues[1], sumValues[2])

        for i in range(len(self.vertices)):
            for j in range(3):
                self.vertices[i][j] -= sumValues[j]
        self.setBoundingBox()


    def setBoundingBox(self):
        minValues, maxValues = [sys.maxsize]*3, [0]*3

        for vertex in self.vertices:
            for i in range(3):
                if vertex[i] < minValues[i]: minValues[i] = vertex[i]
                if vertex[i] > maxValues[i]: maxValues[i] = vertex[i]

        self.boundingBoxDimensions = (maxValues[0]-minValues[0], maxValues[1]-minValues[1], maxValues[2]-minValues[2])


    def normalizeMesh(self):
        for i in range(len(self.vertices)):
            for j in range(3):
                self.vertices[i][j] /= max(self.boundingBoxDimensions)
        self.setBoundingBox()


    def toFile(self):
        with open(self.filename[: self.filename.rfind(".")]+"_processed"+self.filename[self.filename.rfind("."):], "w") as outf:
            outf.write("OFF\n")
            outf.write(str(self.numberOfVertices)+" "+str(self.numberOfFaces)+" 0\n")
            for vertex in self.vertices:
                s = ""
                if type(vertex) is int:
                    s += str(vertex)
                else:
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
        checkedvertices = []

        for face in self.faces:
            for i in range(3):
                j = 0 if i == 2 else i+1
                if not (face[i] in checkedvertices and face[j] in checkedvertices):
                    checkedvertices.append([face[i], face[j]])
                    edgesLength.append((
                        pow(self.vertices[face[i]][0] - self.vertices[face[j]][0], 2) + pow(self.vertices[face[i]][1] - self.vertices[face[j]][1], 2) + pow(self.vertices[face[i]][2] - self.vertices[face[j]][2], 2),
                        face[i],
                        face[j]
                    ))

        edgesLength.sort()
        count = 0
        while count<500:
            for i in range(len(edgesLength)):
                if count >= 500:
                    break
                v1 = self.vertices[edgesLength[i][1]]
                v2 = self.vertices[edgesLength[i][2]]
                if v1 != -1 and v2 != -1:
                    midpoint = [(v1[0]+v2[0])/2, (v1[1]+v2[1])/2, (v1[2]+v2[2])/2]
                    for j in range(len(self.faces)):
                        for k in range(3):
                            if self.faces[j][k] == edgesLength[i][2]: self.faces[j][k] = edgesLength[i][1]
                    self.vertices[edgesLength[i][1]] = midpoint
                    self.vertices[edgesLength[i][2]] = -1
                    count += 1

        newFaces = []
        for i in range(len(self.faces)):
            if not self.faces[i] in newFaces:
                flag = True
                for j in range(len(self.faces[i])-1):
                    if self.faces[i].count(self.faces[i][j])>1:
                        flag = False
                if flag:
                    newFaces.append(self.faces[i])

        self.faces = newFaces
        self.numberOfFaces = len(self.faces)
        self.numberOfVertices = len(self.vertices)


    def eigen(self):
        A = np.zeros((3, len(self.vertices)))
        for i in range(3):
            for j in range(len(self.vertices)):
                A[i][j] = self.vertices[j][i]

        A_cov = np.cov(A)  # 3x3 matrix

        eigenvalues, eigenvectors = np.linalg.eig(A_cov)
        temp = eigenvalues.tolist()
        eigenvectors = eigenvectors.tolist()
        eigenvectorssorted = []
        for i in range(3):
            # index = np.where(temp == max(temp))
            index = temp.index(max(temp))
            eigenvectorssorted.append(eigenvectors[index])
            del eigenvectors[temp.index(max(temp))]
            temp.remove(max(temp))

        self.eigenvectors = eigenvectorssorted


    def changingBase(self):
        for i in range(len(self.vertices)):
            if not self.vertices[i] == -1:
                temp = np.dot(self.eigenvectors, self.vertices[i])
                self.vertices[i] = [temp[0], temp[1], temp[2]]
        self.eigen()

    def flipTest(self):
        sumpos = [0, 0, 0]
        sumneg = [0, 0, 0]
        vertices = self.vertices

        for i in range(len(vertices)):
            for j in range(3):
                if vertices[i][j]<=0: sumneg[j]+=1
                else: sumpos[j] += 1

        flag = [False, False, False]
        for j in range(3):
            if sumpos[j] > sumneg[j]:
                flag[j] = True
        for i in range(len(vertices)):
            if flag[0]:
                vertices[i][0] = - vertices[i][0]
            if flag[1]:
                vertices[i][1] = - vertices[i][1]
            if flag[2]:
                vertices[i][2] = - vertices[i][2]

    def toimage(self):
        width = 2560
        height = 1510
        x = 0
        y = 0
        # Initialize the library
        if not glfw.init():
            return
        # Set window hint NOT visible
        # glfw.window_hint(glfw.VISIBLE, False)

        # Create a windowed mode window and its OpenGL context
        window = glfw.create_window(width, height, "hidden window", None, None)
        if not window:
            glfw.terminate()
            return

        glfw.make_context_current(window)

        glClearColor(1, 1, 1, 1)
        # gluLookAt(0, 0, -g_fViewDistance, 0, 0, 0, -.1, 0, 0)  # -.1,0,0
        # gluPerspective(90, (DISPLAY_WIDTH / DISPLAY_HEIGHT), 0.01, 12)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        # glEnable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_COLOR_MATERIAL)
        glColor3f(0, 0, 0)
        glBegin(GL_TRIANGLES)
        for face in self.faces:
            for vertex in face:
                glVertex3fv(self.vertices[vertex])
        glEnd()
        x, y, width, height = glGetIntegerv(GL_VIEWPORT)
        glPixelStorei(GL_PACK_ALIGNMENT, 1)

        data = glReadPixels(x, y, width, height, GL_RGB, GL_UNSIGNED_BYTE)
        image = Image.frombytes("RGB", (width, height), data)
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
        image.save("image.png", format="png")
        #
        # image = np.fromstring(image_buffer, dtype=np.uint8).reshape(DISPLAY_HEIGHT, DISPLAY_WIDTH, 3)
        # cv2.imwrite("image.png", np.fliplr(image))
        # glfw.destroy_window(window)
        # glfw.terminate()

class TrianglesMesh(Mesh):
    def __init__(self, vertices, numberOfFaces):
        self.poligonType = 3
        Mesh.__init__(vertices, numberOfFaces)

    def draw(self):
        glBegin(GL_TRIANGLES)
        # TODO fill draw method
        glEnd()


class QuadsMesh(Mesh):
    def __init__(self, vertices, numberOfFaces):
        self.poligonType = 4
        Mesh.__init__(vertices, numberOfFaces)

    def draw(self):
        glBegin(GL_QUADS)
        # TODO fill draw method
        glEnd()