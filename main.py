import pandas as pd

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

# Extract month names from file paths (you can adjust parsing logic based on your filenames)
month_names = ["July", "August", "September"]

# Process each pair of files
for month, caa_file, iata_file in zip(month_names, FILE_CAA, FILE_IATA):
    # Load CAA and IATA data
    DATA_CAA = pd.read_csv(caa_file)
    DATA_IATA = pd.read_excel(iata_file)

    # Merge to find rows present in CAA but not in IATA
    merged_df_left = pd.merge(
        DATA_CAA,
        DATA_IATA.rename(columns=columns_diff),
        how="left",
        indicator=True,
        on=[
            "Call Sign", 
            "Aircraft Registration",
            "Origin ICAO Code",
            "Destination ICAO Code",
            "Aircraft Model ICAO Code"
        ],
    )
    Data_Present_CAA_Absent_IATA = merged_df_left[merged_df_left["_merge"] == "left_only"].drop(columns=["_merge"])
    columns_to_keep_caa = [col for col in DATA_CAA.columns]
    filtered_data_present_caa_absent_iata = Data_Present_CAA_Absent_IATA[columns_to_keep_caa]
    output_caa_file = f"output_present_caa_absent_iata_{month}.xlsx"
    filtered_data_present_caa_absent_iata.to_excel(output_caa_file, index=False)

    # Merge to find rows present in IATA but not in CAA
    merged_df_right = pd.merge(
        DATA_CAA,
        DATA_IATA.rename(columns=columns_diff),
        how="right",
        indicator=True,
        on=[
            "Call Sign", 
            "Aircraft Registration",
            "Origin ICAO Code",
            "Destination ICAO Code",
            "Aircraft Model ICAO Code"
        ],
    )
    Data_Present_IATA_Absent_CAA = merged_df_right[merged_df_right["_merge"] == "right_only"].drop(columns=["_merge"])
    columns_to_keep_iata = [col for col in DATA_IATA.rename(columns=columns_diff).columns]
    filtered_data_present_iata_absent_caa = Data_Present_IATA_Absent_CAA[columns_to_keep_iata]
    output_iata_file = f"output_present_iata_absent_caa_{month}.xlsx"
    filtered_data_present_iata_absent_caa.to_excel(output_iata_file, index=False)

    # Print results for the current pair
    print(f"Month: {month}")
    print(f"Rows present in CAA but absent in IATA: {filtered_data_present_caa_absent_iata.shape[0]}")
    print(f"Rows present in IATA but absent in CAA: {filtered_data_present_iata_absent_caa.shape[0]}")
    print(f"Saved files: {output_caa_file}, {output_iata_file}\n")
