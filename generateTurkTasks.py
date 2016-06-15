import csv
import itertools
import re

from loader import get_patient_by_EMPI
from extract_data import get_ef_value_notes
from shared_values import get_supplemental_list

keywords = ['(?:ef|ejection fraction)\s*(?:of|is)?[:\s]*([0-9]*\.?[0-9]*)\s*%']
allpatients = get_supplemental_list()
for key, patients in itertools.groupby(enumerate(allpatients), lambda k: k[0]//20):
    filename = "/home/ubuntu/www/turkTasks_" + str(key) + ".csv"
    print "Working on: " + filename
    rows = []
    for (_, patient) in patients:
        print patient
        patient_data = get_patient_by_EMPI(patient)
        efnotes = get_ef_value_notes(patient_data)
        for (_, ef_value, note) in efnotes:
            note_id = note.split('\n')[1].split('|')[3]

            # change new line to html br
            note = note.replace("\r\n", "<br>")

            # bold found matches
            for keyword in keywords:
                pattern = re.compile(keyword)
                matches = re.finditer(pattern, note)
                offset = 0
                for match in matches:
                    start = match.start() + offset
                    end = match.end() + offset
                    replacement = ("<span class='highlight'>"
                                   + note[start:end]
                                   + "</span>")
                    note = note[:start] + replacement + note[end:]
                    offset += len(replacement) - (end - start)

            rows.append((note, ef_value, patient, note_id))

    with open(filename, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['image1', 'guess', 'empi', 'note_id'])
        csvwriter.writerows(rows)
