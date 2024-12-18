import pandas as pd
from matplotlib_venn import venn2
import matplotlib.pyplot as plt
from datetime import timedelta

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

# Function to standardize time formats
def standardize_time(caa_time, iata_time):
    # Clean and parse NavPass Time
    caa_dt = pd.to_datetime(
        caa_time.astype(str).str.replace(' @ ', ' ', regex=False).str.strip(),
        format='%Y-%m-%d %H:%M %Z',
        errors='coerce'
    )
    
    # Clean and parse CAA Time
    iata_dt = pd.to_datetime(
        iata_time, 
        format='%m/%d/%y %I:%M %p', 
        errors='coerce'
    )
    
    # Remove timezone information to avoid Excel errors
    if caa_dt.dt.tz is not None:
        caa_dt = caa_dt.dt.tz_localize(None)
    if iata_dt.dt.tz is not None:
        iata_dt = iata_dt.dt.tz_localize(None)
    
    return caa_dt, iata_dt

# Function to check if the time difference is within 1 hour
# Function to check if the time difference is within 1 hour
def is_within_one_hour(caa_time, iata_time):
    valid_mask = caa_time.notna() & iata_time.notna()
    time_diff = (caa_time[valid_mask] - iata_time[valid_mask]).abs()
    return valid_mask & (time_diff <= timedelta(hours=1))
    
# Create a figure for subplots
fig, axes = plt.subplots(1, 3, figsize=(18, 6))  # 1 row, 3 columns

# Process each pair of files and plot Venn diagrams
for ax, month, caa_file, iata_file in zip(axes, month_names, FILE_NavPass, FILE_CAA):
    # Load NavPass and CAA data
    DATA_NavPass = pd.read_csv(caa_file)
    DATA_CAA = pd.read_excel(iata_file)

    # Standardize datetime formats for time comparison
    DATA_NavPass['Fir Started'], DATA_CAA['Entry Time'] = standardize_time(DATA_NavPass['Fir Started'], DATA_CAA['Entry Time'])
    DATA_NavPass['Fir Ended'], DATA_CAA['Exit Time'] = standardize_time(DATA_NavPass['Fir Ended'], DATA_CAA['Exit Time'])
    DATA_NavPass.to_excel('updated.xlsx', index=False)

    # Perform the merge
    merged_df = pd.merge(
        DATA_NavPass,
        DATA_CAA.rename(columns=columns_diff),
        how="outer",
        indicator=True,
        on=[
            # "Call Sign", 
            "Aircraft Registration",
            # "Origin ICAO Code",
            # "Destination ICAO Code",
            # "Aircraft Model ICAO Code"
        ],
    )

    # # Filter for time differences within 1 hour
    # time_filter = (
    #     is_within_one_hour(merged_df['Fir Started'], merged_df['Entry Time']) |
    #     is_within_one_hour(merged_df['Fir Ended'], merged_df['Exit Time'])
    # )
    # merged_df = merged_df[time_filter]

    # merged_df = merged_df[
    # (merged_df["_merge"] == "both") & (
    #     is_within_one_hour(merged_df['Fir Started'], merged_df['Entry Time']) |
    #     is_within_one_hour(merged_df['Fir Ended'], merged_df['Exit Time'])
    # )
    # ]

    # Apply the filter only for "_merge == 'both'"
    merged_df.loc[merged_df["_merge"] == "both", "time_match"] = (
        is_within_one_hour(merged_df['Fir Started'], merged_df['Entry Time']) |
        is_within_one_hour(merged_df['Fir Ended'], merged_df['Exit Time'])
    )

    # Keep "both" rows where time_match is True, and all other rows unfiltered
    merged_df = merged_df[
        (merged_df["_merge"] != "both") |  # Keep non-'both' rows
        (merged_df["time_match"] == True)  # Keep 'both' rows where time gap < 1 hour
    ]

    # Drop the temporary "time_match" column after filtering
    merged_df.drop(columns=["time_match"], inplace=True)

    # print(merged_df)

    # merged_df.to_excel("merged.xlsx", index=False)
    # Calculate counts for the Venn diagram
    only_caa_count = (merged_df["_merge"] == "left_only").sum()
    only_iata_count = (merged_df["_merge"] == "right_only").sum()
    common_count = (merged_df["_merge"] == "both").sum()

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

    ax.set_title(f"Venn Diagram - {month}")

# Adjust layout and show the figure
plt.tight_layout()
plt.show()
