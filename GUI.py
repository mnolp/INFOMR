import PySimpleGUI as sg
import database_classes as db
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
            #Query
            id1 = db.session.query(db.Distance)\
                              .join(db.Distance.mesh1)\
                              .filter(db.Mesh.filename==values['_OUTPUT_'])\
                              .first()
            test2 = db.session.query(db.Distance)\
                              .filter(db.Distance.mesh1_id==id1.mesh1_id)\
                              .join(db.Distance.mesh2)\
                              .add_column(db.Mesh.filename)\
                              .add_column(db.Distance.value)\
                              .order_by(db.Distance.value)\
                              .all()

            test2 = [test2[i].filename for i in range(20)]
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
                elif event in (None, 'Cancel'):
                    window2.close()
                    break
        elif event in (None, 'Cancel'):
            #return list
            break


if __name__ == "__main__":
    main()

