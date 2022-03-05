""" 
Helps clean the raw music dataset collected
"""

import pandas as pd

# RAW_DATA_PATH = "./data/test_raw.csv"
# CLEAN_DATA_PATH = "./data/test_cleaned.csv"
RAW_DATA_PATH = "./data/raw_dataset.csv"
CLEAN_DATA_PATH = "./data/cleaned_dataset.csv"
raw_dataset = pd.read_csv(RAW_DATA_PATH)

def clean(raw_dataset: pd.DataFrame):
    # add headers
    headers = ["Artist", "Album", "Title", "Date"]
    raw_dataset.to_csv(CLEAN_DATA_PATH, header=headers, index=False)
    return pd.read_csv(CLEAN_DATA_PATH)

def print_summary(dataset: pd.DataFrame):
    for (columnName, columnData) in dataset.iteritems():
        print(f"========={columnName}==========\n{set(columnData)}")


def main():
    # create the clean dataset
    clean_dataset = clean(raw_dataset)

    # print the summary
    print_summary(clean_dataset)


if __name__ == "__main__":
    main()