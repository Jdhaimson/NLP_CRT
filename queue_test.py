import sys
import csv

################################
#
# Description: adds a test to the queue
#
# example:
#   python -m 'This is a test' -n 500 -cv 3 -d 'from model_builder import build_model, regex_baseline' -r "build_model(regex_baseline, method = 'SVM', features_remove = ['NYHA'], features_add = {'min_ef' : (EFTransformer, {'method' = 'min', 'num_horizon' = 2})})"
#
# Keys:
#   -m      message/description
#   -n      number of patients
#   -cv     number of CV splits
#   -d      dependency string to be executed
#   -r      model string to be executed
#
# Defaults:
#   -m      ""
#   -n      25
#   -cv     3
#   -d      "from model_builder import build_model, regex_baseline"
#   -r      "build_model(regex_baseline)"
#
################################



queue_file_path =  "../experiments/experiments.csv"

def queue_test(message = "", num_patients = 25, cv_splits = 3, build_model_string = "build_model(regex_baseline)", dependencies = "from model_builder import build_model, regex_baseline"):
    with open(queue_file_path, 'r+b') as queue_file:
        test_id = sum(1 for line in queue_file)
        writer = csv.writer(queue_file)
        writer.writerow([test_id, message, cv_splits, num_patients, dependencies, build_model_string, '0'])

def main():
    inputs = sys.argv[1:]
    if len(inputs) % 2 == 1:
        raise ValueError("Uninterpretable input: " + str(inputs))

    queue_args = dict()
    args_converter = {"-m" : "message", "-n" : "num_patients", "-cv" : "cv_splits", "-r" : "build_model_string", "-d" : "dependencies"}

    for i in range(len(inputs) / 2):
        key = inputs[2*i]
        value = inputs[2*i + 1]
        if key in args_converter:
            if key in ['-n', '-cv']:
                value = int(value)
            queue_args[args_converter[key]] = value
        else:
            raise ValueError("Unkown key: " + key)       

    queue_test(**queue_args)



if __name__ == '__main__':
    main()
