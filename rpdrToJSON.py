import json
import os 

path = '/PHShome/ju601/crt/MGHpallcare/'
file_template = 'CL491_070915120556917455_MGH_'
out_path = path + '/json/'

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

    # Build dictionary
    patients = {}
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

            patients[patient['EMPI']] = patient

    return patients

def get_mrn_to_empi(patients):
    mrn_empi = {}
    for empi in patients.keys():
        patient = patients[empi]
        for mrn in patient['MRNS']:
            mrn_empi[mrn] = empi
    return mrn_empi


def parse_consultation_date_file(patients):
    date_file = path + 'Date.txt'

    mrn_to_empi = get_mrn_to_empi(patients)
    patients_dates = {}
    with open(date_file, 'r') as f:
        date_arr = f.read().split('\n')
        for row in date_arr:
            row_arr = row.split(' ')
            if len(row_arr) == 2:
                (mrn, date) = row_arr
                try:
                    empi = mrn_to_empi[mrn]
                    print empi
                    patient = patients[empi]
                    patient['Consult_Date'] = date
                except KeyError:
                    print "Error parsing consult date for MRN:" + mrn

    write_null_if_empty(patients, 'Consult_Date')


def write_null_if_empty(patients, key):
    for empi in patients.keys():
        if key not in patients[empi]:
            patients[empi][key] = None
            

if __name__ == "__main__":
    # Do the conversion!

    patients = get_patient_dem_info()
    parse_consultation_date_file(patients)

    # All unstructured report types:
    # report_types = ['Car', 'Dis', 'End', 'Lno', 'Mic', 'Opn', 'Pat', 'Pul', 'Rad']
    # Only include the ones you anticipate using in the following array:
    report_types = []
    for report_type in report_types:
        report_map = get_docs_empi_map(report_type)
        for patient in patients.keys():
            try:
                patients[patient][report_type] = report_map[patient]
            except:
                patients[patient][report_type] = []
                print('Patient with empi:' + patient + ' doesnt have report for report_type:' + report_type)


    # All structured report types:
    # struct_reports = ['Dia', 'Enc', 'Lab', 'Lhm', 'Lme', 'Lpr', 'Lvs', 'Med', 'Phy', 'Prc', 'Prv', 'Rdt', 'Rnd', 'Trn']
    # Only include the ones you anticipate using in the following array:
    struct_reports = ['Dia', 'Enc']
    for report_type in struct_reports:
        report_map = get_struct_empi_map(report_type)
        for patient in patients.keys():
            try:
                patients[patient][report_type] = report_map[patient]
            except:
                patients[patient][report_type] = []
                print('Patient with empi:' + patient + ' doesnt have report for report_type:' + report_type)

    # Final write of info
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    for key in patients.keys():
        with open(out_path + key + '.json','w') as f:
            json.dump(patients[key], f)
