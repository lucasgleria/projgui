import PySimpleGUIQt as sg

layout = [  [sg.Text('Icon Test')],
            [sg.Text(size=(25,1), key='-OUT-')],
            [sg.Button('Go'), sg.Button('Exit')]  ]

sg.Window('Icon Test', layout, icon=r'transparente1.png').read(close=True)