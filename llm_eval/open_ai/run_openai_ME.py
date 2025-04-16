""""
Description: A program to use the wikipedia API to gather TV and movie data
Author:
Date:
Created for use in the GPT benchmark suite, more information here:
"""

# Imports:
import pandas as pd
from openai import OpenAI
import openai, optparse, sys, time
from datetime import date
import json
from tqdm import tqdm

"""
API Key
"""
with open("OpenAI_ME/config.json", "r") as config_file:
    config = json.load(config_file)

KEY = config["API_KEY_2"]

client = OpenAI(
    api_key=KEY
)

"""
Reading in Data
"""


def main():
    opts = parse_args()
    col_name = opts.col_name
    try:
        dataset = pd.read_csv(opts.dataset_filename)
    except:  # TODO - make this more specific
        print("Dataset not found")
        return

    dataset.dropna(subset=[col_name], inplace=True)
    # Run the ME on the provided column
    print("Running ME on dataset...")
    output_col = str(col_name) + "_ME_response"
    ME_response = run_me_caller(dataset, col_name)
    dataset[output_col] = pd.Series(ME_response)
    print("ME run complete!")

    dataset.to_csv('test_dataset_ME_response.csv', index=True)


def parse_args():
    """Parse command line arguments."""
    parser = optparse.OptionParser(description='run moderation endpoint script')

    parser.add_option('-d', '--dataset_filename', type='string', help='path to' + \
                                                                      ' dataset file (CSV format)')
    parser.add_option('-c', '--col_name', type='string', help='name of' + \
                                                              ' column in dataset to run ME on')

    (opts, args) = parser.parse_args()

    mandatories = ['dataset_filename', ]
    for m in mandatories:
        if not opts.__dict__[m]:
            print('mandatory option ' + m + ' is missing\n')
            parser.print_help()
            sys.exit()

    return opts


# code cite
# https://community.openai.com/t/moderations-create-how-to-save-and-parse-output/530068/2

def process(data):
    if isinstance(data, dict):
        sorted_data = {k: process(v) for k, v in sorted(data.items())}
        return {k: format_floats(v) for k, v in sorted_data.items()}
    elif isinstance(data, list):
        return [process(item) for item in data]
    else:
        return data


def format_floats(data):
    if isinstance(data, float):
        # Format floats to 10 decimal places as strings
        return f"{data:.10f}"
    else:
        return data


def me_caller_simple(input_text, sleep_time=0.5, retry=5):
    try:
        api_response = client.moderations.create(model="omni-moderation-latest", input=input_text)
        response_dict = api_response.model_dump()
        formatted_dict = process(response_dict)
    except Exception as e:
        time.sleep(sleep_time)
        return me_caller_simple(input_text, sleep_time=sleep_time + 0.5,
                                retry=retry - 1) if retry > 0 else f"API error {e}"

    return formatted_dict


""" 
A helper function to run the ME caller on each entry in a dataframe column 
Input: df: a dataframe containing text to send into the ME, col: the column to query
"""


from tqdm import tqdm
from datetime import date

def run_me_caller(df, col, start_index=0):
    """Calls OpenAI moderation API on a DataFrame column, tracking correct row indices."""
    response_list = []
    repeats = 1

    try:
        for i in tqdm(range(len(df))):  # Iterate over batch indices, not full dataset
            if df.iloc[i][col] != "":
                response = me_caller_simple(df.iloc[i][col])  # API call
                response_list.append(response)
                print(response)
            else:
                response_list.append("NoInput")
            # print(f"Processed row {start_index + i + 1}")  # Track the full dataset index

    except TypeError as te:
        print(f"TypeError: {te}")

    model = "omni-moderation-latest"  # Update this if model changes
    return response_list, [(date.today(), model)] * len(response_list)


if __name__ == "__main__":
    main()