import fitz


def extract_cv(filename):
    file = fitz.open(filename)

    for page in file:
        text = page.get_text().strip()
        print(text)

