from loader import get_data, save
from rx_classes import get_rx_classes
from multiprocessing.dummy import Pool

NTHREADS = 6

def preprocess_medications(num_patients):
    for i in range(num_patients):
        print "\nPreprocessing Medications - " + str(i) + " - progress: ",
        p = get_data([i])[0]

        for (i, m) in enumerate(p['Med']):
            if i%100 == 0:
                print ", " + str(i) + '/' + str(len(p['Med'])),
            (name, rxclasses) = get_rx_classes(m['Medication'], include_name=True)
            m['RXNORM_NAME'] = name
            m['RXNORM_CLASSES'] = rxclasses

        save(p)

def preprocess_medications_parallel(patient_range):
    pool = Pool(NTHREADS)
    pool.map(preprocess, patient_range)

def preprocess(i):
    print "\nPreprocessing Medications - " + str(i)
    p = get_data([i])[0]

    for (i, m) in enumerate(p['Med']):
        (name, rxclasses) = get_rx_classes(m['Medication'], include_name=True)
        m['RXNORM_NAME'] = name
        m['RXNORM_CLASSES'] = rxclasses

    save(p)

def remove_medication_preprocessing(num_patients):
    for i in range(num_patients):
        print "Removing Medication Preprocessing - " + str(i)
        p = get_data([i])[0]

        for m in p['Med']:
            del m['RXNORM_NAME']
            del m['RXNORM_CLASSES']

        save(p)

if __name__ == "__main__":
    #preprocess_medications(1056)
    preprocess_medications_parallel(range(220,1056))
