import os
import shutil
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import fitz

def get_pdf(file_path):
    pytesseract.pytesseract.tesseract_cmd = 'C:/Users/Vincent.Livant/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'
    image_file_names = []
    doc_text = ""
    
    # Create temp directory for conversion
    temp_jpeg_dir = './tempPdf2Jpeg'
    if not os.path.exists(temp_jpeg_dir):
        os.makedirs(temp_jpeg_dir)

    # Pre-process pdf and save to temp directory
    preprocessed_pdf = temp_jpeg_dir + "/cleaned.pdf"
    remove_images(file_path, preprocessed_pdf)

    # Get all the pages and convert to jpegs
    pdf_pages = convert_from_path(preprocessed_pdf, 500)
    for page_enumeration, page in enumerate(pdf_pages, start=1):

        filename = f"{temp_jpeg_dir}/page_{page_enumeration:03}.jpg"

        page.save(filename, "JPEG")
        image_file_names.append(filename)

    for file_name in image_file_names:
        img = Image.open(file_name)
        
        boxes = pytesseract.image_to_boxes(img)

        page_text = str(((pytesseract.image_to_string(img))))
        
        # Remove end-of-line hyphens
        page_text = page_text.replace("-\n", "")
        
        doc_text += page_text
    
        img.close()

    shutil.rmtree(temp_jpeg_dir)

    return doc_text

def remove_images(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    for page in doc:
        img_list = page.get_images()
        for img in img_list:
            page.delete_image(img[0])

    doc.save(output_pdf)