from typing import Dict, List, Optional
from collections import Counter

from papeles.paper.neurips import parsing_constants as pc
from papeles.utils.header import get_tokens


_FIND_LOCATION_INSTITUTIONS = ('university of california',
                               'university of massachusetts',
                               'eecs university of california',
                               'university of texas',
                               'the university of texas',
                               'university of texas at')


_INSTITUTIONS_KEYWORDS = (
    'university', 'group', 'dept', 'science', 'laboratory', 'lab', 'research', 'iiit',
    'inc.', 'labs', 'institute', 'technology', 'tech', 'dept.', 'sciences', 'department', 'engineering',
    'computer', 'ecole', 'inria', 'fraunhofer', 'inc', 'informatics', 'centre', 'mit', 'eecs', 'laboratoire',
    'institut', 'team', 'college', 'universitat', 'cybernetics', 'mpi-is', 'eth', 'tu', 'google', 'nicta', 'unam',
    'uc', 'technion', 'center', 'school', 'cnrs', 'univ', 'paristech', 'deepmind', 'ntu', 'politecnico',
    'epfl', 'computational', 'neuroscience', 'ucla', 'caltech', 'stanford', 'cmu', 'nvidia', 'openai',
    'centrum', 'amazon', 'technische', 'universität', 'seas', 'ut', 'mpi', 'université', 'ist', 'idsia', 'csail',
    'uw-madison', 'tecnologia', 'research–almaden', 'sutd', 'usi-supsi', 'dipartament', 'informatica', 'usc',
    'mathematics', 'matematica', 'cmla', 'ibm', 'leuven', 'nyu', 'foundation', 'uiuc', 'universite', 'facebook',
    'twitter', 'linkedin', 'bbva', 'ucl', 'apple', 'ucsc', 'suny', 'corp', 'corporation', 'universidad', 'iit',
    'kaist', 'nec', 'microsoft', 'sequel-inria/lifl-cnrs', 'deib', 'ucsd', 'mpi-sws', 'unc', 'icme',
    'ltci', 'polytechnique', 'école', 'department', 'faculty', 'università', 'informatik', 'iupui', 'kth',
    'riken', 'superieure', 'carnegie', 'ntt', 'purdue', 'collaboratory', 'aecom', 'minds', 'lg', 'electronics',
    'uber', 'wustl', 'lip6', 'upmc', 'aist', 'unviersity', '2tti-chicago', 'academia', 'jst', 'presto', 'inria/ens',
    'autonlab', 'ispgroup/icteam', 'fnrs', 'huawei', 'netflix', 'psychology', 'netﬂix', 'eurecom', 'ttic',
    'institutes', 'vinai', 'département', 'qualcomm', 'technologies', 'instituto', 'crest', 'ensae',
    'universita', 'cifar', 'departement', 'hkust', 'statistik', 'esat-stadius', 'yandex', 'philipps-universitat',
    'friedrich-schiller-universität', 'montanuniversitat', 'wilhelms-universität', 'cnrs-univ', 'oracle', 'sri'
)


def add_location(line, institution):
    """
    Given a city associated to an institution that matched the pattern
    """
    if 'los angeles' in line:
        institution.append('university of california los angeles')
    if 'irvine' in line:
        institution.append('university of california irvine')
    if 'santa cruz' in line:
        institution.append('university of california santa cruz')
    if 'san diego':
        institution.append('university of california san diego')
    if 'berkeley' in line:
        institution.append('university of california berkeley')
    if 'merced' in line:
        institution.append('university of california merced')
    if 'san francisco' in line:
        institution.append('university of california san francisco')
    if 'santa barbara' in line:
        institution.append('university of california santa barbara')
    if 'riverside' in line:
        institution.append('university of california riverside')
    if 'amherst' in line:
        institution.append('university of massachusetts amherst')
    if 'austin' in line:
        institution.append('university of texas at austin')
    if 'dallas' in line:
        institution.append('university of texas at dallas')
    if 'arlington' in line:
        institution.append('university of texas at arlington')
    if 'san antonio' in line:
        institution.append('university of texas at san antonio')
    if 'houston' in line:
        institution.append('university of texas at san houston')


def parse_institutions(header: List[str]) -> List[List[str]]:
    """
    Iterates over the lines in a header, finding matches with institution keywords and
    expanding institutions based on following lines.
    """
    institutions = []
    institution = []
    institutions_no_at = []

    find_location = False
    for line in header:
        match_line = get_tokens(line)
        match_line_joined = ' '.join(match_line).strip()
        match_intersection = set(match_line).intersection(_INSTITUTIONS_KEYWORDS)

        if find_location:
            add_location(line, institution)
        find_location = match_line_joined in _FIND_LOCATION_INSTITUTIONS

        if match_intersection:
            institutions_no_at.append([match_line_joined])

        if '@' in line:  # means that there's an email in the line, usually at the end of the name of the institution
            institutions.append(institution)
            institution = []
            continue

        if match_intersection and not find_location:
            institution.append(match_line_joined)

    if institutions:
        return institutions
    return institutions_no_at


def fix_typo(name: str) -> str:
    """
    Fix common typos from institution name
    """
    return ' '.join(pc.COMMON_TYPOS.get(x, x) for x in name.split(' '))


def fix_institution_parsing(name: str) -> List[str]:
    """
    Fix parsing, usually maps two or more institutions to the output
    """
    if name in pc.INSTITUTION_PARSING_FIXES:
        return pc.INSTITUTION_PARSING_FIXES.get(name)
    return [name]


def fix_institution_name(name: str) -> Optional[str]:
    """
    Maps institution name to a predefined mapping
    """
    if name in pc.INSTITUTIONS_DELETE:
        return None
    return pc.INSTITUTIONS_MAPPING.get(name, name)


def get_institutions_frequency(file_lines: Dict[str, List[str]]) -> Dict[str, int]:
    inst_counter = Counter()
    for file, lines in list(file_lines.items()):
        file_institutions = []
        for institution in parse_institutions(lines):
            if institution:
                name = fix_typo(institution[-1])
                names = fix_institution_parsing(name)
                for name in names:
                    file_institutions.append(fix_institution_name(name))
        unique_file_institutions = list(set(file_institutions))
        inst_counter.update(unique_file_institutions)

    cleaned = len([x for x in inst_counter.items() if x[1] > 0 and x[0]])
    total = sum([x[1] for x in inst_counter.items() if x[1] > 0 and x[0]])

    print(f'current institutions: {cleaned}')
    print(f'total raw institutions: {total}')
    print(f'clean-up fraction: {"{:0.2f}".format(1 - cleaned / total)}')

    return inst_counter


def get_file_institutions(lines, filtered_institutions=None):
    file_institutions = []
    for institution in parse_institutions(lines):
        if institution:
            name = fix_typo(institution[-1])
            names = fix_institution_parsing(name)
            for name in names:
                fixed_name = fix_institution_name(name)
                if filtered_institutions:
                    if fixed_name in filtered_institutions:
                        file_institutions.append(fixed_name)
                else:
                    file_institutions.append(fixed_name)
    return file_institutions
