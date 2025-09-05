import os
import pdfplumber
import fitz
import shutil
import pytesseract

from collections import Counter
from pdf2image import convert_from_path
from File_Parsing.ImageParser import get_img_text

def get_body_char_height(page):
    char_heights = []
    for char in page.chars:
        char_heights.append(char['height'])

    data = Counter(char_heights)
    return max(char_heights, key=data.get)

def get_footers_bounds(page, body_char_height):
    first_char = page.chars[0]
    last_char = page.chars[0]
    first_found = False

    for char in page.chars:
    # Read lines until find one with lesser height
        if char['height'] < body_char_height:
            # Keep reading until finding last consecutive line of lesser height
            if first_found:
                last_char = char
            # We found our first line
            else:
                first_char = char
                first_found = True
        # If it isn't consecutive we're not at the footers (maybe figure text), so restart.
        else:
            first_found = False
    # We found no footers
    if first_found == False:
        return None
    # Return a bounding box of the footer
    else:
        bbox = [ first_char['x0'], first_char['top'], last_char['x1'], last_char['bottom'] ]
        return bbox

def remove_images(input_pdf, output_pdf):
    '''
    input_pdf: The complete path to a PDF file to preprocess for text extraction.
    output_pdf: The complete path to output location of the preprocessed PDF.

    remarks: Preprocessing removes images from the PDF file.
    '''
    doc = fitz.open(input_pdf)
    for page in doc:
        img_list = page.get_images()
        for img in img_list:
            page.delete_image(img[0])

    doc.save(output_pdf)
    doc.close()

def get_pdf_text(file_path, try_ocr = True):
    '''
    file_path: Path to a PDF file from which to extract text.
    try_ocr: If True and no characters are found in the PDF file, text will tried to be read using OCR.

    returns: 
        -body: A string representation of the body text of a PDF, including section headers.
        -footers: A string representation of the footnotes of a PDF.

    remarks: If OCR is used all text will be returned in 'body'.
    '''
    body = ""
    footers = ""
    with pdfplumber.open(file_path) as pdf:
        # If no characters found, try OCR
        if len(pdf.chars) == 0 & try_ocr:
            body = get_pdf_text_ocr(file_path)
            return body, footers
        
        # Get body-text line height
        body_char_height = get_body_char_height(pdf.pages[0])

        for page in pdf.pages:
            footer_bbox = get_footers_bounds(page, body_char_height)
            if footer_bbox != None:
                footer_chars = page.crop(footer_bbox).chars
                text = "".join(f"{char['text']}" for char in footer_chars)
                footers += text + '\n'

                body_chars = page.outside_bbox(footer_bbox).chars
                text = "".join(f"{char['text']}" for char in body_chars)
                body += text + '\n'
            else:
                text = "".join(f"{char['text']}" for char in page.chars)
                body += text

    return body, footers

def get_pdf_text_ocr(file_path):
    '''
    file_path: Path to a PDF file from which to extract text.

    returns: A string representation of the text found in a PDF using OCR.

    remarks: User must set the 'tesseract_cmd' variable manually in the function code.
    '''
    # SET VARIABLE TO COMPLETE PATH TO TESSERACT.EXE: 
    pytesseract.pytesseract.tesseract_cmd = 'C:/Users/Vincent.Livant/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'
    
    image_file_names = []
    doc_text = ""
    
    # Create temp directory for conversion
    temp_jpeg_dir = './tempPdf2Jpeg'
    if not os.path.exists(temp_jpeg_dir):
        os.makedirs(temp_jpeg_dir)

    # Get all the pages and convert to jpegs
    pdf_pages = convert_from_path(file_path, 500)
    for page_enumeration, page in enumerate(pdf_pages, start=1):

        filename = f"{temp_jpeg_dir}/page_{page_enumeration:03}.jpg"

        page.save(filename, "JPEG")
        image_file_names.append(filename)

    # Extract text from saved images.
    for file_name in image_file_names:        
        doc_text += get_img_text(file_name)
    
    # delete temp files and directory
    shutil.rmtree(temp_jpeg_dir)

    return doc_text