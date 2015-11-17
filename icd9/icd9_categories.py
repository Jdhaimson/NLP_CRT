from collections import defaultdict
import os

def get_diagnosis_categories(return_descriptions=False):
    '''
    Parses the ICD9 Categories file to allow conversion of an ICD9 code 
    into a categorical hierarchy.
    :return: A dict from ICD9 codes (as strings like '0380') to their
             category (as strings like '1.1.2.1')
    '''
    filepath = (os.path.dirname(os.path.realpath(__file__)) 
                + '/ICD9_Diagnosis_Categories.txt')
    current_category = None
    icd9_to_category = {}
    category_to_description = {} # Not used yet, but maybe in the future
    with open(filepath, 'r') as f:
        for line in f:
            first_char = line[0]
            try:
                # This is a new category line
                int(first_char)
                current_category = line.split()[0]
                category_to_description[current_category] = ' '.join(line.split()[1:])
            except ValueError:
                # This is a list of ICD codes line
                if current_category is not None:
                    for code in line.split():
                        icd9_to_category[code] = current_category


    '''
    '''

    if not return_descriptions:
        return icd9_to_category
    else:
        return category_to_description

def get_max_diagnosis_info():
    category_to_description = get_diagnosis_categories(return_descriptions=True)
    maxes = defaultdict(lambda : -1)
    for key in category_to_description.keys():
        for (i, num_str) in enumerate(key.split('.')):
            num = int(num_str)
            if maxes[i] < num:
                maxes[i] = num
    return dict(maxes)
