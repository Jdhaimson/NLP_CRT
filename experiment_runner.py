import logging
import sys
import time

from daemon import runner
import pandas as pd


class ExperimentRunner():

    def __init__(self):
        base = '/home/ubuntu/experiments/'
        self.experiments_file = base + 'experiments.csv'
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
        exec(experiment['Dependencies'])
        pipeline = eval(experiment['Model'])

        logger.info(str(pipeline))

        # Mark experiment as run
        experiments.loc[idx, 'Run?'] = 1
        experiments.to_csv(self.experiments_file, index=False)

    def run(self):
        while True:
            success = self.do_next_experiment()
            if not success:
                logger.info("No experiments to run, waiting for more")
                time.sleep(5)


if __name__ == "__main__":
    # Configure Logger
    logger = logging.getLogger("DaemonLog")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = logging.FileHandler("/home/ubuntu/experiments/runner.log")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Configure app to run as daemon
    exp_runner = ExperimentRunner()
    daemon_runner = runner.DaemonRunner(exp_runner)
    daemon_runner.daemon_context.files_preserve=[handler.stream]
    daemon_runner.do_action()
