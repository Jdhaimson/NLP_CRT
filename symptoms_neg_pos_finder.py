import re
import loader
import build_graphs
import extract_data

prefix = '(neither|nor|no|denies|not|do not think is|has not felt|far less|did not|without|does not|less|-|(-)|neg|neg for|negative|improved|depressed|negative for|no complaints of)'
suffix = '(:[ \t]*N|:[ \t]*n|:[ \t]*ok)'

def getSymptomsRegexes():
    symptoms_regexes = {}
    with open("symptoms_regex_final.txt") as f:
        content = f.readlines()
    for line in content:
        name, regex = line.strip().split(': ', 1)
        symptoms_regexes[name] = [re.compile(regex), re.compile(prefix + ' ' + regex), re.compile(regex + suffix)]
    return symptoms_regexes

def main():
    empi = "FAKE_EMPI_385" # testing a single patient
    symptoms_regexes = getSymptomsRegexes()
    person = loader.get_patient_by_EMPI(empi)
    operation_date = build_graphs.get_operation_date(person)
    note_types = ['Car', 'Lno']
    person_pos_history = {}
    person_neg_history = {}
    sec_per_day = 24 * 60 * 60
    for note_type in note_types:
        print 'Examining ' + note_type + ' Notes for Patient ' + empi
        date_key = extract_data.get_date_key(note_type)
        if note_type in person.keys() and date_key != None:
            for i in range(len(person[note_type])):
                print '\tNote' + str(i)
                doc = person[note_type][i]
                date = extract_data.parse_date(doc[date_key])
                if date != None:
                    delta_days = (date - operation_date).total_seconds() / sec_per_day
                    for sym in symptoms_regexes:
                        normal, neg_pre, neg_suff = [bool(x.search(doc['free_text'])) for x in symptoms_regexes[sym]]
                        if neg_pre or neg_suff:
                            if sym in person_neg_history:
                                person_neg_history[sym].append(delta_days)
                            else:
                                person_neg_history[sym] = [delta_days]
                            print '\t\tNegative,' + sym + ',' + str(delta_days)
                        elif normal:
                            if sym in person_pos_history:
                                person_pos_history[sym].append(delta_days)
                            else:
                                person_pos_history[sym] = [delta_days]
                            print '\t\tPositive,' + sym + ',' + str(delta_days)
    return person_pos_history, person_neg_history
                        
if __name__ == '__main__':
    pos, neg = main()
    print pos
