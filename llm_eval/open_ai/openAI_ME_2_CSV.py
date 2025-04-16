import pandas as pd
import time
import os
from run_openai_ME import run_me_caller


def conv_openAI_ME_data(ME_responses):
    """Converts ME responses to boolean values or returns -1 if responses are invalid."""

    # Check if all responses are dictionaries
    if not all(isinstance(resp, dict) for resp in ME_responses):
        print("Warning: One or more responses are not valid dictionaries. Returning -1 for all responses.")
        return [-1] * len(ME_responses)  # Return -1 for all entries

    # Extract flagged values safely
    return [
        1 if ME_response.get("results", [{}])[0].get("flagged", False) else 0
        for ME_response in ME_responses
    ]


# File paths
input_file = "history_data/movie_TV_raw_data.csv"
output_file = "OpenAI_ME/movieTV_25-02-22_OpenAI_omni-moderation-2024-09-26.csv"

# Read the dataset
dataset = pd.read_csv(input_file)
total_rows = dataset.shape[0]
batch_size = 100

print(f"Total rows: {total_rows}")
print("Starting ME API calls...")

# Check if the output file already exists to resume from last saved batch
if os.path.exists(output_file):
    processed_df = pd.read_csv(output_file)
    start_index = len(processed_df)  # Resume from the last saved row
    print(f"Resuming from row {start_index}...")
else:
    processed_df = pd.DataFrame()
    start_index = 0

start_time = time.time()

# Process the dataset in batches
for i in range(start_index, total_rows, batch_size):
    end_index = min(i + batch_size, total_rows)  # Ensure we don't exceed dataset length
    batch = dataset.iloc[i:end_index].copy()  # Copy to avoid SettingWithCopyWarning

    print(f"Processing rows {i} to {end_index - 1}...")

    # OpenAI API call (pass correct start_index)
    OpenAI_ME_responses = run_me_caller(batch, "content", i)

    # Add responses to DataFrame
    batch["OpenAI_ME_responses"] = OpenAI_ME_responses[0]
    batch["OpenAI_ME_bool_Feb"] = conv_openAI_ME_data(OpenAI_ME_responses[0])
    batch["OpenAI_data"] = OpenAI_ME_responses[1]

    # Save incrementally (append mode)
    batch.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False)

    print(f"Saved rows {i} to {end_index - 1}.")

print(f"Total elapsed time: {time.time() - start_time:.2f} seconds")