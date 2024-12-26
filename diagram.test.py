import pandas as pd
from matplotlib_venn import venn2
import matplotlib.pyplot as plt
from datetime import timedelta
import numpy as np  # For calculating the average
from rapidfuzz import process, fuzz

# Define file paths for NavPass and CAA data
FILE_NavPass = ["docs/SomaliaJuly2024.csv", "docs/SomaliaAugust.csv", "docs/SomaliaSeptember.csv"]
FILE_CAA = [
    "docs/2024 08 07 2024 JULY ANC IATA BILLING.xlsx", 
    "docs/2024 08 08 2024 AUGUST ANC IATA BILLING (1).xlsx", 
    "docs/ANC 2024 SEPTEMBER ANC BILLING.xlsx"
]

# Column mapping for CAA data
columns_diff = {
    "CallSign Flight No": "Call Sign",
    "Aircraft Registration No": "Aircraft Registration",
    "From Airport Code ICAO": "Origin ICAO Code",
    "To Airport Code ICAO": "Destination ICAO Code",
    "Aircraft Type Code ICAO": "Aircraft Model ICAO Code"
}

# Month names for titles
month_names = ["July", "August", "September"]
# month_names = ["August"]

# Function to check if the time difference is within 1 hour
def is_within_one_hour(caa_time, iata_time):
    valid_mask = caa_time.notna() & iata_time.notna()
    time_diff = (caa_time[valid_mask] - iata_time[valid_mask]).abs()
    return valid_mask & (time_diff <= timedelta(hours=1))
    
# Create a figure for subplots
fig, axes = plt.subplots(1, 3, figsize=(18, 6))  # 1 row, 3 columns
# Define a function to map fuzzy matches
def fuzzy_match_operator_names_with_ratios(caa_names, navpass_names, threshold=20):
    """
    Matches NavPass operator names to the closest CAA operator names based on fuzzy similarity.
    Args:
        caa_names (pd.Series): List of operator names from CAA dataset.
        navpass_names (pd.Series): List of operator names from NavPass dataset.
        threshold (int): Minimum similarity score to consider a match.
    Returns:
        dict: Mapping of NavPass operator names to the closest CAA operator names.
    """
    mapping = {}
    match_ratios = []
    caa_unique_names = caa_names.dropna().unique()
    for nav_name in navpass_names.dropna().unique():
        match = process.extractOne(nav_name, caa_unique_names, scorer=fuzz.ratio)
        if match and match[1] >= threshold:  # Check if a match is found and meets the threshold
            mapping[nav_name] = match[0]  # `match[0]` contains the best match
            match_ratios.append(match[1])  # Store the match ratio
    return mapping, match_ratios


# Process each pair of files and plot Venn diagrams
for ax, month, navpass_file, caa_file in zip(axes, month_names, FILE_NavPass, FILE_CAA):
    # Load NavPass and CAA data
    DATA_NavPass = pd.read_csv(navpass_file)
    DATA_CAA = pd.read_excel(caa_file)

    DATA_CAA['Flight_Date'] = pd.to_datetime(DATA_CAA['Flight Date Time']).dt.date
    DATA_CAA = DATA_CAA.sort_values(['Flight_Date', 'Aircraft Registration No', 'Flight Date Time'])
    DATA_CAA['Flight_Number_Day'] = DATA_CAA.groupby(['Flight_Date', 'Aircraft Registration No']).cumcount() + 1
    DATA_CAA['New_Key'] = DATA_CAA['Flight_Date'].astype(str) + '-' + DATA_CAA['Aircraft Registration No'].astype(str) + '-' + DATA_CAA['Flight_Number_Day'].astype(str)

    DATA_CAA.to_excel(f'Updated CAA Data - {month}.xlsx')
    
    DATA_NavPass.rename(
        columns={
            "Aircraft Model ICAO Code": "Aircraft Type Code ICAO",
            "Operator": "Operator Name"
        },
        inplace=True)

    DATA_NavPass['Flight_Date'] = pd.to_datetime(DATA_NavPass['Fir Start Date']).dt.date
    DATA_NavPass = DATA_NavPass.sort_values(['Flight_Date', 'Aircraft Registration', 'Fir Start Date'])
    DATA_NavPass['Flight_Number_Day'] = DATA_NavPass.groupby(['Flight_Date', 'Aircraft Registration']).cumcount() + 1
    DATA_NavPass['New_Key'] = DATA_NavPass['Flight_Date'].astype(str) + '-' + DATA_NavPass['Aircraft Registration'].astype(str) + '-' + DATA_NavPass['Flight_Number_Day'].astype(str)
    
    DATA_NavPass.to_excel(f'Updated NavPass Data - {month}.xlsx')

    # Apply fuzzy matching and calculate match ratios
    operator_mapping, match_ratios = fuzzy_match_operator_names_with_ratios(
        DATA_CAA['Operator Name'], 
        DATA_NavPass['Operator Name']
    )
    
    # Replace operator names in NavPass with the closest match from CAA
    DATA_NavPass['Operator Name'] = DATA_NavPass['Operator Name'].map(operator_mapping).fillna(DATA_NavPass['Operator Name'])
    # Calculate the average match ratio
    average_match_ratio = np.mean(match_ratios)

    # Merge the two DataFrames on the 'New_Key' column
    merged_data = pd.merge(
        DATA_CAA, 
        DATA_NavPass,
        on=[
            'New_Key',
            'Aircraft Type Code ICAO',
            'Operator Name'
            ],
        how='outer',
        indicator=True
    )  # Use 'inner' or 'outer' depending on your needs

    print(merged_data)
    # Optionally, save the merged DataFrame to an Excel file
    merged_data.to_excel(f'Merged Data - {month}.xlsx', index=False)

    # Calculate counts for the Venn diagram
    only_caa_count = (merged_data["_merge"] == "left_only").sum()
    only_iata_count = (merged_data["_merge"] == "right_only").sum()
    common_count = (merged_data["_merge"] == "both").sum()

    # Calculate total for percentages
    total_count = only_caa_count + only_iata_count + common_count

    # Calculate percentages
    only_caa_percentage = (only_caa_count / total_count) * 100
    only_iata_percentage = (only_iata_count / total_count) * 100
    common_percentage = (common_count / total_count) * 100
    
    # Plot the Venn diagram for the current month
    venn = venn2(
        subsets=(only_caa_count, only_iata_count, common_count),
        set_labels=("NavPass", "CAA"),
        ax=ax
    )
    venn.get_label_by_id('10').set_text(f"{only_caa_count}\n({only_caa_percentage:.1f}%)")
    venn.get_label_by_id('01').set_text(f"{only_iata_count}\n({only_iata_percentage:.1f}%)")
    venn.get_label_by_id('11').set_text(f"{common_count}\n({common_percentage:.1f}%)")

    # Annotate the fuzzy match ratio in the plot
    ax.annotate(
        f"Avg. Fuzzy Match Ratio: {average_match_ratio:.1f}%", 
        xy=(0.5, -0.1), 
        xycoords='axes fraction',
        ha='center',
        fontsize=10,
        color='blue'
    )
    
    # ax.set_title(f"Venn Diagram - {month} (Avg. Match: {average_match_ratio:.1f}%)")

# # Adjust layout and show the figure
plt.tight_layout()
plt.show()
