import re
import json

path = '/media/josh/Josh/CRT MGH 950 cohort/'

def anonymize_doc(patient, doc):
    replacements = []
    replacements.append((patient['First_Name'], 'First_Name'))
    replacements.append((patient['Last_Name'], 'Last_Name'))
    replacements.append((patient['Last_Name'], 'Last_Name'))
    replacements.append((patient['EMPI'], patient['NEW_EMPI']))
    for mrn in patient['MRNS']:
        replacements.append((mrn.strip(), 'MRN'))

    for (regex, sub) in replacements:
        doc = re.sub(regex, sub, doc)

    return doc
    

def get_docs_empi_map(doc_type):
    doc_file = path + 'cl491_092315161707361168_' + doc_type + '.txt'
    with open(doc_file, 'r') as f:
        doc_text = f.read()
        doc_array = doc_text.split('[report_end]')
    
    doc_map = {}
    for doc in doc_array:
        empi = doc.split('\n')[1].split('|')[0]
        if empi not in doc_map:
            doc_map[empi] = ''
        doc_map[empi] += doc

    return doc_map

def get_struct_empi_map(doc_type):
    doc_file = path + 'cl491_092315161707361168_' + doc_type + '.txt'
    with open(doc_file, 'r') as f:
        doc_text = f.read()
        doc_array = doc_text.split('\n')
    
    doc_map = {}
    keys = doc_array[0].split('|')
    for row in doc_array[1:]:
        cols = row.split('|')
        empi = cols[0]
        record = {}
        try:
            for i in range(3, len(keys)):
                key = keys[i]
                record[key] = cols[i]
        except:
            print 'Error for type:' + doc_type + ' column:' + str(i) + ' row:' + row
        doc_map[empi] = record

    return doc_map

def get_patient_dem_info():
    # Get demographic text
    dem_file = path + 'cl491_092315161707361168_Dem.txt'
    with open(dem_file, 'r') as f:
        dem_text = f.read()
        dem_array = dem_text.split('\n')

    # Get contact text
    contact_file = path + 'cl491_092315161707361168_Con.txt'
    with open(contact_file, 'r') as f:
        contact_text = f.read()
        contact_array = contact_text.split('\n')

    # Build dictionary
    patients = {}
    for (i, row) in enumerate(contact_array[1:]):
        cols = row.strip().split('|')
        patient = {}
        try:
            patient['NEW_EMPI'] = 'FAKE_EMPI_' + str(i)
            patient['EMPI'] = cols[0]
            patient['MRNS'] = cols[2].strip().split(',')
            patient['Last_Name'] = cols[3]
            patient['First_Name'] = cols[4]
            patient['Middle_Name'] = cols[5]
            
            # store in dict
            patients[patient['EMPI']] = patient
        except:
            print('Error in contact dict build for row:')
            print row

    for row in dem_array[1:]:
        cols = row.strip().split('|')
        try:
            empi = cols[0]
            patient = patients[empi]
            
            patient['Vital_status'] = cols[13]
            patient['Date_of_Death'] = cols[14]
        except:
            print('Error in dem build for row:')
            print row

    return patients

# Attach all unstructured reports to the patients
patients = get_patient_dem_info()

report_types = ['Car', 'Dis', 'End', 'Lno', 'Mic', 'Opn', 'Pat', 'Pul', 'Rad']
for report_type in report_types:
    report_map = get_docs_empi_map(report_type)
    for key in patients.keys():
        try:
            doc = report_map[key]
            patients[key][report_type] = anonymize_doc(patients[key], doc)
        except:
            patients[key][report_type] = ''
            print('Patient with empi:' + key + ' doesnt have report for report_type:' + report_type)

struct_reports = ['Dia', 'Enc', 'Lab', 'Lhm', 'Lme', 'Lpr', 'Lvs', 'Med', 'Phy', 'Prc', 'Prv', 'Rdt', 'Rnd', 'Trn']
for report_type in struct_reports:
    report_map = get_struct_empi_map(report_type)
    for key in patients.keys():
        try:
            patients[key][report_type] = report_map[key]
        except:
            patients[key][report_type] = {}
            print('Patient with empi:' + key + ' doesnt have report for report_type:' + report_type)

# Final delete of info
anon_patients = {}
old_mapping = {}
for key in patients.keys():
    patient = patients[key]
    old_mapping[patient['EMPI']] = patient['NEW_EMPI']
    del patient['EMPI']
    del patient['MRNS']
    del patient['Last_Name']
    del patient['First_Name']
    del patient['Middle_Name']
    anon_patients[patient['NEW_EMPI']] = patient
 
with open('mapping.csv', 'w') as f:
    for key in old_mapping.keys():
        f.write(key + ',' + old_mapping[key] + '\n')

with open('anon_data.json', 'w') as f:
    json.dump(anon_patients, f)
