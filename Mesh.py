from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
from PIL import Image
import cv2, math
import glfw
import Mesh2D

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
        self.eigenvectors = []
        self.eigenvalues = []
        self.boundingBoxDimensions = []
        # self.old_eignvectors = []
        # self.mesh2d = Mesh2D.Mesh2D(self.toimage())

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

        for i in range(len(self.vertices)):
            for j in range(3):
                self.vertices[i][j] -= sumValues[j]

    '''
    This method find the bounding box of the mesh
    Run first eigen() and changingBase() to find oriented bounding box
    '''
    def setBoundingBox(self):
        minValues, maxValues = [sys.maxsize]*3, [0]*3

        for vertex in self.vertices:
            for i in range(3):
                if vertex[i] < minValues[i]: minValues[i] = vertex[i]
                if vertex[i] > maxValues[i]: maxValues[i] = vertex[i]

        return (maxValues[0]-minValues[0], maxValues[1]-minValues[1], maxValues[2]-minValues[2])

    '''
    This function scales the mesh to fit in the unary box (-0.5, 0.5)
    '''
    def normalizeMesh(self):
        for i in range(len(self.vertices)):
            for j in range(3):
                self.vertices[i][j] /= max(self.boundingBoxDimensions)
        self.setBoundingBox()

    '''
    This method dump the mesh to file in .off format
    '''
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


    '''
    Reduce the amount of polygons in the mesh
    '''
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

    '''
    This function finds and sort by dimension the eigen vectors'''
    def eigen(self):
        A = np.zeros((3, len(self.vertices)))
        for i in range(3):
            for j in range(len(self.vertices)):
                A[i][j] = self.vertices[j][i]

        A_cov = np.cov(A)  # 3x3 matrix

        eigenvalues, eigenvectors = np.linalg.eig(A_cov)
        print(eigenvectors)
        print(eigenvalues)
        self.eigenvalues = eigenvalues
        temp = eigenvalues.tolist()
        eigenvectors = eigenvectors.tolist()
        eigenvectorssorted = []
        for i in range(3):
            # index = np.where(temp == max(temp))
            index = temp.index(max(temp))
            eigenvectorssorted.append(eigenvectors[index])
            del eigenvectors[temp.index(max(temp))]
            temp.remove(max(temp))
        print(eigenvectorssorted)
        # self.old_eignvectors = self.eigenvectors
        return eigenvectorssorted

    '''
    This function change our reference system in accord to the eigen vectors found
    '''
    def changingBase(self):
        print(self.vertices[0])
        for i in range(len(self.vertices)):
            if not self.vertices[i] == -1:
                # temp = np.dot(self.eigenvectors, self.vertices[i])
                temp = np.dot(self.vertices[i], self.eigenvectors)
                self.vertices[i] = [temp[0], temp[1], temp[2]]
        print(self.vertices[0])
        self.eigen()

    '''
    This function checks if the mesh is correctly oriented.
    If not the mesh is flipped.
    '''
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

    '''
    This function save to .png file the silhouette of the mesh
    '''
    def toimage(self):
        width = 600
        height = 600
        x = 0
        y = 0

        if not glfw.init():
            return
        glfw.window_hint(glfw.VISIBLE, False)
        window = glfw.create_window(width, height, "hidden window", None, None)
        if not window:
            glfw.terminate()
            return
        glfw.make_context_current(window)

        glClearColor(1, 1, 1, 1)
        glDisable(GL_LIGHTING)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        z_vec = 0
        z = 0
        for i in range(len(self.eigenvectors)):
            if abs(self.eigenvectors[i][2])>z: z_vec = i

        gluLookAt(
            self.eigenvectors[z_vec][0], self.eigenvectors[z_vec][1], self.eigenvectors[z_vec][2],              # eye position
            # 0, 0, 0,
            0, 0, 0,                                                                                # focus point
            0, 1, 0                                                                                 # up vector
        )

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-1, 1, -1, 1, -5, 5)

        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_COLOR_MATERIAL)
        glColor3f(0, 0, 0)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glBegin(GL_TRIANGLES)
        for face in self.faces:
            for vertex in face:
                glVertex3fv(self.vertices[vertex])
        glEnd()
        glBegin(GL_LINES)
        # draw line for x axis
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3fv(self.eigenvectors[0])
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3fv(self.eigenvectors[1])
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0, 0, 0)
        glVertex3fv(self.eigenvectors[2])
        glEnd()
        glFlush()


        x, y, width, height = glGetIntegerv(GL_VIEWPORT)
        glPixelStorei(GL_PACK_ALIGNMENT, 1)

        data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
        image = Image.frombytes("RGB", (width, height), data)
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
        imagename = self.filename[: self.filename.rfind('/')] + self.filename[self.filename.rfind('/'): self.filename.rfind('.')] + "_silhouette.png"
        image.save(imagename, format="png")

        glfw.destroy_window(window)
        glfw.terminate()

        return imagename

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