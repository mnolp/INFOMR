from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import array
import plyfile

# -----------
# VARIABLES
# -----------

g_fViewDistance = 9.
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
        if i_face == 0:
            shape = s[0]
        # for x in range(1, 4):
        #     faces.append(int(s[x]))
        faces.append([int(s[x]) for x in range(1, 4)])
    # finalVerts = []
    # for i in range(len(faces)):
    #     finalVerts.append(verts[faces[i]])
    # print(finalVerts)
    return shape, verts, faces


def meshFromArray(file):
    shape, vertexes, faces = read_off(file)
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, vertexes)
    glDrawElements(GL_TRIANGLES, len(faces), GL_UNSIGNED_INT, faces)
    glDisableClientState(GL_VERTEX_ARRAY)


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
        x = 0
        for vertex in face:
            x += 1
            glNormal3fv(triangleNormal(verticies, face))
            glVertex3fv(verticies[vertex])
    glEnd()

def triangleNormal(vertexes, triangle):
    ux = vertexes[triangle[1]][0] - vertexes[triangle[0]][0]
    uy = vertexes[triangle[1]][1] - vertexes[triangle[0]][1]
    uz = vertexes[triangle[1]][2] - vertexes[triangle[0]][2]
    vx = vertexes[triangle[2]][0] - vertexes[triangle[0]][0]
    vy = vertexes[triangle[2]][1] - vertexes[triangle[0]][1]
    vz = vertexes[triangle[2]][2] - vertexes[triangle[0]][2]

    x = (uy*vz)-(uz-vy)
    y = (uz*vx)-(ux-vz)
    z = (ux*vy)-(uy-vx)

    xf = x / (abs(x) + abs(y) + abs(z))
    yf = y / (abs(x) + abs(y) + abs(z))
    zf = z / (abs(x) + abs(y) + abs(z))

    return (xf, yf, zf)


def scenemodel():
    glRotate(90, 0., 0., 1.)
    with open("dataset/Teddy/164.off", "r") as f:
        # mesh_reconstructor(f)
        meshFromArray(f)


# ---------
# PlyLoader
# ---------

def plyLoader(file):
    with open(file) as f:
        plydata = plyfile.PlyData.read(f)

    return plydata

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
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    glShadeModel(GL_FLAT);
    light = (1, 1, 1, 0);
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, light)
    glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE);
    glEnable(GL_COLOR_MATERIAL)
    glColor3f(0.8, 0.8, 0.8);

    glEnable(GL_DEPTH_TEST);
    glEnable(GL_NORMALIZE);
    # glLightfv(GL_LIGHT0, GL_POSITION, [.0, 10.0, 10., 0.])
    # glLightfv(GL_LIGHT0, GL_AMBIENT, [.0, .0, .0, 1.0]);
    # glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0]);
    # glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0]);
    glShadeModel(GL_SMOOTH);
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
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # Set up viewing transformation, looking down -Z axis
    glLoadIdentity()
    gluLookAt(0, 0, -g_fViewDistance, 0, 0, 0, -.1, 0, 0)  # -.1,0,0
    # Set perspective (also zoom)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(zoom, float(g_Width) / float(g_Height), g_nearPlane, g_farPlane)
    glMatrixMode(GL_MODELVIEW)
    # Render the scene
    polarView()
    scenemodel()
    # Make sure changes appear onscreen
    glutSwapBuffers()


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
    if (key == 'r'): resetView()
    if (key == 'q'): exit(0)
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
def meshRenderer ():
    # GLUT Window Initialization
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