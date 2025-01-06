import PyPDF2

def pdf_to_text(pdf_path, output_txt_path = None):
    '''
    Inputs
        pdf_path: file path of the PDF to be read
        output_txt_path: File path of the txt output file if you would like one. If left blank, no file will be saved.

    Returns:
        A string containing the text from the PDF
    '''
    # Open the PDF file in read-binary mode
    with open(pdf_path, 'rb') as pdf_file:
        # Create a PdfReader object instead of PdfFileReader
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Initialize an empty string to store the text
        text = ''

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()

    # Write the extracted text to a text file
    if output_txt_path != None:
        with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text)

    return text

def standardizeWhitespace(text):
    '''
    Takes a string and ensures all whitespace around punctuation is consistent.
    Returns string with more normal whitespace
    '''
    pass

if __name__ == "__main__":
    pdf_path = './Text Splitter/TestComments/NissanResponse.pdf'


    long_text = pdf_to_text(pdf_path)

    print(long_text)
