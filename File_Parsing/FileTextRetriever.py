import os
import docx

from File_Parsing.ImageParser import get_img_text
from striprtf.striprtf import rtf_to_text
from File_Parsing.PdfReader import get_pdf_text

def get_text(file_path):
    _, file_extension = os.path.splitext(file_path)
    match file_extension:
        case '.docx':
            return get_docx(file_path)
        case '.rtf':
            return get_rtf(file_path)
        case '.bmp' | '.jfif' | '.jpg' | '.jpeg' | '.png' | '.tif' |'.tiff':
            return get_img_text(file_path)
        case '.pdf':
            body, footers = get_pdf_text(file_path)
            return body, footers
        case '.txt':
            with open(file_path, 'r') as file:
                return file.read()
    return None

def get_docx(file_path):
    return '\n'.join([p.text for p in docx.Document(file_path).paragraphs])

def get_rtf(file_path):
    with open(file_path) as file:
        content = file.read()
        return rtf_to_text(content)
    