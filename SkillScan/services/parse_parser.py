import fitz


def extract_cv(filename):
    file = fitz.open(filename)

    for page in file:
        text = page.get_text().strip()
        print(text)


extract_cv(r'C:\Users\radic\OneDrive\Desktop\CV - Radica Stojkoska.pdf')