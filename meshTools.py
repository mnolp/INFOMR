from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
from PIL import Image

# -----------
# VARIABLES
# -----------


g_fViewDistance = 1.5
g_Width = 600
g_Height = 600

g_nearPlane = 1.
g_farPlane = 1000.

action = ""
xStart = yStart = 0.
zoom = 65.

xRotate = 0.
yRotate = 0.
zRotate = 0.

xTrans = 0.
yTrans = 0.

FILE_PATH = ''


# -------------------
# SCENE CONSTRUCTOR
# -------------------


def read_off(file):
    if 'OFF' != file.readline().strip():
        raise('Not a valid OFF header')
    n_verts, n_faces, n_edges = tuple([int(s) for s in file.readline().strip().split(' ')])
    verts = [[float(s) for s in file.readline().strip().split(' ')] for i_vert in range(n_verts)]
    faces = []
    for i_face in range(n_faces):
        s = file.readline()
        s = s.strip().split(' ')
        if len(s)==0:
            pass
        if i_face == 0:
            shape = s[0]
        # for x in range(1, 4):
        #     faces.append(int(s[x]))
        try:
            faces.append([int(s[x]) for x in range(1, 4)])
        except IndexError as error:
            print(i_face+len(verts))
    # finalVerts = []
    # for i in range(len(faces)):
    #     finalVerts.append(verts[faces[i]])
    # print(finalVerts)
    return shape, verts, faces


def meshFromArray(file):
    shape, vertices, faces = read_off(file)
    glEnableClientState(GL_VERTEX_ARRAY)
    #glEnableClientState(GL_NORMAL_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, vertices)
    #glNormalPointer(GL_FLOAT, len(faces), triangularMeshNormals(vertices, faces))
    glDrawElements(GL_TRIANGLES, len(faces), GL_UNSIGNED_INT, faces)
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_NORMAL_ARRAY)


def mesh_reconstructor(file):
    shape, verticies, faces = read_off(file)
    #
    # glBegin(GL_LINES)
    # for face in faces:
    #     glColor3f(0.8, 0.8, 0.8)
    #     glVertex3fv(verticies[face[0]])
    #     glVertex3fv(verticies[face[1]])
    #     glVertex3fv(verticies[face[0]])
    #     glVertex3fv(verticies[face[2]])
    #     glVertex3fv(verticies[face[1]])
    #     glVertex3fv(verticies[face[2]])
    # glEnd()

    glBegin(GL_TRIANGLES)
    for face in faces:
        for vertex in face:
            v = verticies[vertex]
            glNormal3fv(triangleNormal(verticies, face))
            glVertex3fv(v)
    glEnd()


def triangularMeshNormals(vertices, faces):
    normals = []
    for i in range(len(faces)):
        if i%3 == 0:
            faceNormal = triangleNormal(vertices, (faces[i], faces[i+1], faces[i+2]))
            normals.append([faceNormal]*3)
    return normals

def triangleNormal(vertices, face):
    ux = vertices[face[1]][0] - vertices[face[0]][0]
    uy = vertices[face[1]][1] - vertices[face[0]][1]
    uz = vertices[face[1]][2] - vertices[face[0]][2]
    vx = vertices[face[2]][0] - vertices[face[0]][0]
    vy = vertices[face[2]][1] - vertices[face[0]][1]
    vz = vertices[face[2]][2] - vertices[face[0]][2]

    x = (uy*vz)-(uz-vy)
    y = (uz*vx)-(ux-vz)
    z = (ux*vy)-(uy-vx)

    xf = x / math.sqrt(pow(x,2) + pow(y, 2) + pow(z, 2))
    yf = y / math.sqrt(pow(x,2) + pow(y, 2) + pow(z, 2))
    zf = z / math.sqrt(pow(x, 2) + pow(y, 2) + pow(z, 2))

    return (xf, yf, zf)


def scenemodel():
    glRotate(90, 0., 0., 1.)
    with open(FILE_PATH, "r") as f:
        mesh_reconstructor(f)
        # meshFromArray(f)



# --------
# VIEWER
# --------

def printHelp():
    print(
    """\n\n    
         -------------------------------------------------------------------\n
         Left Mousebutton       - move eye position (+ Shift for third axis)\n
         Middle Mousebutton     - translate the scene\n
         Right Mousebutton      - move up / down to zoom in / out\n
          Key                - reset viewpoint\n
          Key                - exit the program\n
         -------------------------------------------------------------------\n
         \n"""
    )

def init():
    glLoadIdentity()
    # glEnable(GL_DEPTH_TEST)
    # glEnable(GL_NORMALIZE)
    # glShadeModel(GL_FLAT)
    #
    # glEnable(GL_LIGHTING)
    # glEnable(GL_LIGHT0)
    #
    # glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE);
    glEnable(GL_COLOR_MATERIAL)
    glColor3f(0, 0, 0)

    resetView()


