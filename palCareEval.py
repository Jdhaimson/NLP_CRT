from collections import Counter
from datetime import datetime, timedelta

from loader import get_data

class Range:
    def __init__(self, low, high):
        self.low = self.icd9_to_float(low)
        self.high = self.icd9_to_float(high)
    def icd9_to_float(self, icd9):
        try:
            return float(icd9)
        except ValueError:
            extension = float(icd9[1:])
            letter = icd9[0]
            return ord(letter)*1000 + extension
    def __eq__(self, other):
        other = self.icd9_to_float(other)
        return other >= self.low and other <= self.high
    def __ne__(self, other):
        return not self.__eq__(other)

num_patients = 1579
#num_patients = 100

dead_patients = []
gender = []
age = []
is_cancer = []
consult_time = []
cancer_time = []
cancer_mgh_time = []
cardio_mgh_time = []
noncancer_time = []
utilization = []
utilization_cancer = []
utilization_mgh_cancer = []
utilization_noncancer = []
utilization_mgh_cardio = []
for i in range(num_patients):
    p = get_data([i])[0]
    # Filter to only dead patients
    if p['Vital_status'] == 'Date of Death reported from SS Death Master File':
        if p['Consult_Date'] not in [None, '']:
            dead_patients.append(p['EMPI'])
            gender.append(p['Gender'])

            # Dates
            dob = datetime.strptime(p['Date_of_Birth'], "%m/%d/%Y")
            dod = datetime.strptime(p['Date_Of_Death\r'], "%m/%d/%Y")
            doc = datetime.strptime(p['Consult_Date'], "%m/%d/%Y")
            age.append((dod - dob).days/365.0)
            timing = dod - doc
            consult_time.append(timing.days)

            # Diagnoses
            cancer_icds = [Range(140.00, 209.99), Range(230.00, 239.99)]
            is_cancer_patient = False
            for d in p['Dia']:
                if d['Code_Type'] == 'ICD9':
                    try:
                        if d['Code'] in cancer_icds:
                            is_cancer_patient = True
                    except:
                        pass
            is_cancer.append(is_cancer_patient)


            # Stratify
            if is_cancer_patient:
                cancer_time.append(timing.days)
            else:
                noncancer_time.append(timing.days)

            # Utilization
            mgh_onc_enc_count = 0
            mgh_cardio_enc_count = 0
            utilization_cutoff = timedelta(days=30*3)
            num_eol_enc = 0
            len_eol_enc = 0
            died_in_hospital = False
            for enc in p['Enc']:
                admitted = datetime.strptime(enc['Admit_Date'], "%m/%d/%Y")

                # MGH?
                if (dod - admitted) < timedelta(days=365):
                    if enc['Clinic_Name'] == 'Medical Oncology Group (609)':
                        mgh_onc_enc_count += 1
                    elif enc['Clinic_Name'] == 'Cardiology (12)':
                        mgh_cardio_enc_count += 1

                if (dod - admitted) < utilization_cutoff:
                    num_eol_enc += 1
                    try:
                        discharged = datetime.strptime(enc['Discharge_Date'], "%m/%d/%Y")
                        if enc['Inpatient_Outpatient'] == 'Inpatient':
                            len_eol_enc += (discharged-admitted).days
                            if dod == discharged:
                                died_in_hospital = True
                    except:
                        pass
            utilization.append((timing.days, num_eol_enc, len_eol_enc, died_in_hospital))
            if is_cancer_patient:
                utilization_cancer.append((timing.days, num_eol_enc, len_eol_enc, died_in_hospital))
            else:
                utilization_noncancer.append((timing.days, num_eol_enc, len_eol_enc, died_in_hospital))

            # Is an MGH Oncology patient
            if mgh_onc_enc_count >= 2:
                utilization_mgh_cancer.append((timing.days, num_eol_enc, len_eol_enc, died_in_hospital))
                cancer_mgh_time.append(timing.days)

            if not is_cancer_patient and mgh_cardio_enc_count >= 2:
                utilization_mgh_cardio.append((timing.days, num_eol_enc, len_eol_enc, died_in_hospital))
                cardio_mgh_time.append(timing.days)
    else:
        if p['Vital_status'] != 'Not reported as deceased':
            print "***********************"
            print p['Vital_status'] 
            print "***********************"
# Step 1:
print "Percent of patients dead: " + str(float(len(dead_patients))/num_patients)

# Step 2:
# Age
print "Age distribution:"
print age
# Gender
print "Gender Distribution: " + str(Counter(gender))
# Cancer?
print "Is Cancer Patient: " + str(Counter(is_cancer))

# Step 3:
print "Consult timing distribution:"
print consult_time

# Step 4:
print "Cancer patient consult times:"
print cancer_time
print "MGH Cancer patient consult times:"
print cancer_mgh_time
print "Non-Cancer patient consult times:"
print noncancer_time 
print "MGH Cardio patient consult times:"
print cardio_mgh_time

# Step 5:
print "Utilization"
print utilization
print "Utilization: Cancer"
print utilization_cancer
print "Utilization: MGH Cancer"
print utilization_mgh_cancer
print "Utilization: Non Cancer"
print utilization_noncancer
print "Utilization: MGH Cardio"
print utilization_mgh_cardio
