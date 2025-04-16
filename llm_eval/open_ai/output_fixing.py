import pandas as pd
'''
This is a file used to fix the flag reading from the raw output from open ai response
Sometimes the original function cannot correctly parse the responses, resulting -1 flag.
'''

# First, let's define the conversion function similar to the one in openAI_ME_2_CSV.py
def fix_openAI_ME_response(response_str):
    """Convert a single OpenAI ME response string to boolean value (0 or 1)"""
    try:
        # Convert string to dictionary if it's a string
        if isinstance(response_str, str):
            response_dict = eval(response_str)
        else:
            response_dict = response_str
            
        # Extract flagged value
        flagged = response_dict.get("results", [{}])[0].get("flagged", False)
        return 1 if flagged else 0
    except Exception as e:
        print(f"Error processing response: {e}")
        return 0  # Default to 0 if we can't process it

# Read the original CSV
df = pd.read_csv('movieTV_25-02-22_OpenAI_omni-moderation-2024-09-26.csv')

# Create a mask for rows where OpenAI_ME_bool_Feb is -1
mask_neg_one = df['OpenAI_ME_bool_Feb'] == -1

# Print number of rows to fix
print(f"Number of rows to fix: {mask_neg_one.sum()}")

# Fix the -1 values by processing OpenAI_ME_responses for those rows
df.loc[mask_neg_one, 'OpenAI_ME_bool_Feb'] = df[mask_neg_one]['OpenAI_ME_responses'].apply(fix_openAI_ME_response)

# Print the new value counts to verify the fix
print("\nNew value counts for OpenAI_ME_bool_Feb:")
print(df['OpenAI_ME_bool_Feb'].value_counts())

# Save the corrected DataFrame to a new CSV
output_path = 'movieTV_25-02-22_OpenAI_omni-moderation-2024-09-26_fixed.csv'
df.to_csv(output_path, index=False)

print(f"\nCorrected CSV saved to: {output_path}")