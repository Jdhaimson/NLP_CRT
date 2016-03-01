import sys
import csv
import itertools

################################
#
# Description: adds a test to the queue
#
# example of queue:
#   python queue_test.py -mes 'This is a test' -n 500 -cv 3 -d 'from model_builder import build_model, regex_baseline' -r "build_model(regex_baseline, method = 'SVM', features_remove = ['NYHA'], features_add = {'min_ef' : (EFTransformer, {'method':'min', 'num_horizon': 2})})"
#
#  Keys    Description                                 Default                    
#   -h      displays help message                       
#   -mes    message/description                         ""
#   -n      number of patients                          900
#   -cv     number of CV splits                         5
#   -d      dependency string to be executed            "" (this dependency is only added on to default)
#   -con    control                                     regex_baseline
#   -met    method to override control                  adaboost
#   -arg*   arguments to override control model params  None
#   -a*     features to add                             None
#   -c*     features to change                          None
#   -r*     features to remove                          None
#   -g      the grid of features                        None
#
# The keys with the * indicate that the string can be formatted according to the grid. 
# For example, I could pass the following:
#   -arg "{'n_estimators' : <<N>>}" -g "{'N' : [5, 50, 500]}"
# which would mean that the model would be ran 3 times, with n_estimators replaced each time. 
#
################################



queue_file_path =  "../experiments/experiments.csv"

base_dependency = "from model_builder import build_model, regex_baseline, control_features, control_groups, struct_baseline, adaboost_baseline, lr_baseline" 

def queue_test(message = "", num_patients = 900, cv_splits = 5, build_model_string = "build_model(regex_baseline)", dependencies = "from model_builder import build_model, regex_baseline"):
    with open(queue_file_path, 'r+b') as queue_file:
        test_id = sum(1 for line in queue_file)
        writer = csv.writer(queue_file)
        writer.writerow([test_id, message, cv_splits, min(num_patients, 906), dependencies, build_model_string, '0'])

def queue_grid_search(grid = None, message = "", num_patients = 900, cv_splits = 5, dependencies = "", control_string = 'regex_baseline', method_string = 'None', model_args = 'None', features_add_string = 'None', features_change_string = 'None', features_remove_string = 'None'):

    if not grid == None: 
        args_options = build_options(grid, model_args)
        add_options = build_options(grid, features_add_string)
        change_options = build_options(grid, features_change_string)
        remove_options = build_options(grid, features_remove_string)
    else:
        args_options = [model_args]
        add_options = [features_add_string]
        change_options = [features_change_string]
        remove_options = [features_remove_string]
    results = []  
    for args in args_options:
        for add in add_options:
            for change in change_options:
                for remove in remove_options:
                    results += [make_model_string(control_string, method_string, args, add, change, remove)] 

    for model_string in results:
        queue_test(message, num_patients, cv_splits, model_string, base_dependency  + "; " + dependencies)

def make_model_string(control, method, args, add, change, remove):
    result = "build_model("
    result += "control = " + control + ", "
    if not method == 'None':
        result += "method = '" + method + "', "
    if not args == 'None':
        result += "model_args = " + args + ", "
    if not add == 'None':
        result += "features_add = " + add + ", "
    if not change == 'None':
        result += "features_change = " + change + ", "
    if not remove == 'None':
        result += "features_remove = " + remove
    result += ")"
    return result

def update_string(mapping, string):
    replace_pairs = [('{', '{{'), ('}', '}}'), ('<<', '{'), ('>>', '}')]
    for replace_pair in replace_pairs:
        string = string.replace(replace_pair[0], replace_pair[1])
    return string.format(**mapping)

def build_options(mapping, string):
    result = []
    keys = list(mapping.keys())
    relevant_keys = [key for key in keys if "<<" + key + ">>" in string]
    if len(relevant_keys) > 0:
        values = [mapping[key] for key in relevant_keys]
        combo_iterator = itertools.product(*values)
        for combo in combo_iterator:
            single_map = dict(zip(relevant_keys, combo))
            result += [update_string(single_map, string)]
        return list(set(result)) 
    else:
        return [string]

def main():
    inputs = sys.argv[1:]
    if len(inputs) == 1 and inputs[0] in ['-h', 'help']:
       show_help()
    else:  
        if len(inputs) % 2 == 1:
            raise ValueError("Uninterpretable input: " + str(inputs))

        queue_args = dict()
        args_converter = {"-con" : "control_string", "-a" : "features_add_string", "-met" : 'method_string', '-arg' : 'model_args', '-c' : 'features_change_string', "-g" : "grid", "-mes" : "message", "-n" : "num_patients", "-r" : "features_remove_string", "-cv" : "cv_splits", "-d" : "dependencies"}

        for i in range(len(inputs) / 2):
            key = inputs[2*i]
            value = inputs[2*i + 1]
            if key in args_converter:
                if key in ['-g', '-n', '-cv' ]:
                    value = eval(value) if key != '-n' else min(906, eval(value))
                queue_args[args_converter[key]] = value
            else:
                raise ValueError("Unkown key: " + key)       

        queue_grid_search(**queue_args)
def show_help():

    print "\033[95m   Keys    Description                                 Default\033[0m"                    
    print '   -mes    message/description                         ""'
    print '   -n      number of patients                          900'
    print '   -cv     number of CV splits                         5'
    print '   -d      dependency string to be executed            "" (this dependency is only added on to default)'
    print '   -con    control                                     regex_baseline'
    print '   -met    method to override control                  adaboost'
    print '   -arg*   arguments to override control model params  None'
    print '   -a*     features to add                             None'
    print '   -c*     features to change                          None'
    print '   -r*     features to remove                          None'
    print '   -g      the grid of features                        None'
    print '\033[92m   The keys with the * indicate that the string can be formatted according to the grid.'
    print '   For example, I could pass the following:'
    print '         -arg "{\'n_estimators\' : <<N>>}" -g "{\'N\' : [5, 50, 500]}"'
    print '   which would mean that the model would be ran 3 times, with n_estimators replaced each time.\033[0m' 
    print '\033[96m   You also have the following variables availible to use (they are in model_builder.py):\033[0m'
    print '   control_features      a dict of all features and their (name, class, args) tuple'
    print '   control_groups        a dict of some groups of names, which are "regex", "structured_only", "notes_tfidf", and "labs" for now'
    print '   adaboost_baseline     (for -con) baseline with no features but has adaboost with 500 weak learners'
    print '   struct_baseline       (for -con) baseline with Enc, Sex, lab_values, ICD9, has adaboost with 200 weak learners'
    print '   lr_baseline           (for -con) baseline with no features but has logisitic regression'
    print '   regex_baseline        (for -con) adaboost_baseline with control_groups["regex"] loaded'
    print '\033[96m   Use these in combintion with grid to easily gain control over our experiments:\033[96m'
    print '   Run control, without regex features, without notes: -r "<<G>>" -g "{\'G\' : [\'None\', \'control_groups[\\"regex\\"]\', \'control_groups[\\"notes_tfidf\\"]\']}"'
    print '   Run with regex added in, labs added in: -a "[control_features[x] for x in control_groups[\'<<G>>\']]" -g "{\'G\' : [\'regex\', \'labs\']}"'
    print '  \033[92m See model_builder.py for more information about these structures and how to handle FeaturePipeline changes'
    print '\033[0m'
if __name__ == '__main__':
    main()
