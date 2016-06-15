from collections import defaultdict, Counter
from datetime import date, datetime, timedelta
import numpy as np

from extract_data import get_operation_date, get_ef_values
from language_processing import parse_m_d_y
from loader import get_data

def get_baseline_lab_value(p, lab_types, procedure_date):
    for lab in p['Lab']:
        if lab['Test_Description'] in lab_types:
            date = datetime.strptime(lab['Seq_Date_Time'], "%m/%d/%Y %H:%M").date()
            if date == procedure_date:
                try:
                    return float(lab['Result'])
                except:
                    return None
    return None

def filter_out_post_procedure(documents, procedure_date, date_key):
    doc_list = []
    for doc in documents:
        date = parse_m_d_y(doc[date_key])
        p_delta = (date - procedure_date).days
        if p_delta <= 0:
            doc_list.append((p_delta, doc))
    return sorted(doc_list)


def get_n_preprocedure_dia(diagnoses, procedure_date, n):
    d_list = filter_out_post_procedure(diagnoses, procedure_date, 'Date')
    n = min(n, len(d_list))
    return map(lambda x: x[1], d_list[-1*n:])

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

cpt = {
    'crt_out': [33224, 33225, 33226]
}
icds = {
    'crt_in': [00.50, 00.51],
    'ischemic': [410.0, 410.01, 410.02, 410.1, 410.10, 410.11, 410.12, 410.2, 410.20, 410.21, 410.22, 410.3, 410.30, 410.31, 410.32, 410.4, 410.40, 410.41, 410.42, 410.5, 410.50, 410.51, 410.52, 410.6, 410.60, 410.61, 410.62, 410.7, 410.70, 410.71, 410.72, 410.8, 410.80, 410.81, 410.82, 410.9, 410.90, 410.91, 410.92, 411.0, 411.1, 411.8, 411.81, 411.89, 412.0, 413.0, 413.1, 413.9, 414.0, 414.00, 414.01, 414.02, 414.03, 414.04, 414.05, 414.06, 414.07, 414.1, 414.10, 414.11, 414.12, 414.19, 414.2, 414.3, 414.4, 414.8, 414.9],
    'non-ischemic': [425.4],
    'arrhythmia': [427.1, 427.4, 427.41, 427.42, 427.5, 427.9],
    'lbbb': [426.3, 426.2, 426.51, 426.52, 426.53],
    'av_block': [426.0],
    'afib': [427.31],
    'cpd': [Range(490, 492.8), Range(493.00, 493.92), Range(494, 494.1), Range(495.0, 505), 506.4],
    'diabetes': [Range(250.00, 250.33), Range(250.40, 250.93)],
    'renal_disease': [403.01, 403.11, 403.91, 404.02, 404.03, 404.12, 404.13, 404.92, 404.93, 585, 586, 'V42.0', 'V45.1', Range('V56.0', 'V56.2'), 'V56.8']
}

def get_ef_delta(patient_data):
    after_threshold = 365
    ef_values = get_ef_values(patient_data)
    sorted_ef = sorted(ef_values)
    before = None
    before_date = None
    after = None
    after_date = None
    dist_from_thresh = float('inf')
    for (rel_date, ef_value) in sorted_ef:
        if rel_date <= 0:
            before = ef_value
            before_date = rel_date
        else:
            dist = abs(rel_date - after_threshold)
            if dist < dist_from_thresh:
                after = ef_value
                after_date = rel_date
                dist_from_thresh = dist
    if before is not None and after is not None:
        return (after - before, before, after, before_date, after_date)
    else:
        return (None, None, None, None, None)

# Collect statistics
stats = defaultdict(list) 
for i in range(906):
    p = get_data([i])[0]
    print p['NEW_EMPI']

    procedure_date = get_operation_date(p)
    if procedure_date:
        (ef_delta, baseline_ef, followup_ef, baseline_date, followup_date) = get_ef_delta(p)    
        if baseline_ef:
            if followup_date > 100 and followup_date < 500 and baseline_date > -3:
                stats['procedure_date'].append(procedure_date)
                stats['baseline_days'].append(baseline_date)
                stats['followup_days'].append(followup_date)
                stats['baseline_lvef'].append(baseline_ef)
                stats['lvef_followup'].append(followup_ef)
                stats['lvef_change'].append(ef_delta)

                stats['sex'].append(p['Sex'])
                stats['n_enc'].append(len(filter_out_post_procedure(p['Enc'], procedure_date, 'Admit_Date')))

                if p['Date_of_Death']:
                    death_date = parse_m_d_y(p['Date_of_Death'])
                    stats['died_in_year'].append((death_date - procedure_date) < timedelta(365))
                else:
                    stats['died_in_year'].append(False)

                dia = get_n_preprocedure_dia(p['Dia'], procedure_date, 76)
                icd_present = defaultdict(lambda : False)
                for d in dia:
                    if d['Code_Type'] == 'ICD9':
                        try:
                            code = float(d['Code'])
                        except ValueError:
                            code = d['Code']
                        for key in icds.keys():
                            if code in icds[key]:
                                icd_present[key] = True
                    """
                    elif d['Code_Type'] == 'CPT':
                        try:
                            code = float(d['Code'])
                            for key in cpt.keys():
                                if code in cpt[key]:
                                    icd_present[key] = True
                        except:
                            pass
                    """

                            
                for key in icds.keys():
                    stats[key].append(icd_present[key])

                stats['baseline_creatinine'].append(get_baseline_lab_value(p, ['Plasma Creatinine', 'Creatinine'], procedure_date))
                stats['baseline_sodium'].append(get_baseline_lab_value(p, ['Plasma Sodium'], procedure_date))
                stats['baseline_hgb'].append(get_baseline_lab_value(p, ['HGB'], procedure_date))


