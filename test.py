from loader import * 

data = get_data()
clean_data(data)

num = -1
while num < 0 or num >= len(data.keys()):
    num = int(raw_input("Select a patient number from 0 - " + str(len(data.keys())-1) + ": "))
patient = data[data.keys()[num]]
explore(patient)