def resetView():
    global zoom, xRotate, yRotate, zRotate, xTrans, yTrans
    zoom = 65.
    xRotate = 0.
    yRotate = 0.
    zRotate = 0.
    xTrans = 0.
    yTrans = 0.
    glutPostRedisplay()


def display():
    # Clear frame buffer and depth buffer
    glClearColor(1, 1, 1, 1);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # Set up viewing transformation, looking down -Z axis
    glLoadIdentity()
    gluLookAt(0, 0, -g_fViewDistance, 0, 0, 0, -.1, 0, 0)  # -.1,0,0
    # Set perspective (also zoom)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(zoom, float(g_Width) / float(g_Height), g_nearPlane, g_farPlane)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glMatrixMode(GL_MODELVIEW)
    # Render the scene
    polarView()
    scenemodel()
    drawAxis()
    drawEigen()
    # Make sure changes appear onscreen
    glutSwapBuffers()


def drawAxis():

    glBegin(GL_LINES)
    # draw line for x axis
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(1.0, 0.0, 0.0)
    # draw line for y axis
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 1.0, 0.0)
    # drawline for Z axis
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 1.0)
    glEnd()
    # load the previous matrix


eigenVectors = []
def drawEigen():

    c = [0.0, 0.0, 0.0]
    glBegin(GL_LINES)
    for i in range(len(eigenVectors)):
        c[i] = 1.0
        glColor3fv(c)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3fv(eigenVectors[i])
    glEnd()


def reshape(width, height):
    global g_Width, g_Height
    g_Width = width
    g_Height = height
    glViewport(0, 0, g_Width, g_Height)


def polarView():
    glTranslatef(yTrans / 100., 0.0, 0.0)
    glTranslatef(0.0, -xTrans / 100., 0.0)
    glRotatef(-zRotate, 0.0, 0.0, 1.0)
    glRotatef(-xRotate, 1.0, 0.0, 0.0)
    glRotatef(-yRotate, .0, 1.0, 0.0)


def keyboard(key, x, y):
    global zTr, yTr, xTr
    if (key == b'r'): resetView()
    if (key == b'q'): sys.exit(0)
    glutPostRedisplay()


def mouse(button, state, x, y):
    global action, xStart, yStart
    if (button == GLUT_LEFT_BUTTON):
        if (glutGetModifiers() == GLUT_ACTIVE_SHIFT):
            action = "MOVE_EYE_2"
        else:
            action = "MOVE_EYE"
    elif (button == GLUT_MIDDLE_BUTTON):
        action = "TRANS"
    elif (button == GLUT_RIGHT_BUTTON):
        action = "ZOOM"
    xStart = x
    yStart = y


def motion(x, y):
    global zoom, xStart, yStart, xRotate, yRotate, zRotate, xTrans, yTrans
    if (action == "MOVE_EYE"):
        xRotate += x - xStart
        yRotate -= y - yStart
    elif (action == "MOVE_EYE_2"):
        zRotate += y - yStart
    elif (action == "TRANS"):
        xTrans += x - xStart
        yTrans += y - yStart
    elif (action == "ZOOM"):
        zoom -= y - yStart
        if zoom > 150.:
            zoom = 150.
        elif zoom < 1.1:
            zoom = 1.1
    else:
        print("unknown action\n", action)
    xStart = x
    yStart = y
    glutPostRedisplay()


# ------
# MAIN
# ------
def meshRenderer (filepath, eigenV):
    # GLUT Window Initialization
    global FILE_PATH
    FILE_PATH = filepath
    global eigenVectors
    eigenVectors = eigenV
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # zBuffer
    glutInitWindowSize(g_Width, g_Height)
    glutInitWindowPosition(0 + 4, int(g_Height / 4))
    glutCreateWindow("Visualizzatore_2.0")
    # Initialize OpenGL graphics state
    init()
    # Register callbacks
    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutKeyboardFunc(keyboard)
    printHelp()
    # Turn the flow of control over to GLUT
    glutMainLoop()




def getPositionDimensions(vertices):
    maxx, maxy, maxz = 0, 0, 0
    minx, miny, minz = sys.maxsize
    sumx, sumy, sumz = 0, 0, 0

    for vertex in vertices:
        if vertex[0] < minx: minx = vertex[0]
        if vertex[0] < miny: miny = vertex[1]
        if vertex[0] < minz: minz = vertex[2]
        if vertex[0] > maxx: maxx = vertex[0]
        if vertex[0] > maxy: maxy = vertex[1]
        if vertex[0] > maxz: maxz = vertex[2]

        sumx += vertex[0]
        sumy += vertex[1]
        sumz += vertex[2]
    sumx /= len(vertices)
    sumy /= len(vertices)
    sumz /= len(vertices)

    return ([minx, miny, minz], [maxx, maxy, maxz], [sumx, sumy, sumz])

def moveMeshToCenter(vertices, delta):
    for i in range(len(vertices)):
        for j in range(3):
            vertices[i][j] -= delta[j]
    return vertices

