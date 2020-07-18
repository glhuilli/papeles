import json
import os
from typing import Iterable, Dict, Tuple, Union


from papeles.utils import pdf_parser


def load_folder(folder: str) -> Tuple[Dict[Union[bytes, str], Iterable[str]], dict]:
    """
    Loads data from the folder output using neurips_crawler

    output/data_<year>/papers_data.jsons
    output/data_<year>/pdfs/<files>

    where
     - <year> is a 4 digits year associated to the year of the Neurips conference.
     - papers_data.json is a metadata file for each paper in this conference
     - <files> are the raw PDF file for this conference

    """
    year_data = {}
    with open(os.path.join(folder, 'papers_data.jsons'), 'r') as f:
        for line in f.readlines():
            paper_data = json.loads(line.strip())
            year_data[paper_data['pdf_name']] = paper_data
    files = {}
    for file in os.listdir(os.path.join(folder, 'pdfs')):
        files[file] = pdf_parser.get_text(os.path.join(folder, 'pdfs', file), local=True)
    return files, year_data

#
# NEURIPS_DATA_OUTPUT = '/Users/gastonlhuillier/Personal/neurips_crawler/output'
#
# data = {}  # year -> NeurIPS object
# files = {}  # file_name -> text of file
# for folder in tqdm(os.listdir(NEURIPS_DATA_OUTPUT)):
#     year = folder.split('_')[-1]
#     ffiles, fdata = load_folder(os.path.join(NEURIPS_DATA_OUTPUT, folder))
#     data[year] = fdata
#     files.update(ffiles)
#
# print(f'total years of data: {len(data)}')
# print(f'total papers: {len(files)}')
