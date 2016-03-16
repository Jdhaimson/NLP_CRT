import argparse
import pandas as pd

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("id")
    args = parser.parse_args()

    result_id = int(args.id)

    results = pd.read_csv('/home/ubuntu/experiments/results.csv')
    print results[results['Id'] == result_id].iloc[0]
