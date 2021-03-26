import PySimpleGUI as sg
import Scanner as scn

def gui_start():
    layout = [
        [sg.Text("Document to Rename")],
        [sg.In(key="_FILES_"), sg.FilesBrowse(file_types=(("PDF Files", "*.pdf"),))],
        [sg.Button("OK")]
    ]

    # Create the window
    window = sg.Window("Scan BR Rename Tool", layout)

    # Create an event loop
    while True:
        event, values = window.read()

        # End program if user closes window or
        # presses the OK button
        if event == "OK":
            f_name = values["_FILES_"]
            if not f_name:
                sg.popup("No file selected")
            else:
                # print("Loop through files: ", values["_FILES_"])
                f_name_split = values["_FILES_"].split(";")

                for i in f_name_split:
                    # print(i)
                    scn.getFileName(i)

                sg.popup("Renaming Completed", title="Rename Status")
        elif event == sg.WIN_CLOSED:
            break
    window.close()