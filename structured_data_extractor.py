import sys
import loader
import extract_data
import numpy as np
import build_graphs

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
        encounters.sort(key = lambda x: x[0]) # just sort on Admit_Date
    return encounters

def get_labs_before_date(empi, date):
    """Given an empi and a date, will return the labs for that patient before that date.
    Specifically, will return four dictionaries where the key is always the lab group id
    and the values are the total counts, low counts, high counts, and latest (date, low/high) tuple for 
    that test respectively. Note that low and high mean the test value was below or above the norm respectively."""
    p = loader.get_patient_by_EMPI(empi)
    lab_counts = {}
    lab_lows = {}
    lab_highs = {}
    lab_latest = {}
    if 'Lab' in p.keys():
        for lab in p['Lab']:
            if lab['Seq_Date_Time'] and extract_data.parse_date(lab['Seq_Date_Time']) < date: 
                if lab['Group_Id'] in lab_counts:
                    lab_counts[lab['Group_Id']] += 1
                else:
                    lab_counts[lab['Group_Id']] = 1
                lab_date = extract_data.parse_date(lab['Seq_Date_Time'])
                if lab['Group_Id'] in lab_latest:
                    recorded_test_date = lab_latest[lab['Group_Id']][0]
                    if lab_date > recorded_test_date: # keep most recent test value
                        lab_latest[lab['Group_Id']] = (lab_date, lab['Abnormal_Flag'])
                else:
                    lab_latest[lab['Group_Id']] = (lab_date, lab['Abnormal_Flag'])
                if lab['Abnormal_Flag']:
                    if lab['Abnormal_Flag'] == 'L':
                        if lab['Group_Id'] in lab_lows:
                            lab_lows[lab['Group_Id']] += 1
                        else:
                            lab_lows[lab['Group_Id']] = 1
                    elif lab['Abnormal_Flag'] == 'H':
                        if lab['Group_Id'] in lab_highs:
                            lab_highs[lab['Group_Id']] += 1
                        else:
                            lab_highs[lab['Group_Id']] = 1
    return lab_counts, lab_lows, lab_highs, lab_latest

def get_lab_history_before_date(empi, date, time_thresholds_months):
    """Given an empi and a date, will return a summarized history of the labs for that patient
    before the date.  Specifically, will return a dictionary where the key is a lab group id and
    the value is a list of size len(time_threshold_months) where each index represents whether the lab was mostly high or low
    in the threshold times set it time_thresholds_months.  For example, if we have 'BUN' => ['H', None, 'L'],
    then this indicates a transition from low (L) to high (H) leading up to the indicated date."""
    p = loader.get_patient_by_EMPI(empi)
    lab_history_counts = {}
    """
    lab_history_counts is 2-D array
    first dimension = time period
    second dimension = counts of 'H', 'L', and None
    example = [[15, 1, 2], ...] means in the past 1 month, 'H' was most (15 times)
    """
    seconds_in_month = 365 * 24 * 60 * 60 / 12
    values = ['H', 'L', None]
    if 'Lab' in p.keys():
        for lab in p['Lab']:
            if lab['Seq_Date_Time'] and extract_data.parse_date(lab['Seq_Date_Time']) < date:
                lab_date = extract_data.parse_date(lab['Seq_Date_Time'])
                value = lab['Abnormal_Flag'] if lab['Abnormal_Flag'] in ['H', 'L'] else None
                value_index = values.index(value)
                time_index = 0
                while time_index < len(time_thresholds_months) and (date - lab_date).total_seconds() > (time_thresholds_months[time_index] * seconds_in_month):
                    time_index += 1
                if time_index >= len(time_thresholds_months):
                    continue
                if lab['Group_Id'] not in lab_history_counts:
                    lab_history_counts[lab['Group_Id']] = np.zeros([len(time_thresholds_months), len(values)])
                lab_history_counts[lab['Group_Id']][time_index][value_index] += 1
    lab_history = {}
    for lab_name in lab_history_counts:
        lab_history[lab_name] = [None] * len(time_thresholds_months)
        for i in range(len(time_thresholds_months)):
            lab_history[lab_name][i] = values[lab_history_counts[lab_name][i].argmax()]
    return lab_history                  

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
    elif command == 'labs':
        """
        lab_counts, lab_lows, lab_highs, lab_latest = get_labs_before_date(empi, extract_data.parse_date('11/16/2015'))
        for lab in lab_counts:
            print(lab)
            print('COUNT: ' + str(lab_counts[lab]))
            print('LOWS: ' + str(lab_lows[lab]) if lab in lab_lows else 'LOWS: 0')
            print('HIGHS: ' + str(lab_highs[lab]) if lab in lab_highs else 'HIGHS: 0')
            print('LATEST: ' + str(lab_latest[lab]))
            print('')
        """
        operation_date = build_graphs.get_operation_date(loader.get_patient_by_EMPI(empi))
        lab_history = get_lab_history_before_date(empi, operation_date)
        for lab in lab_history:
            print(str(lab) + str(lab_history[lab]))
