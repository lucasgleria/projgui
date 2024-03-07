# import PySimpleGUIQt as sg

# sg.theme('DarkBlue')
# sg.set_options(font=('Courier New', 20))

# layout = [
#     [
#         sg.Text('Select'),
#         sg.Combo(['one', 'two'], tooltip="choose something", ),
#     ]
# ]

# sg.Window("hello!", layout, icon='Drop-box-e-icone/guanixim.jpg').read(close=True)


# After Pyinstaller, an exe file generated and got my icon 'D:/job.ico' on taskbar. The same if I run it in file explorer or console CMD.

# pyinstaller --onefile --noconsole my_script.py

import PySimpleGUIQt as sg
import sys

# This bit gets the taskbar icon working properly in Windows
if sys.platform.startswith('win'):
    import ctypes
    # Make sure Pyinstaller icons are still grouped
    if sys.argv[0].endswith('.exe') == False:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'CompanyName.ProductName.SubProduct.VersionInformation') # Arbitrary string

layout = [
    [sg.Text('Test text that\'s just long enough for a decent width window')],
]

window = sg.Window('Title', layout, icon='Drop-box-E-icone\guanixim.jpg', resizable=False, finalize=True)

while True:
    event, values = window.read()

    if event in (sg.WIN_CLOSED, 'Exit'):
        break