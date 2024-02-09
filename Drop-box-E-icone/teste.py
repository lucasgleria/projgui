import PySimpleGUIQt as sg

sg.theme('DarkBlue')
sg.set_options(font=('Courier New', 20))

layout = [
    [
        sg.Text('Select'),
        sg.Combo(['one', 'two'], tooltip="choose something", ),
    ]
]

sg.Window("hello!", layout, icon='transparente2.png').read(close=True)


# After Pyinstaller, an exe file generated and got my icon 'D:/job.ico' on taskbar. The same if I run it in file explorer or console CMD.

# pyinstaller --onefile --noconsole my_script.py