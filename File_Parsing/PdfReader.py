import os
import pdfplumber
import fitz
import shutil
import pytesseract
import re

from collections import Counter
from pdf2image import convert_from_path
from File_Parsing.ImageParser import get_img_text

def get_text_by_mcid(page):
    mcid_dict = { }

    for char in page.chars:
        mcid_dict[char['mcid']] = mcid_dict.setdefault(char['mcid'], "") + char['text']

    mcid_dict = {key: value for key, value in mcid_dict.items() if len(value.strip()) > 0}

    return list(mcid_dict.values())

def get_text_by_coords(page, paragraphs):
    footers = ""

    body_char_mode, line_height_mode, left_rule = get_page_dimensional_info(page)

    # Paragraph breaks usually take the form of 1.5 a line,
    # but *1.4 leaves room for tolerance due to font changes
    para_break_height = line_height_mode * 1.4

    footer_bbox = get_footers_bounds(page, body_char_mode)
    if footer_bbox != None:
        footer_chars = page.crop(footer_bbox).chars
        footers += "".join(f"{char['text']}" for char in footer_chars) + '\n'

        body_chars = page.outside_bbox(footer_bbox).chars
    else:
        body_chars = page.chars

    prev_char = body_chars[0]
    start_index = 0
    para_indexes = [ ]
    # Split strings by paragraph
    for i, char in enumerate(body_chars):
        # Allow .2 tolerance for bold fonts, else .1
        tolerance = .2 if re.search("bold", char['fontname'].lower()) != None else .1 
        line_height = prev_char['y0'] - char['y0'] + tolerance
        if  line_height > para_break_height: 
            para_indexes.append((start_index, i - 1))
            start_index = i
        # skip whitespace characters since some pdfs use them, while others just change coords on page
        prev_char = prev_char if char['text'].isspace() else char

    # Filter chars by size to remove artifacts (and superscripts)
    for i, (start, end) in enumerate(para_indexes):
        # Need to allow small size tolerance because PDFs are great
        text = "".join(f"{['', char['text']][char['size'] >= body_char_mode - .1]}"
                        for char in body_chars[start:end]).strip()
        
        # Remove page number
        end = 0
        regex = re.compile("^\d+ ")
        if regex.match("".join(text[0:4])):
            end = [m.end(0) for m in re.finditer(regex, text[0:4])][0]
            text = text[end:]
        
        if len(text) > 0:
            # Join paragraphs continued between pages
            is_left_rule_aligned = abs(body_chars[end]['x0'] - left_rule) < 0.1 # Allow .1 tolerance
            if (len(paragraphs) > 0) & (i == 0) & is_left_rule_aligned:
                paragraphs[-1] = paragraphs[-1] + ' ' + text
            else:
                paragraphs.append(text)

    return paragraphs

def get_unique_paragraphs(paragraphs):
    unique_paragraphs = []

    # MCID method often picks up footers
    # #so attempt to strip random space differences and numbers to identify them as non-uniuq
    stripped = [''.join([i for i in item if not i.isdigit() or i.isspace()]) for item in paragraphs]

    for i, val in enumerate(paragraphs):
        if stripped.count(val) == 1:
            unique_paragraphs.append(paragraphs[i])

    return unique_paragraphs

def get_greater_mode(data):
    '''
    If the second most common element of the data is of greater value than the most common, returns the second most
    common element; ELSE returns the most common element.

    data: a list of integer elements to find the mode of.
    '''
    counter = Counter(data)
    mode1 = max(data, key = counter.get)
    mode2 = -1
    
    data1 = list(filter(lambda elem: elem != mode1, data))
    if (len(data1) > 0):
        counter = Counter(data)
        mode2 = max(data1, key = counter.get)

    return max(mode1, mode2)

def get_page_dimensional_info(page):
    char_heights = []
    line_heights = []
    prev_char_y = 1000
    left_rule = 1000

    for char in page.chars:
        left_rule = min(left_rule, char['x0'])
        # Skip whitespace and bolds to exclude heading text.
        isWhitespace = char['text'] == ' '
        isBold = re.search("bold", char['fontname'].lower()) != None
        if isWhitespace or isBold: continue
            
        char_heights.append(char['height'])
        if (prev_char_y - char['y0'] - .1) > 0:
            line_heights.append(prev_char_y - char['y0'])
        prev_char_y = char['y0']

    char_height_mode = get_greater_mode(char_heights)
    line_height_mode = get_greater_mode(line_heights)

    return char_height_mode, line_height_mode, left_rule

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
    paragraphs = [ ]
    body = ""
    footers = ""
    with pdfplumber.open(file_path) as pdf:
        # If no characters found, try OCR
        if len(pdf.chars) == 0 & try_ocr:
            body = get_pdf_text_ocr(file_path)
            return body, footers

        for page in pdf.pages:
            chars = page.chars
            if any(char['mcid'] != None for char in chars):
                paragraphs.extend(get_text_by_mcid(page))
            else:
                paragraphs = get_text_by_coords(page, paragraphs)

        # Remove all duplicates since those are almost certainly heading/footing
        unique_paragraphs = get_unique_paragraphs(paragraphs)
        unique_footers = get_unique_paragraphs(footers)

    return unique_paragraphs, unique_footers

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