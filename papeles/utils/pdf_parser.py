from io import BytesIO, StringIO
from typing import Iterable

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import requests


def get_document(path: str, local=True):
    """
    Loads document from path and returns an BytesIO object
    """
    if local:
        return open(path, 'rb')
    file_r = requests.get(path)
    return BytesIO(file_r.content)


def get_text(pdf_path: str, local: bool) -> Iterable[str]:
    """
    Given a pdf file path, returns an Iterable[str] where each string is a line in the pdf file.
    """
    fp = get_document(pdf_path, local)
    document = PDFDocument(PDFParser(fp))
    if not document.is_extractable:
        return []
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec='utf-8', laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        text = retstr.getvalue()
        yield [x for x in text.splitlines() if x and '\x00' not in x]
        retstr.truncate(0)
