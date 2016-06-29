import csv
import json
import os 

path1 = '/PHShome/ju601/crt/data/patients_10_2015/'
path2 = '/PHShome/ju601/crt/data/added_patients_4_2016/'
file_template1 = 'cl491_092315161707361168_'
file_template2 = 'cl491_04071618244390383_'
out_path = '/PHShome/ju601/crt/data/json/'
procedure_file = '/PHShome/ju601/crt/data/procedure_dates_updated.csv'

def get_docs_empi_map(doc_type, path, file_template):
    doc_file = path + file_template + doc_type + '.txt'
    with open(doc_file, 'r') as f:
        doc_text = f.read()
        doc_array = doc_text.split('[report_end]')

    # Get structured data fields from each report
    doc0_split = doc_array[0].split('\r\n')
    keys = doc0_split[0].split('|')
    doc_array[0] = '\r\n'.join(doc0_split[1:])
    
    doc_map = {}
    for doc_text in doc_array:
        doc = {}
        structured = doc_text.split('\r\n')[1].split('|')
        for (i, val) in enumerate(structured):
            doc[keys[i]] = val
        doc['free_text'] = doc_text
        empi = structured[0]
        if empi not in doc_map:
            doc_map[empi] = []
        doc_map[empi].append(doc)

    return doc_map

def get_struct_empi_map(doc_type, path, file_template):
    doc_file = path + file_template + doc_type + '.txt'
    with open(doc_file, 'r') as f:
        doc_text = f.read()
        doc_array = doc_text.split('\r\n')
    
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

def get_patient_dem_info(dem_file, patients = {}):
    # Get demographic text
    with open(dem_file, 'r') as f:
        dem_text = f.read()
        dem_array = dem_text.split('\r\n')

    # Build dictionary
    key_arr = dem_array[0].split('|')
    for row in dem_array[1:]:
        cols = row.strip().split('|')
        if len(cols) == len(key_arr):
            patient = {}
            for (i, col) in enumerate(cols):
                try:
                    if i == 2:
                        patient['MRNS'] = map(lambda x: x.strip(), col.strip().split(','))
                    else:
                        patient[key_arr[i]] = col
                except:
                    print('Error in contact dict build for row:')
                    print row

            if patient['EMPI'] in patients:
                print "DEMFILE- Duplicate patient: " + patient['EMPI']
            else:
                patients[patient['EMPI']] = patient

    return patients

def get_mrn_to_empi(patients):
    mrn_empi = {}
    for empi in patients.keys():
        patient = patients[empi]
        for mrn in patient['MRNS']:
            mrn_empi[mrn] = empi
    return mrn_empi

def parse_procedure_date_file(proc_file, patients):
    mrn_to_empi = get_mrn_to_empi(patients)
    patients_procs = {}
    with open(proc_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mrn = row['MRN']
            if mrn != '':
                try:
                    empi = mrn_to_empi[mrn]
                    patient = patients[empi]
                    proc = {}
                    proc['Implant Status'] = row['ImplantDate']
                    proc['1 Mo. Appt'] = ''
                    proc['3 Mo. Appt'] = ''
                    patient['Procedure'] = proc
                except KeyError:
                    print "Error parsing procedure date for MRN:" + mrn

    write_null_if_empty(patients, 'Procedure')

def add_reports(patients, report_types, is_structured, paths):
    if is_structured:
        report_id_key = 'Encounter_number'
    else:
        report_id_key = 'Report_Number'

    for report_type in report_types:
        patients_no_report = set(patients.keys())
        for (path, file_template) in paths:
            if is_structured:
                report_map = get_struct_empi_map(report_type, path, file_template)
            else:
                report_map = get_docs_empi_map(report_type, path, file_template)
            for patient in patients.keys():
                # Patient does not have any of these reports yet
                if report_type not in patients[patient]:
                    if patient in report_map and report_map[patient] != []:
                        patients[patient][report_type] = report_map[patient]
                        patients_no_report.remove(patient)

                # Patient already has some of these reports:
                else:
                    if patient in report_map:
                        for report in report_map[patient]:
                            # Only add unique reports
                            if report not in patients[patient][report_type]:
                                patients[patient][report_type].append(report)

        for patient in patients_no_report:
            patients[patient][report_type] = []
        print "Patients without report: " + report_type
        print patients_no_report


def write_null_if_empty(patients, key):
    for empi in patients.keys():
        if key not in patients[empi]:
            patients[empi][key] = None
            print "No " + key + " for patient: " + str(empi)
            

if __name__ == "__main__":
    paths = [(path1, file_template1), (path2, file_template2)]

    # Do the conversion!
    patients = get_patient_dem_info(path1 + file_template1 + 'Dem.txt')
    patients = get_patient_dem_info(path2 + file_template2 + 'Dem.txt', patients)
    parse_procedure_date_file(procedure_file, patients)

    # All unstructured report types:
    # report_types = ['Car', 'Dis', 'End', 'Lno', 'Mic', 'Opn', 'Pat', 'Pul', 'Rad']
    # Only include the ones you anticipate using in the following array:
    report_types = ['Car', 'Dis', 'End', 'Lno', 'Mic', 'Opn', 'Pat', 'Pul', 'Rad']
    report_types = ['Car', 'Dis', 'Lno', 'Rad']
    add_reports(patients, report_types, False, paths)

    # All structured report types:
    # struct_reports = ['Dia', 'Enc', 'Lab', 'Lhm', 'Lme', 'Lpr', 'Lvs', 'Med', 'Mrn', 'Phy', 'Prc', 'Prv', 'Rdt', 'Rnd', 'Trn']
    # Only include the ones you anticipate using in the following array:
    struct_reports = ['Dia', 'Enc', 'Lab', 'Lhm', 'Lme', 'Lpr', 'Lvs', 'Med', 'Mrn', 'Phy', 'Prc', 'Prv', 'Rdt', 'Trn']
    struct_reports = ['Dia', 'Enc', 'Lab', 'Med']
    add_reports(patients, struct_reports, True, paths)

    # Final write of info
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    for key in patients.keys():
        with open(out_path + key + '.json','w') as f:
            json.dump(patients[key], f)
