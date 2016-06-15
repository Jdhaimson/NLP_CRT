from collections import defaultdict
import re

from loader import get_patient_by_EMPI
from model_tester import get_preprocessed_patients, change_ef_values_to_categories

patient_empis, patient_efs = get_preprocessed_patients(sample_size=906)
response_status = change_ef_values_to_categories(patient_efs)

bigrams = [('Lno', ["back pain", "daily nitroglycerin", "and palpitations", "sleep apnea", "admitted with", "has progressed", "married and", "father died"]),
           ('Car', ["is normal"])
          ]


out = {}
for (doc_type, patterns) in bigrams:
    for pattern in patterns:
        out[doc_type + pattern] = open("bigram_data/" + doc_type + '_' + pattern.replace(' ', '_') + '_bigrams.txt', 'w')

for (i, empi) in enumerate(patient_empis):
    print empi
    p = get_patient_by_EMPI(empi)
    for (doc_type, patterns) in bigrams:
        for doc in p[doc_type]:
            for pattern in patterns:
                if re.search(pattern, doc['free_text']):
                    out[doc_type + pattern].write("Patient: " + empi + " Outcome: " + ("Non-Response" if response_status[i] else "Response"))
                    out[doc_type + pattern].write(doc['free_text'])

for key in out.keys():
    out[key].close()
