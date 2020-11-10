# Imports and Set-up
import sys
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfile, askdirectory
from PIL import ImageTk, Image
import os

import app_backend

app_version = '0.1'
app_title = "Extract text from receipts images - "+app_version
intro_text = ""#[Some instructions here]"

#Set parameters
window_width = 500
window_height = 500
max_screen = False
scrollbar = True

#Global parameters
processing_started = False
df_dict = None

def display_title(title, frame):
    label = ttk.Label(frame, text=title, wraplength=546, justify=tk.LEFT, font=("Calibri", 12, 'bold'), style='my.TLabel')
    label.pack(anchor='nw', padx=(30, 30), pady=(0, 5))
    frame.update()
    return label

def display_message(message, frame):
    label = ttk.Label(frame, text=message, wraplength=546, justify=tk.LEFT, font=("Calibri Italic", 11), style='my.TLabel')
    label.pack(anchor='nw', padx=(30, 30), pady=(0, 5))
    frame.update()
    return label


def save_results(results_dict):
    file_types = [('Excel File', '*.xlsx')]
    saving_path = asksaveasfile(mode='wb', filetypes = file_types, defaultextension=".xlsx")

    result = app_backend.save_dataset(saving_path, results_dict)

    if(result):
        display_message("Saved. Bye!")

def select_output_folder_and_start_process(frame, dir_path):

    #If processing_started, return
    global processing_started
    if(processing_started):
        return

    #Ask user for folder where to save results
    output_path = askdirectory()

    #If no output_path was selected, insist
    while not output_path:
        output_path = askdirectory()

    #Start processing df
    display_message("Your task starting now", frame)
    processing_started = True

    files_names = app_backend.get_all_file_names(dir_path)

    results = []
    files_not_processed = []

    image_number_display = None
    for index, file_name in enumerate(files_names):
        image_number_display = display_message(f'{index+1}/{len(files_names)}', frame)
        image_processing_result = app_backend.process_image(dir_path, file_name)
        image_number_display.pack_forget()

        if image_processing_result:
            results.append(image_processing_result)
        else:
            files_not_processed.append(file_name)

    #Save results
    app_backend.save_df(results, files_not_processed, output_path)
    display_message(f'Task ready! Find results in {output_path}', frame)

def select_input_folder(frame):

    #If processing_started, return
    global processing_started
    if(processing_started):
        return

    #Ask user for input folder with receipts
    dir_path = askdirectory()

    #If no output_path was selected, insist
    while not dir_path:
        dir_path = askdirectory()
    #Else, change folder_imported status so as to disable new imports
    else:
        folder_imported = True


    select_output_button = ttk.Button(frame, text="Select where to save results",
    command=lambda : select_output_folder_and_start_process(frame, dir_path), style='my.TButton')
    select_output_button.pack(anchor='nw', padx=(30, 30), pady=(0, 5))



def window_setup(master):

    global window_width
    global window_height

    #Add window title
    master.title(app_title)

    #Add window icon
    if hasattr(sys, "_MEIPASS"):
        icon_location = os.path.join(sys._MEIPASS, 'app_icon.ico')
    else:
        icon_location = 'app_icon.ico'
    master.iconbitmap(icon_location)

    #Set window position and max size
    if(max_screen):
        window_width, window_height = master.winfo_screenwidth(), master.winfo_screenheight() # master.state('zoomed')?
    master.geometry("%dx%d+0+0" % (window_width, window_height))

    #Make window reziable
    master.resizable(True, True)


def window_style_setup(root):
    root.style = ttk.Style()
    root.style.configure('my.TButton', font=("Calibri", 11, 'bold'), background='white')
    root.style.configure('my.TLabel', background='white')
    root.style.configure('my.TCheckbutton', background='white')
    root.style.configure('my.TMenubutton', background='white')

def create_first_view_frame(main_frame):

    first_view_frame = tk.Frame(master=main_frame, bg="white")
    first_view_frame.pack(anchor='nw', padx=(0, 0), pady=(0, 0))

    #Add intro text
    if intro_text!= "":
        intro_text_label = ttk.Label(first_view_frame, text=intro_text, wraplength=746, justify=tk.LEFT, font=("Calibri", 11), style='my.TLabel')
        intro_text_label.pack(anchor='nw', padx=(30, 30), pady=(0, 12))

    #Labels and buttoms to run app
    start_application_label = ttk.Label(first_view_frame, text="Run application: ", wraplength=546, justify=tk.LEFT, font=("Calibri", 12, 'bold'), style='my.TLabel')
    start_application_label.pack(anchor='nw', padx=(30, 30), pady=(0, 10))

    select_folder_button = ttk.Button(first_view_frame, text="Select Folder with Receipts",
    command=lambda : select_input_folder(first_view_frame), style='my.TButton')
    select_folder_button.pack(anchor='nw', padx=(30, 30), pady=(0, 5))

    return first_view_frame

def add_scrollbar(root, canvas, frame):

    #Configure frame to recognize scrollregion
    def onFrameConfigure(canvas):
        '''Reset the scroll region to encompass the inner frame'''
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))

    def onMouseWheel(canvas, event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    #Bind mousewheel to scrollbar
    frame.bind_all("<MouseWheel>", lambda event, canvas=canvas: onMouseWheel(canvas, event))

    #Create scrollbar
    vsb = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")

if __name__ == '__main__':

    # Create GUI window
    root = tk.Tk()

    window_setup(root)

    window_style_setup(root)

    # Create canvas where app will displayed
    canvas = tk.Canvas(root, width=window_width, height=window_height, bg="white")
    canvas.pack(side="left", fill="both", expand=True)

    # Create frame inside canvas
    main_frame = tk.Frame(canvas, width=window_width, height=window_height, bg="white")
    main_frame.pack(side="left", fill="both", expand=True)

    #This create_window is related to the scrollbar.
    canvas.create_window(0,0, window=main_frame, anchor="nw")

    #Create Scrollbar
    if(scrollbar):
        add_scrollbar(root, canvas, main_frame)

    #Add IPA logo
    if hasattr(tk.sys, "_MEIPASS"):
        logo_location = os.path.join(sys._MEIPASS, 'ipa_logo.jpg')
    else:
        logo_location = 'ipa_logo.jpg'
    logo = ImageTk.PhotoImage(Image.open(logo_location).resize((147, 71), Image.ANTIALIAS))
    tk.Label(main_frame, image=logo, borderwidth=0).pack(anchor="nw", padx=(30, 30), pady=(30, 0))

    #Add app title
    app_title_label = ttk.Label(main_frame, text=app_title, wraplength=536, justify=tk.LEFT, font=("Calibri", 13, 'bold'), style='my.TLabel')
    app_title_label.pack(anchor='nw', padx=(30, 30), pady=(30, 10))

    #Create first view page
    first_view_frame = create_first_view_frame(main_frame)

    # Constantly looping event listener
    root.mainloop()
