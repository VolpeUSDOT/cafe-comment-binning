import os
import shutil
import pytesseract
import fitz

from pdf2image import convert_from_path
from File_Parsing.ImageParser import get_img_text

def get_pdf(file_path):
    '''
    file_path: Path to a PDF file from which to extract text.

    returns: A string representation of the text of a PDF, excluding images present in the file.

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

    # Pre-process pdf and save to temp directory
    preprocessed_pdf = temp_jpeg_dir + "/cleaned.pdf"
    preprocess_pdf(file_path, preprocessed_pdf)

    # Get all the pages and convert to jpegs
    pdf_pages = convert_from_path(preprocessed_pdf, 500)
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

def preprocess_pdf(input_pdf, output_pdf):
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