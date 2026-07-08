import fitz


def extract_cv(filename):
    file = fitz.open(filename.path)
    ret_text = ""

    for page in file:
        text = page.get_text().strip()
        ret_text += text
        print(text)

    return ret_text

