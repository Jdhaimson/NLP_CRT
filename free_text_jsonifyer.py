import language_processing as lp
import loader
import json

def jsonify_text(person_id):
    person = loader.get_data([person_id])[0]
    for key in person.keys():
        if lp.is_note_doc(key):
            for i in range(len(person[key])):
                doc = person[key][i]
                data = lp.parse_note_header(doc, key)
                data['free_text'] = doc
                person[key][i] = data
    with open('./data/patients/FAKE_EMPI_' + str(person_id) + '.json', 'w') as outfile:
        json.dump(person, outfile)
        print 'JSONIFIED PERSON ' + str(person_id)

def jsonify_all(num_of_patients):
    for i in range(num_of_patients):
        jsonify_text(i)

if __name__ == '__main__':
    # uncomment below to JSONIFY all files, but they should already be jsonified to be careful...
    # jsonify_all(907)     
