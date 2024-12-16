import pandas as pd
from matplotlib_venn import venn2
import matplotlib.pyplot as plt

# Define file paths for CAA and IATA data
FILE_CAA = ["docs/SomaliaJuly2024.csv", "docs/SomaliaAugust.csv", "docs/SomaliaSeptember.csv"]
FILE_IATA = [
    "docs/2024 08 07 2024 JULY ANC IATA BILLING.xlsx", 
    "docs/2024 08 08 2024 AUGUST ANC IATA BILLING (1).xlsx", 
    "docs/ANC 2024 SEPTEMBER ANC BILLING.xlsx"
]

# Column mapping for IATA data
columns_diff = {
    "CallSign Flight No": "Call Sign",
    "Aircraft Registration No": "Aircraft Registration",
    "From Airport Code ICAO": "Origin ICAO Code",
    "To Airport Code ICAO": "Destination ICAO Code",
    "Aircraft Type Code ICAO": "Aircraft Model ICAO Code"
}

# Month names for titles
month_names = ["July", "August", "September"]

# Create a figure for subplots
fig, axes = plt.subplots(1, 3, figsize=(18, 6))  # 1 row, 3 columns

# Process each pair of files and plot Venn diagrams
for ax, month, caa_file, iata_file in zip(axes, month_names, FILE_CAA, FILE_IATA):
    # Load CAA and IATA data
    DATA_CAA = pd.read_csv(caa_file)
    DATA_IATA = pd.read_excel(iata_file)

    # Perform the merge
    merged_df = pd.merge(
        DATA_CAA,
        DATA_IATA.rename(columns=columns_diff),
        how="outer",
        indicator=True,
        on=[
            "Call Sign", 
            "Aircraft Registration",
            "Origin ICAO Code",
            "Destination ICAO Code",
            "Aircraft Model ICAO Code"
        ],
    )

    # Calculate counts for the Venn diagram
    only_caa_count = (merged_df["_merge"] == "left_only").sum()
    only_iata_count = (merged_df["_merge"] == "right_only").sum()
    common_count = (merged_df["_merge"] == "both").sum()

    # Plot the Venn diagram for the current month
    venn = venn2(
        subsets=(only_caa_count, only_iata_count, common_count),
        set_labels=(f"CAA ({month})", f"IATA ({month})"),
        ax=ax
    )
    ax.set_title(f"Venn Diagram - {month}")

# Adjust layout and show the figure
plt.tight_layout()
plt.show()
