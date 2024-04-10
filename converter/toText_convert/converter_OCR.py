import tempfile
import pytesseract


def image_to_text(img, user) -> str:
    img_temp_f = tempfile.NamedTemporaryFile()
    img_temp_f.write(img.read())
    text_result = pytesseract.image_to_string(img_temp_f.name)

    return text_result