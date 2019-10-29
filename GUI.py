import PySimpleGUI as sg

sg.ChangeLookAndFeel('GreenTan')
layout = [
         [sg.Text('Search Shape', size=(15, 1)), sg.InputText(), sg.FileBrowse()],
            [sg.Text('Select from list of Shapes', size=(15, 1)),sg.Combo(values=[], key='_OUTPUT_', size=(15, 1))],
            [sg.Open(), sg.Cancel()]
]

layout2 = [
            [sg.Text('List of similar shapes', size=(15, 10)),sg.Listbox(values=[], key='list', size=(15, 10),select_mode='LISTBOX_SELECT_MODE_EXTENDED')],
            [sg.Open(), sg.Cancel()]
]

window = sg.Window('Content-based Shape Retrieval System', layout).finalize()
#query to get list of shapes
test=['dassa','asd','ada']
window.FindElement('_OUTPUT_').Update(values=test)

#query to get list of retrieved shapes
test2=['asda','ada','sda']


event, values = window.Read()
while True:
    event, values = window.Read()
    if event in (None, 'Open'):
        #Query
        window2 = sg.Window('Similar Shapes', layout2).finalize()
        window2.FindElement('list').Update(values=test2)
        event, values = window2.Read()
        #return list
    break

