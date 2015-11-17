import sys
import loader
import extract_data

def get_supplemental_details(field_name):
    """Takes in the name of a field and prints how many of the patients have that field.
    Note that the field must be a top-level field (i.e. 'Car', 'Lno', etc.).
    This was used to test how many patients had the 'Supplemental' field."""
    total = 0
    field_count = 0
    for i in range(907):
        try:
            p = loader.get_patient_by_EMPI("FAKE_EMPI_" + str(i))
            if field_name in p.keys():
                if p[field_name] != None:
                    print(str(i) + ": " + str(len(p[field_name])))
                    field_count += 1
                else:
                    print(str(i) + ": " + str(0))
            total += 1
        except Exception as e:
            print(str(i) + " DOES NOT EXIST")
            continue
    print("RESULTS: " + str(field_count) + "/" + str(total))

def get_diagnoses(empi):
    """Given an empi, will the return the diagnosis timeline T for that patient.
    T is just an array of tuples of the form (diagnosis date, Code_Type, code, diagnosis name),
    sorted by date. Note that a given date may, and often does, have several diagnoses.  Also,
    a diagnosis can be repeatedly reported on every visit."""
    p = loader.get_patient_by_EMPI(empi)
    diagnoses = [] 
    if 'Dia' in p.keys():
        for dia in p['Dia']:
            diagnoses.append((extract_data.parse_date(dia['Date']), dia['Code_Type'], dia['Code'], dia['Diagnosis_Name']))
        diagnoses.sort()
    return diagnoses

def get_date_to_diagnoses(empi):
    """Given an empi, returns a map from dates to lists of diagnoses
    for the patient at those dates"""
    diagnoses = get_diagnoses(empi)
    date_to_diagnoses = {}
    for d in diagnoses:
        date = d[0]
        if date in date_to_diagnoses:
            date_to_diagnoses[date].append(d[1:])
        else:
            date_to_diagnoses[date] = [d[1:]]
    return date_to_diagnoses

def get_diagnosis_to_dates(empi):
    """Given an empi, returns a map from diagnoses to lists of
    dates that the diagnoisis was recorded at for the patient.
    Note that diagnoses are tuples of the form (ICD9, name)."""
    diagnoses = get_diagnoses(empi)
    diagnosis_to_dates = {}
    for d in diagnoses:
        diagnosis = d[1:]
        if diagnosis in diagnosis_to_dates:
            diagnosis_to_dates[diagnosis].append(d[0])
        else:
            diagnosis_to_dates[diagnosis] = [d[0]]
    return diagnosis_to_dates

def get_chronic_diagnoses(empi, threshold_days):
    """Given an empi and a threshold number of days, returns a list
    of diagnoses for the patient that were recorded multiple times and
    at least threshold_days apart."""
    diagnosis_to_dates = get_diagnosis_to_dates(empi)
    threshold = threshold_days * 24 * 60 * 60
    chronics = []
    for diagnosis in diagnosis_to_dates:            
        first_date = diagnosis_to_dates[diagnosis][0]
        last_date = diagnosis_to_dates[diagnosis][-1]
        if (last_date - first_date).total_seconds() > threshold:
            chronics.append(diagnosis)
    return chronics 

def get_encounters_details(empi):
    """Used in testing the Enc field to understand what subfields exist and what values they take"""
    p = loader.get_patient_by_EMPI(empi)
    interesting_fields = ['Admit_Date', 'Inpatient_Outpatient', 'Discharge_Date', 'LOS_Days', 'DRG']
    for enc in p['Enc']:
        print('ENCOUNTER ' + enc['Encounter_number'] + ':')
        for field in interesting_fields:
            if enc[field]:
                print(field + ' = ' + str(enc[field]))
        extra_diagnoses = 0
        for i in range(1, 10):
            if enc['Diagnosis_' + str(i)]:
                extra_diagnoses += 1
        print('Extra Diagnoses = ' + str(extra_diagnoses))
        print('')
    ins = 0
    outs = 0
    for enc in p['Enc']:
        if enc['Inpatient_Outpatient'] == 'Inpatient':
            ins += 1
        else:
            outs += 1
    print(str(ins) + ' Inpatients')
    print(str(outs) + ' Outpatients')

def get_encounters(empi):
    """Given an empi, returns a list of encounters for that patient
    sorted by Admit Date (since Discharge Date is not always recorded)."""
    p = loader.get_patient_by_EMPI(empi)
    encounters = []
    if 'Enc' in p.keys():
        for enc in p['Enc']:
            extra_diagnoses = 0
            for i in range(1, 10):
                if enc['Diagnosis_' + str(i)]:
                    extra_diagnoses += 1
            if enc['Admit_Date']:
                encounters.append((extract_data.parse_date(enc['Admit_Date']), str(enc['Inpatient_Outpatient']), extract_data.parse_date(enc['Discharge_Date']), int(enc['LOS_Days']) if enc['LOS_Days'] else 0, extra_diagnoses))
        encounters.sort()
    return encounters

if __name__ == "__main__":
    # get_supplemental_details('Supplemental')
    command = sys.argv[1]
    empi = sys.argv[2]
    if command == 'diagnosis': 
        diagnoses = get_diagnoses(empi)
        for d in diagnoses:
            print(d)
        date_to_diagnoses = get_date_to_diagnoses(empi)
        chronic_diagnoses = get_chronic_diagnoses(empi, 90)
        start_date = diagnoses[0][0]
        end_date = diagnoses[-1][0]
        print("~~~~~~~~~~~~~~~~")
        print("Start Date: " + str(start_date))
        print("End Date: " + str(end_date))
        print("Num. of Entries: " + str(len(diagnoses)))
        print("Num. of Visits: " + str(len(date_to_diagnoses)))
        # print("Chronic Diagnoses: " + str(chronic_diagnoses))
    elif command == 'encounter':
        encounters = get_encounters(empi)
        for enc in encounters:
            print(enc)
        #get_encounters_details(empi)
