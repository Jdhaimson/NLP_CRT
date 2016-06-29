import csv
import json
import os 
import re

path = '/home/josh/code/healthanon/CRT MGH 950 cohort/'
file_template = 'cl491_092315161707361168_'

def anonymize_doc(patient, doc):
    replacements = []
    replacements.append((patient['First_Name'], 'First_Name'))
    replacements.append((patient['Last_Name'], 'Last_Name'))
    replacements.append((patient['Last_Name'], 'Last_Name'))
    replacements.append((patient['EMPI'], patient['NEW_EMPI']))
    for mrn in patient['MRNS']:
        replacements.append((mrn, 'MRN'))

    for (regex, sub) in replacements:
        pattern = re.compile(regex, re.IGNORECASE)
        doc = re.sub(pattern, sub, doc)

    return doc
    

def get_docs_empi_map(doc_type):
    doc_file = path + file_template + doc_type + '.txt'
    with open(doc_file, 'r') as f:
        doc_text = f.read()
        doc_array = doc_text.split('[report_end]')
    
    doc_map = {}
    for doc in doc_array:
        empi = doc.split('\n')[1].split('|')[0]
        if empi not in doc_map:
            doc_map[empi] = []
        doc_map[empi].append(doc)

    return doc_map

def get_struct_empi_map(doc_type):
    doc_file = path + file_template + doc_type + '.txt'
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

        if empi not in doc_map:
            doc_map[empi] = []
        doc_map[empi].append(record)

    return doc_map

def get_patient_dem_info():
    # Get demographic text
    dem_file = path + file_template + 'Dem.txt'
    with open(dem_file, 'r') as f:
        dem_text = f.read()
        dem_array = dem_text.split('\n')

    # Get contact text
    contact_file = path + file_template + 'Con.txt'
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
            patient['EMPI'] = cols[0].strip()
            patient['MRNS'] = map(lambda x: x.strip(), cols[2].strip().split(','))
            patient['Last_Name'] = cols[3].strip()
            patient['First_Name'] = cols[4].strip()
            patient['Middle_Name'] = cols[5].strip()
            
            # store in dict
            patients[patient['EMPI']] = patient
        except:
            print('Error in contact dict build for row:')
            print row

    for row in dem_array[1:]:
        cols = row.strip().split('|')
        try:
            empi = cols[0].strip()
            patient = patients[empi]
            
            patient['Vital_status'] = cols[13].strip()
            patient['Date_Of_Death'] = cols[14].strip()
        except:
            print('Error in dem build for row:')
            print row

    return patients

def get_mrn_to_empi(patients):
    mrn_empi = {}
    for empi in patients.keys():
        patient = patients[empi]
        for mrn in patient['MRNS']:
            mrn_empi[mrn] = empi
    return mrn_empi


def parse_procedure_date_file(patients):
    proc_file = path + 'additional data/PATIENT_LIST_with_appointment_dates.csv'

    mrn_to_empi = get_mrn_to_empi(patients)
    patients_procs = {}
    with open(proc_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mrn = row['MR#'].strip().replace('-','')
            if mrn != '':
                try:
                    empi = mrn_to_empi[mrn]
                    patient = patients[empi]

                    del row['Name']
                    del row['MR#']
                    patients[empi]['Procedure'] = row
                except KeyError:
                    print "Error parsing procedure date for MRN:" + mrn

    write_null_if_empty(patients, 'Procedure')


def write_null_if_empty(patients, key):
    for empi in patients.keys():
        if key not in patients[empi]:
            patients[empi][key] = None
            

def parse_response_file(patients):
    resp_file = path + 'additional data/9 24 14 CRT Database for Charlotta.csv'

    mrn_to_empi = get_mrn_to_empi(patients)
    patients_procs = {}
    with open(resp_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mrn = row['Patient_ID'].strip()
            if mrn != '':
                try:
                    empi = mrn_to_empi[mrn]
                    patient = patients[empi]

                    del row['First_Name']
                    del row['Last_Name']
                    del row['Patient_ID']
                    del row['DOB']
                    patients[empi]['Supplemental'] = row
                except KeyError:
                    print "Error parsing supplemental data for MRN:" + mrn

    write_null_if_empty(patients, 'Supplemental')
        

if __name__ == "__main__":
    # Do the anonymization!

    patients = get_patient_dem_info()
    parse_procedure_date_file(patients)
    parse_response_file(patients)

    report_types = ['Car', 'Dis', 'End', 'Lno', 'Mic', 'Opn', 'Pat', 'Pul', 'Rad']
    for report_type in report_types:
        report_map = get_docs_empi_map(report_type)
        for key in patients.keys():
            try:
                docs = report_map[key]
                for doc in docs:
                    if report_type not in patients[key]:
                        patients[key][report_type] = []
                    patients[key][report_type].append(anonymize_doc(patients[key], doc))
            except:
                patients[key][report_type] = []
                print('Patient with empi:' + key + ' doesnt have report for report_type:' + report_type)

    struct_reports = ['Dia', 'Enc', 'Lab', 'Lhm', 'Lme', 'Lpr', 'Lvs', 'Med', 'Phy', 'Prc', 'Prv', 'Rdt', 'Rnd', 'Trn']
    for report_type in struct_reports:
        report_map = get_struct_empi_map(report_type)
        for key in patients.keys():
            try:
                patients[key][report_type] = report_map[key]
            except:
                patients[key][report_type] = []
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
     
    out_path = '/home/josh/code/healthanon/data/'
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    with open(out_path + 'mapping.csv', 'w') as f:
        for key in old_mapping.keys():
            f.write(key + ',' + old_mapping[key] + '\n')

    for key in anon_patients.keys():
        with open(out_path + key + '.json','w') as f:
            json.dump(anon_patients[key], f)
