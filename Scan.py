from pdf2image import convert_from_path
import PyPDF2
import pytesseract
from pytesseract import Output
import re
import numpy as numpy
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