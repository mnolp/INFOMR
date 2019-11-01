import PySimpleGUI as sg
import database_classes as db
import Annoy as ann
# import trimesh
# import pyrender
#
#
#
# def render_mesh(filepath):
#     filepath = 'dataset/'+filepath
#     fuze_trimesh = trimesh.load(filepath)
#     mesh = pyrender.Mesh.from_trimesh(fuze_trimesh)
#     scene = pyrender.Scene()
#     scene.add(mesh)
#     pyrender.Viewer(scene, use_raymond_lighting=True)


def main():
    sg.ChangeLookAndFeel('GreenTan')
    layout = [
             [sg.Text('Search Shape', size=(15, 1)), sg.InputText(), sg.FileBrowse()],
                [sg.Text('Select from list of Shapes', size=(15, 1)),sg.Combo(values=[], key='_OUTPUT_', size=(40, 1))],
                [sg.Open(), sg.Cancel()]
    ]

    window = sg.Window('Content-based Shape Retrieval System', layout).finalize()
    #query to get list of shapes
    test=db.session.query(db.Mesh.filename).order_by(db.Mesh.filename).all()
    window.FindElement('_OUTPUT_').Update(values=test)

    # event, values = window.Read()
    while True:
        event, values = window.Read()
        if event == 'Open':
            # Query
            selected_id = db.session.query(db.Mesh.mesh_id).filter(db.Mesh.filename==values['_OUTPUT_']).first()
            t = ann.load_index()
            knn = t.get_nns_by_item(selected_id.mesh_id, 20)
            test2 = [db.session.query(db.Mesh.filename).filter(db.Mesh.mesh_id==i).first() for i in knn]

            while True:
                layout2 = [
                    [sg.Text('List of similar shapes', size=(15, 10)),
                     sg.Listbox(values=[], key='list', size=(15, 10), select_mode='LISTBOX_SELECT_MODE_EXTENDED')],
                    [sg.Open(), sg.Cancel()]
                ]
                window2 = sg.Window('Similar to '+str(values['_OUTPUT_']), layout2).finalize()
                window2.FindElement('list').Update(values=test2)
                event, values = window2.Read()
                if event == 'Open':
                    pass
                    # render_mesh(values['list'])
                    window2.close()
                elif event in (None, 'Cancel'):
                    window2.close()
                    break
        elif event in (None, 'Cancel'):
            #return list
            break


if __name__ == "__main__":
    main()

