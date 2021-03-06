from pdf2image import convert_from_path
import PyPDF2
import pytesseract
from pytesseract import Output
import re
import numpy as np
import cv2
import pandas as pd
import os
import getpass
from datetime import datetime

# poppler_location = "...\poppler-0.68.0\bin"
poppler_location = r""
# tess_location = r"...\AppData\Local\Tesseract-OCR\\tesseract.exe"
tess_location = r"C:\Users\\" + getpass.getuser() + r"\AppData\Local\Tesseract-OCR\\tesseract.exe"


def get_dir(doc_name):
    """
	Gets the document name from the directory
	:param doc_name: the document name e.g. abc.pdf
	:return: full path of the document
	"""
    dir_str = os.path.dirname(doc_name)
    return dir_str


def listToString(input_list):
    """
	Converts the input from a list to string
	:param input_list: list
	:return: string
	"""
    final_str = ''.join(input_list)
    return final_str


def getImageOrientation(img_obj):
    """
	Gets the orientation of the image in degrees
	:param img_obj: opencv object
	:return: degree of rotation
	"""
    osd = pytesseract.image_to_osd(img_obj)
    return re.search('(?<=Rotate: )\d+', osd).group(0)


def rotateImage(image_to_rotate):
    """
	Rotates the image to the upright position based on the text orientation
	:param image_to_rotate: opencv image
	:return: rotated opencv image
	"""
    angle_to_rotate = getImageOrientation(image_to_rotate)

    if angle_to_rotate == 90:
        return cv2.rotate(image_to_rotate, cv2.ROTATE_90_CLOCKWISE)

    elif angle_to_rotate == 180:
        return cv2.rotate(image_to_rotate, cv2.ROTATE_180)

    elif angle_to_rotate == 270:
        return cv2.rotate(image_to_rotate, cv2.ROTATE_90_COUNTERCLOCKWISE)

    else:
        return image_to_rotate


def getImage(document_name, page_number):
    """
	Converts the PDF file and returns a opencv image file
	:param document_name: document name e.g. abc.pdf
	:param page_number: the page number of the document to be scanned
	:return:
	"""
    # Converts the PDF file and returns a cv2 image file

    # Convert PIL to cv2 and grayscale
    image_test = convert_from_path(document_name, poppler_path=poppler_location,
                                   first_page=page_number, last_page=page_number)
    img = cv2.cvtColor(np.array(image_test[0]), cv2.COLOR_BGR2GRAY)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)  # Scale to a larger image

    # Apply Dilation and Erosion
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    img = cv2.medianBlur(img, 3)  # Blurring
    img = np.uint8(np.abs(img))
    ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return img


def getFileName(doc_name):
    """
	Looks through all the pages and gets the number that matches the regex pattern
	:param doc_name: document name e.g. abc.pdf
	:return:
	"""
    print("Script Start")
    start_time = datetime.now()

    # Regex Patterns
    # Fill in as required
    matcode_pattern = ""
    batchnum_pattern = ""
    erp_pattern = ""

    try:
        df_list = []
        pdf = PyPDF2.PdfFileReader(doc_name)
        pdf_totalpages = pdf.getNumPages()

        for x in range(1, pdf_totalpages + 1):
            page_list = []
            print("Page Number: {} / {}".format(x, pdf_totalpages))

            img = getImage(doc_name, x)
            img = rotateImage(img)
            d = pytesseract.image_to_data(img, output_type=Output.DICT)
            keys = list(d.keys())

            n_boxes = len(d['text'])
            for i in range(n_boxes):

                if re.fullmatch(matcode_pattern, d['text'][i]):
                    # For debugging purposes
                    # print("\n", str(re.findall(matcode_pattern, d['text'][i])))
                    page_list.insert(0, listToString(re.findall(matcode_pattern, d['text'][i])))

                if re.fullmatch(batchnum_pattern, d['text'][i]):
                    # For debugging purposes
                    # print("\n", str(re.findall(batchnum_pattern, d['text'][i])))
                    page_list.insert(0, listToString(re.findall(batchnum_pattern, d['text'][i])))

                if re.fullmatch(erp_pattern, d['text'][i]):
                    # For debugging purposes
                    # print("\n", str(re.findall(erp_pattern, d['text'][i])))
                    page_list.insert(0, listToString(re.findall(erp_pattern, d['text'][i])))

                if int(d['conf'][i]) > 60:
                    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                    img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            df_list.append(page_list)
            if len(page_list) == 3:
                break

        # Test to show the image (For debugging purposes
        # cv2.imshow('img', img)
        # cv2.waitKey(0)

        df = pd.DataFrame(df_list, columns=['Document_ID'])
        df.drop_duplicates(inplace=True)
        df.dropna(inplace=True, axis=0)

        # Generate the final file name
        final_file_name = df.iloc[0, 0] + "_" + df.iloc[0, 1] + "_" + df.iloc[0, 2] + ".pdf"

        # Rename the pdf file
        final_name = str(os.path.dirname(doc_name)) + r'/' + final_file_name
        print("Final File Name: ", final_name)
        print(" /\_/\\")
        print(r"( o.o )  File Renamed!")
        print(r" > ^ <")
        os.rename(doc_name, final_name)

    except:
        pass

    print("Total Time Taken: ", datetime.now() - start_time)
