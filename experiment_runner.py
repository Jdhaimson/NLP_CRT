import logging
import sys
import time
import csv
from daemon import runner
import pandas as pd

from model_tester import test_model, execute_test


class ExperimentRunner():

    def __init__(self):
        #base = '../experiments/'
        base = '/home/ubuntu/experiments/'
        self.experiments_file = base + 'experiments.csv'
        self.results_file = base + 'results.csv'
        self.pidfile_path = base + 'runner.pid'
        self.pidfile_timeout = 5
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'

    def do_next_experiment(self):
        experiments = pd.read_csv(self.experiments_file)
        idx = experiments.loc[experiments.loc[:,'Run?'] < 1].index.tolist()
        if len(idx) > 0:
            idx = idx[0]
            next_experiment = experiments.iloc[idx]
            self.run_experiment(next_experiment, experiments, idx)
            return True
        else:
            return False
        
    def run_experiment(self, experiment, experiments, idx):
        logger.info("Running experiment: " + str(experiment['Id']))
        try:
            exec(experiment['Dependencies'])
            pipeline = eval(experiment['Model'])

            logger.info(str(pipeline))
            results = execute_test(pipeline, experiment['Patients'], experiment['CV'])
        except Exception as e:
            logger.error("Error on the following experiment:\n" + str(experiment))
            logger.exception("Here was the stack trace:")

        # Mark experiment as run
        experiments.loc[idx, 'Run?'] = 1
        experiments.to_csv(self.experiments_file, index=False)

        #post results
        try:
            with open(self.results_file, "a") as results_file:
                writer = csv.writer(results_file)
                writer.writerow([experiment[key] for key in ['Id', 'Purpose', 'CV', 'Patients', 'Model']] + 
                                [results[key] for key in ['mode', 'precision_mean', 'precision_std', 'recall_mean',
                                                          'recall_std', 'f1_mean', 'f1_std', 'accuracy_mean',
                                                          'accuracy_std', 'important_features']
                                ])

        except Exception as e:
            logger.error(e)

    def run(self):
        waiting = False
        while True:
            success = self.do_next_experiment()
            if not success:
                if not waiting:
                    logger.info("No experiments to run, waiting for more")
                waiting = True
                time.sleep(5)
            else:
                waiting = False

if __name__ == "__main__":
    # Configure Logger
    logger = logging.getLogger("DaemonLog")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = logging.FileHandler("../experiments/runner.log")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Configure app to run as daemon
    exp_runner = ExperimentRunner()
    daemon_runner = runner.DaemonRunner(exp_runner)
    daemon_runner.daemon_context.files_preserve=[handler.stream]
    daemon_runner.do_action()
