import PySimpleGUI as sg
import database_classes as db
import Annoy as ann
import trimesh
import pyrender



def render_mesh(filepath):
    filepath = filepath[0][0]
    if filepath[0]!='/': filepath = 'dataset/'+filepath#[:filepath.index('.')]+'_processed.off'
    fuze_trimesh = trimesh.load(filepath)
    mesh = pyrender.Mesh.from_trimesh(fuze_trimesh)
    scene = pyrender.Scene()
    scene.add(mesh)
    pyrender.Viewer(scene, use_raymond_lighting=True)

import Mesh, Mesh2D
import meshTools
from main import add_mesh
def add_mesh_GUI(filepath):
    with open(filepath, "r") as f:
        shape, vertexes, faces = meshTools.read_off(f)
    m = Mesh.Mesh(filepath, vertexes, faces)
    m.setMeshToCenter()
    m.eigen()
    m.changingBase()
    m.setBoundingBox()
    m.normalizeMesh()
    m.flipTest()
    processed_file = m.toFile()
    filepath2D = m.toimage()
    m2D = Mesh2D.Mesh2D(filepath2D)
    add_mesh(filepath, m, m2D)

def main():
    sg.ChangeLookAndFeel('GreenTan')
    layout = [
             [sg.Text('Browse Shape', size=(15, 1)), sg.InputText(size=(30, 1), key='Browsed'), sg.FileBrowse(), sg.Open(key='OpenBrowse')],
                [sg.Text('Or select from list of Shapes', size=(15, 1)),sg.Combo(values=[], key='_OUTPUT_', size=(30, 1)), sg.Open(key='OpenFromList')],
                [sg.Cancel()]
    ]

    window = sg.Window('Content-based Shape Retrieval System', layout).finalize()
    #query to get list of shapes
    test=db.session.query(db.Mesh.filename).filter(~db.Mesh.meshtype_id.in_([3, 6, 11, 18, 20])).order_by(db.Mesh.filename).all()
    window.FindElement('_OUTPUT_').Update(values=test)

    # event, values = window.Read()
    while True:
        event, values = window.Read()
        if event == 'OpenFromList' or event == 'OpenBrowse':
            if event == 'OpenBrowse':
                print(values['Browsed'])
                add_mesh_GUI(values['Browsed'])
                selected_id = db.session.query(db.Mesh.mesh_id).filter(db.Mesh.filename == values['Browsed']).first()
            # Query
            elif event == 'OpenFromList':
                selected_id = db.session.query(db.Mesh.mesh_id).filter(db.Mesh.filename==values['_OUTPUT_']).first()
            t = ann.create_index([3, 6, 11, 18, 20])
            knn = t.get_nns_by_item(selected_id.mesh_id, 20)
            test2 = [db.session.query(db.Mesh.filename).filter(db.Mesh.mesh_id==i).first() for i in knn]

            while True:
                layout2 = [
                    [sg.Text('List of similar shapes', size=(15, 10)),
                     sg.Listbox(values=[], key='list', size=(30, 10), select_mode='LISTBOX_SELECT_MODE_EXTENDED')],
                    [sg.Open(), sg.Cancel()]
                ]
                window2 = sg.Window('Similar to', layout2).finalize()
                window2.FindElement('list').Update(values=test2)
                event, values = window2.Read()
                if event == 'Open':
                    render_mesh(values['list'])
                    window2.close()
                elif event in (None, 'Cancel'):
                    window2.close()
                    break
        elif event in (None, 'Cancel'):
            #return list
            break


if __name__ == "__main__":
    main()

