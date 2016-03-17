import argparse
import pandas as pd

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("id", type=int)
    parser.add_argument("--features", action="store_true")
    args = parser.parse_args()

    results = pd.read_csv('/home/ubuntu/experiments/results.csv')
    row = results[results['Id'] == args.id].iloc[0]
    print row
    if args.features:
        print row['Important Features'].replace("\\n", "\n")
