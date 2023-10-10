'''
Designed to work with Wikipedia dumps.
Extracts text from xml as well as the in-line text associated with each link, and 
saves this to a CSV. 
'''

import csv
import mwparserfromhell
from bs4 import BeautifulSoup
import os

def extract_from_xml(xml_data):
    # Parse the XML data using BeautifulSoup
    soup = BeautifulSoup(xml_data, 'lxml')
    text_tags = soup.find_all('text')
    rows = []

    # Iterate through each <text> tag and get its content
    for tag in text_tags:
        wikicode_str = tag.get_text(separator=' ', strip=True)
        wikicode = mwparserfromhell.parse(wikicode_str)
        wikicode_str = str(wikicode)
        links_list = []

        # Remove templates
        for template in wikicode.filter_templates():
            template_str = str(template)
            wikicode_str = wikicode_str.replace(template_str, '')

        # Process links
        for link in wikicode.filter_wikilinks():
            link_str = str(link)
            if link_str.lower().startswith("[[file:") or link_str.lower().startswith("[[image:") or link_str.lower().startswith("[[category:"):
                wikicode_str = wikicode_str.replace(link_str, '')
            else:
                if link.text:
                    links_list.append(link.text.strip_code())
                else:
                    links_list.append(link.title.strip_code())

        wikicode = mwparserfromhell.parse(wikicode_str)
        plain_text = wikicode.strip_code().replace('\n', ' ')
        links_str = ', '.join(links_list)

        if 3000 < len(plain_text) < 12000:
            rows.append([plain_text, links_str])
    
    print(f"Extracted {len(rows)} rows from this XML file.")
    return rows


directory = 'wiki_dumps'

# Check if directory exists
if not os.path.exists(directory):
    print(f"Directory '{directory}' does not exist.")

# Create/open a CSV file for writing
with open('data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile, delimiter='\u2063')

    # Check XML files in directory
    xml_files = [f for f in os.listdir(directory) if f.endswith('.xml')]
    if not xml_files:
        print(f"No XML files found in the '{directory}' directory.")
    
    # Process XML files
    for filename in xml_files:
        print(f"Processing {filename}...")
        with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
            xml_data = file.read()
            extracted_data = extract_from_xml(xml_data)
            
            for row in extracted_data:
                writer.writerow(row)

print("Extraction completed!")