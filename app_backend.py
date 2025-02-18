import cv2
import pytesseract
from PIL import Image
from os import listdir
from os.path import isfile, join
import os
import pandas as pd

import image_utilities

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def get_all_file_names(dir_path):
    only_files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    return only_files


def crop_and_get_php_value(file_path):

    img = image_utilities.crop_php(file_path)

    text = pytesseract.image_to_string(img)

    php_value = get_php_value(text)

    return php_value

def get_php_value(text, file_path=None):

    #Works for most images
    for line in [line.lower() for line in text.split('\n')]:
        if 'php' in line:
            # print(line)
            try:
                clean_line = line.split("php")[1].replace(',','')

                php_value = int(float(clean_line))

                return php_value
            except:
                a=1 #Do nothing
                # print("ups")

    #For text messages
    # for line in [line.lower() for line in text.split('\n')]:
    #     if 'you have paid p' in line:
    #         # print(line)
    #         try:
    #             clean_line = line.split("you have paid p")[1].split(" ")[0]
    #             # print(clean_line)
    #             php_value = int(float(clean_line))
    #             return php_value
    #         except:
    #             a=1 #Do nothing
    #             print("ups2")
    #For the images with PHP in red

    if file_path is not None:
        return crop_and_get_php_value(file_path)
    else:
        return False

def get_first_13_digits_number(text):
    for line in text.split('\n'):
        #Take first element of line
        first_line_element = line.split(' ')[0]
        if len(first_line_element)==13:
            #If its indeed a number
            if(int(first_line_element)):
                return first_line_element

def get_ref_n(text):
    for line in text.split('\n'):
        if 'Ref. No' in line:
            #Remove 'ref. no. ' from string
            ref_n = line.split('Ref. No')[1].replace('.','').replace(',','').replace(':','').replace(' ','').replace('O','0')

            #Someimes the number comes in following lines
            if(ref_n == ''):
                #Look for next line with 13 digits
                ref_n = get_first_13_digits_number(text)

            return ref_n

    #For receipts with blue background
    for line in text.split('\n'):
        if 'GCash Ref Number' in line:
            ref_n = line.split('GCash Ref Number')[1].replace(':','').replace(' ','').replace('O','0')
            return ref_n

    #For receipts with green check on top
    for line in text.split('\n'):
        if 'Recipient' in line:
            ref_n = line.split('Recipient')[1].replace('O','0')
            if(ref_n!=""):
                return ref_n

    #For receipts with number in top
    for line in text.split('\n'):
        if 'Sent money to ' in line:
            ref_n = line.split('Sent money to ')[1].replace('O','0')
            return ref_n

    #Some come with a 'Recipient\niS number' message
    for line in text.split('\n'):
        if 'iS' in line:
            ref_n = line.split('iS ')[1].replace('O','0')
            return ref_n

    #If no Ref No found
    return False



def process_image(dir_path, file_name):
    file_path = join(dir_path, file_name)
    img = Image.open(file_path)


    text = pytesseract.image_to_string(img)

    php_value = get_php_value(text, file_path)
    ref_n = get_ref_n(text)


    file_name_has_ref_n = ref_n and ref_n in file_name


    if(php_value):
        # print([file_name, php_value, ref_n, file_name_has_ref_n])
        return [file_name, php_value, ref_n, file_name_has_ref_n]
    else:
        return False

def save_df(results, files_not_processed, output_path):

    results_df = pd.DataFrame()
    results_df = results_df.append(results)
    results_df.columns=['File_name', 'PHP Value', 'Ref. No.', 'File name matches ref n']
    results_df.to_csv(join(output_path,'results.csv'), index=False)

    if len(files_not_processed)>0:

        files_not_processed_df = pd.DataFrame()
        files_not_processed_df = files_not_processed_df.append(files_not_processed)
        files_not_processed_df.columns=['File_name']
        files_not_processed_df.to_csv(join(output_path,'files_not_processed.csv'), index=False)


if __name__ == '__main__':

    from tkinter.filedialog import askdirectory

    dir_path = askdirectory()

    files_names = get_all_file_names(dir_path)

    results = []
    files_not_processed = []

    for index, file_name in enumerate(files_names):
        print(f'{index+1}/{len(files_names)}')
        image_processing_result = process_image(dir_path, file_name)
        # image_number_display.pack_forget()

        if image_processing_result:
            results.append(image_processing_result)
        else:
            files_not_processed.append(file_name)

    #Save results
    save_df(results, files_not_processed)