print "Demographics:"
print "Num: " + str(len(stats['procedure_date']))
sex = Counter(stats['sex'])
print "Male: " + str(sex["Male\r\n"]/float(sum(sex.values())))

print "\nMGH Care:"
iqr = np.subtract(*np.percentile(stats['n_enc'], [75, 25]))
print "Median Pre-Procedure Encounters: " + str(np.median(stats['n_enc'])) + " (" + str(iqr) + ")"

print "\nDiagnoses:"
ischemic = Counter(stats['ischemic'])
print "Ischemic: " + str(ischemic[True]/float(sum(ischemic.values())))
nonischemic = Counter(stats['non-ischemic'])
print "Non-Ischemic: " + str(nonischemic[True]/float(sum(nonischemic.values())))
lbbb = Counter(stats['lbbb'])
print "lbbb: " + str(lbbb[True]/float(sum(lbbb.values())))
arrhythmia = Counter(stats['arrhythmia'])
print "arrhythmia: " + str(arrhythmia[True]/float(sum(arrhythmia.values())))
av_block = Counter(stats['av_block'])
print "av_block: " + str(av_block[True]/float(sum(av_block.values())))
afib = Counter(stats['afib'])
print "afib: " + str(afib[True]/float(sum(afib.values())))
crt_in = Counter(stats['crt_in'])
print "crt_in: " + str(crt_in[True]/float(sum(crt_in.values())))
#crt_out = Counter(stats['crt_out'])
#print "crt_out: " + str(crt_out[True]/float(sum(crt_out.values())))

print "\nComorbidities:"
cpd = Counter(stats['cpd'])
print "cpd: " + str(cpd[True]/float(sum(cpd.values())))
diabetes = Counter(stats['diabetes'])
print "diabetes: " + str(diabetes[True]/float(sum(diabetes.values())))
renal_disease = Counter(stats['renal_disease'])
print "renal_disease: " + str(renal_disease[True]/float(sum(renal_disease.values())))


#iqr = np.subtract(*np.percentile(x, [75, 25]))
print "\nBaseline Data:"
lvef_array = filter(lambda x: bool(x), stats['baseline_lvef'])
print "LVEF: " + str(np.mean(lvef_array)) + " (" + str(np.std(lvef_array)) + ")"
creatinine_array = filter(lambda x: bool(x), stats['baseline_creatinine'])
print "Creatinine: " + str(np.mean(creatinine_array)) + " (" + str(np.std(creatinine_array)) + ")"
sodium_array = filter(lambda x: bool(x), stats['baseline_sodium'])
print "Sodium: " + str(np.mean(sodium_array)) + " (" + str(np.std(sodium_array)) + ")"
hgb_array = filter(lambda x: bool(x), stats['baseline_hgb'])
print "HGB: " + str(np.mean(hgb_array)) + " (" + str(np.std(hgb_array)) + ")"

print "\nMedications:"


print "\nYear:"
print "Earliest: " + str(sorted(stats['procedure_date'])[:10])
print "Latest: " + str(max(stats['procedure_date']))
pre_2009 = Counter(map(lambda x: x < date(2009, 1, 1), stats['procedure_date']))
print "Pre-2009: " + str(pre_2009[True]/float(sum(pre_2009.values())))
p_2009_2012 = Counter(map(lambda x: x >= date(2009, 1, 1) and x < date(2013, 1, 1), stats['procedure_date']))
print "2009-2012: " + str(p_2009_2012[True]/float(sum(p_2009_2012.values())))
p_2012 = Counter(map(lambda x: x >= date(2013, 1, 1), stats['procedure_date']))
print "post-2012: " + str(p_2012[True]/float(sum(p_2012.values())))

print "\nTable 2"
base_lvef_days = filter(lambda x: x is not None, stats['baseline_days'])
print "Baseline Days: " + str(np.mean(base_lvef_days)) + " (" + str(np.std(base_lvef_days)) + ")"
#print base_lvef_days
lvef_days = filter(lambda x: x is not None, stats['followup_days'])
#print lvef_days
print "Followup Days: " + str(np.mean(lvef_days)) + " (" + str(np.std(lvef_days)) + ")"
lvef_followup = filter(lambda x: x is not None, stats['lvef_followup'])
print "Followup LVEF: " + str(np.mean(lvef_followup)) + " (" + str(np.std(lvef_followup)) + ")"
lvef_change = filter(lambda x: x is not None, stats['lvef_change'])
print "LVEF Change: " + str(np.mean(lvef_change)) + " (" + str(np.std(lvef_change)) + ")"
def change_to_response(x):
    if x < 5:
        return "Non-Responder"
    elif x < 15:
        return "Responder"
    else:
        return "Super-Responder"
lvef_response = Counter(map(change_to_response, lvef_change))
print "Non-Responder: " + str(lvef_response['Non-Responder']/float(sum(lvef_response.values())))
print "Responder: " + str(lvef_response['Responder']/float(sum(lvef_response.values())))
print "Super-Responder: " + str(lvef_response['Super-Responder']/float(sum(lvef_response.values())))
died_in_year = Counter(stats['died_in_year'])
print "Died within 1 year: " + str(died_in_year[True]/float(sum(died_in_year.values())))
