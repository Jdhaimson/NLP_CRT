import json
import os

# Deprecated
#loads old annonomyzed data from JSON file into nested dictionary
def get_old_data():
    with open('data/anon_data_OLD.json', 'r') as f:
        data = json.load(f)
    return data

# Gets a specific patient by their EMPI
def get_patient_by_EMPI(empi):
    patients_path = '/home/ubuntu/project/data/patients/'
    file_path = patients_path + empi + '.json'
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            patient = json.load(f)
        return patient
    else:
        raise ValueError("Patient with EMPI: " + empi + " does not exist")

def get_data(patient_range=range(0,10)):
    patients_path = '/home/ubuntu/project/data/patients/'
    files = os.listdir(patients_path)
    # Sort by number order
    files = sorted(files, key=lambda x: int(x.split('.json')[0].split('_')[2]))

    # Get all patients in patient range
    patients = []
    for i in patient_range:
        if i < len(files):
            file_path = patients_path + files[i]
            with open(file_path, 'r') as f:
                patient = json.load(f)
                patients.append(patient)
    return patients

def get_dummy_non_anonymized_patient():
    return {'First_Name':'Josh', 'Last_Name':'Haimson', 'EMPI':'1234emPI', 'NEW_EMPI':'FAKE_EMPI_1', 'MRNS':['mrn12','mrn34']}

#Removes empty fields from data
#Recursive, modifies object, returns nothing
def clean_data(data):
    if type(data) == type(dict()):
        for k in data.keys():
            clean_data(data[k])
            if data[k] in [u'', [], "", dict(), None]:
                data.pop(k)
    elif type(data) == type([]):
        for i in range(len(data)):
            clean_data(data[i])    

#little function to help with exploring the data from commandline
def explore(data):
    if type(data) == type(dict()) or (type(data) ==  type([]) and len(data)>1):
        again = True
        
        while again:
            if type(data) == type(dict()):    
                keys = data.keys()
                for i in range(len(keys)):
                    size = ""
                    if type(data[keys[i]]) == type([]):
                        if len(data[keys[i]]) > 1:
                            size = " (" + str(len(data[keys[i]])) + ")"
                    print str(i+1) + ".\t", keys[i], size
                inp = unicode("-1")
                while not(inp == ""  or  inp in keys or (inp.isnumeric() and ( int(inp) > 0 and int(inp) <= len(keys)))):
                    inp = unicode(raw_input("Select a key: "))
                print ""
                if inp != "" and inp.isnumeric():
                    print keys[int(inp)-1], ": "
                    explore(data[keys[int(inp)-1]])
                elif inp == "":
                    again = False
                else:
                    print inp, ": "
                    explore(data[inp])
            else:
                inp = unicode("-1")
                while not(inp == "" or (inp.isnumeric() and int(inp) > 0 and int(inp) <= len(data))):
                    inp = unicode(raw_input("Select a file from 1-" + str(len(data)) +": "))
                if inp != "":
                    explore(data[int(inp)-1])
                else:
                    again = False 
    elif type(data) == type([]):
        explore(data[0])  
    else:
        print data.strip("\n")
        print
        inp = raw_input("[ Press enter to continue ]")
        print

#Makes dictionaries and nested dictionaries easy to read
def dict_to_string(myDict, tabs = 0, width = 100):
    tab = "    "
    output = ""
    for key in myDict:
        output += tab * tabs + str(key) + ":\n"
        item = myDict[key]
        if type(item) == type(dict()):
            output += format(item, tabs + 1, width)
        else:
            item = item.strip("\n")
            item = item.strip("\t")
            item = item.replace("\n", "; ")
            item = item.replace("\t", "   ")
            size = width - len(tab)*(tabs+1)
            if(len(item) <= size):
                output += tab * (tabs + 1) + item + "\n"
            else:
                output += tab * (tabs + 1) + item[:(size + 5) / 2] + " ... " + item[-1*(size+5) / 2 : ] + "\n"    
    return output

#prints dictionaries in easy to read way, abstracting the format function
def print_dict(myDict):
    print dict_to_string(myDict)

    
