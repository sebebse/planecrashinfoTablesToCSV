import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os

year = 1920
# Fetch the webpage
for i in range(5):
    
    r = requests.get('https://planecrashinfo.com/'+str(year)+'/'+str(year)+'.htm')
    soup = BeautifulSoup(r.text, 'html.parser')

    # Extract table headers
    table = soup.find_all("table")[0]  # Select the first table
    header = table.find("tr")
    list_header = [item.get_text(strip=True) for item in header.find_all("td")]

    # Extract table rows
    data = []
    rows = table.find_all("tr")[1:]  # Skip the header row

    for row in rows:
        cells = row.find_all("td")
        row_data = []
        for cell in cells:
            # Unwrap <font> tag to remove font styling but keep content
            for tag in cell.find_all(["font", "a"]):
                tag.unwrap()

            cell_content = cell.decode_contents()  # Keeps <br> tags intact
            row_data.append(cell_content)
        
        # Ensure row matches the header length
        if len(row_data) == len(list_header):
            data.append(row_data)

    # Create DataFrame and save to csv
    dataFrame = pd.DataFrame(data=data, columns=list_header)
    dataFrame.to_csv('psd.csv', index=False)

    # Load the CSV file
    dataFrame = pd.read_csv('psd.csv')
    dataFrame['Location / Operator'] = dataFrame['Location / Operator'].str.replace(r'Near', '', regex=True)
    dataFrame['Location / Operator'] = dataFrame['Location / Operator'].str.replace(r'Over', '', regex=True)
    dataFrame['Location / Operator'] = dataFrame['Location / Operator'].str.replace(r'Off', '', regex=True)
    #dataFrame['Location / Operator'] = dataFrame['Location / Operator'].str.replace(r'USSR', 'Russia', regex=True)

    # Target the 2nd and 3rd columns
    columns_to_modify = [1, 2]
    for col in columns_to_modify:
        dataFrame.iloc[:, col] = dataFrame.iloc[:, col].apply(lambda x: str(x).split('<br>')[0])
        dataFrame.iloc[:, col] = dataFrame.iloc[:, col].apply(lambda x: str(x).split('<br/>')[0])
        # Sometimes Mr. Kebabjian uses <br> and other times </br>
    # Use regex to extract the three numbers from the fatalities column
    dataFrame[['Passenger count', 'Passenger deaths', 'Ground deaths']] = dataFrame['Fatalities'].str.extract(r'(\d+)/(\d+)\((\d+)\)', expand=True)

    # Save the modified DataFrame to a new CSV
    dataFrame = dataFrame.drop(columns=['Fatalities'])
    dataFrame.to_csv(str(year)+'_psd.csv', index=False)

    print(str(year)+" CSV file has been created successfully.")
    year += 1
os.remove('psd.csv')