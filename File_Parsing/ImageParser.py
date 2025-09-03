import pytesseract
from PIL import Image

def get_img_text(file_path):
        img = Image.open(file_path)
        
        page_text = str(((pytesseract.image_to_string(img))))
        
        # Remove end-of-line hyphens
        page_text = page_text.replace("-\n", "")
            
        img.close()

        return page_text