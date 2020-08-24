import os
from typing import Iterable, Dict, List, Union


from papeles.utils import pdf_parser


def load_folder(folder: str) -> Dict[str, Iterable[List[str]]]:
    """
    Loads data from the folder output using KDD data

    ]
    output/data_<year>/pdfs/<files>

    where
     - <year> is a 4 digits year associated to the year of the Neurips conference.
     - papers_data.json is a metadata file for each paper in this conference
     - <files> are the raw PDF file for this conference

    """
    files = {}
    for file in os.listdir(folder):
        files[file] = pdf_parser.get_text(os.path.join(folder, file), local=True)
    return files
