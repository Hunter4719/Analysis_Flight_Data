import pandas as pd

DATA_CAA = pd.read_excel("docs/SomaliaAugust.csv")
# Process Somalia dataset
DATA_CAA['Flight_Date'] = pd.to_datetime(DATA_CAA['Fir Start Date']).dt.date
DATA_CAA = DATA_CAA.sort_values(['Flight_Date', 'Aircraft Registration', 'Fir Start Date'])
DATA_CAA['Flight_Number_Day'] = DATA_CAA.groupby(['Flight_Date', 'Aircraft Registration']).cumcount() + 1
DATA_CAA['New_Key'] = DATA_CAA['Flight_Date'].astype(str) + '-' + DATA_CAA['Aircraft Registration'] + '-' + DATA_CAA['Flight_Number_Day'].astype(str)

# Process IATA dataset
iata_df = pd.read_excel("docs/2024 08 08 2024 AUGUST ANC IATA BILLING (1).xlsx")
iata_df['Flight_Date'] = pd.to_datetime(iata_df['Flight Date Time']).dt.date
iata_df = iata_df.sort_values(['Flight_Date', 'Aircraft Registration No', 'Flight Date Time'])
iata_df['Flight_Number_Day'] = iata_df.groupby(['Flight_Date', 'Aircraft Registration No']).cumcount() + 1
iata_df['New_Key'] = iata_df['Flight_Date'].astype(str) + '-' + iata_df['Aircraft Registration No'] + '-' + iata_df['Flight_Number_Day'].astype(str)