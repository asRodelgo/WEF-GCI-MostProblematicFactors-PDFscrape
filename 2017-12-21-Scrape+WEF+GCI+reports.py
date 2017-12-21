
# coding: utf-8

# # Import modules, define functions and dicts
import tabula
import pandas as pd
import requests
import bs4 
import numpy as np
import datetime
from urllib.request import urlopen, urlretrieve, Request
import io

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

date_today = datetime.date.today().strftime("%Y-%m-%d")

# load dictionary of Country name - Country ISO mappings
cou_dict = pd.read_csv("countryISO3.csv").set_index('Economy').to_dict()['ISO3']


# define custom function to convert PDF to text
def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp1 = urlopen(Request(path)).read()
    fp = io.BytesIO(fp1)
    
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,
                                  password=password,
                                  caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text


# # Extract list of country pdf URLs
# go to main downloads page for most recent GCI
main_download_url = 'http://reports.weforum.org/global-competitiveness-index-2017-2018/downloads/'
r = requests.get(main_download_url)
soup = bs4.BeautifulSoup(r.text, "lxml")

url_list = []
for url in soup.find_all('a', href=True):
    url_list.append(url['href'])
    
# get all country PDF links
query = "http://www3.weforum.org/docs/GCR2017-2018/03CountryProfiles/Standalone2-pagerprofiles/WEF_GCI_2017_2018_Profile_"
country_pdf_list = [url for url in url_list if query in url]

# # Iterate through each PDF and scrape 2017 GCI Most Problematic country data

# set anchor text to scrape data from
start = "Most problematic factors for doing business\n"
end = "\n\nNote: From the list of factors, respondents to the World Economic Forum's Executive Opinion Survey"

# initialize empty dataframe to consolidate
df_all = pd.DataFrame()

# iterate through each PDF URL
for cou_pdf in country_pdf_list:
    
    # extract the country name from the PDF url
    cou_name = cou_pdf.replace(query,"").replace(".pdf", "").replace("_"," ")
    
    # convert PDf to text
    df_text = convert_pdf_to_txt(cou_pdf)
    
    # extract the data from the text using the text anchors
    df_cou = pd.DataFrame([df_text[df_text.find(start)+len(start):df_text.find(end)].split("\n\n")[0].split("\n"), df_text[df_text.find(start)+len(start):df_text.find(end)].split("\n\n")[1].split("\n")]).T
    
    # data processing to add structure to dat
    df_cou.columns = ['Indicator', '2017']
    df_cou['Country ISO3'] = cou_dict[cou_name]
    
    # combine all data
    df_all = df_all.append(df_cou)


# # convert Indicator Name to correct Name and ID in TCdata360

# map all indicator names to actual names in TCdata360
ind_dict = pd.read_csv('mapping.csv').set_index('Indicator').to_dict()['name']
df_all['Indicator'] = df_all['Indicator'].replace(ind_dict)

# get indicator IDs from TCdata360 API
df_ind_metadata = pd.DataFrame(requests.get('https://tcdata360-backend.worldbank.org/api/v1/indicators/?fields=id%2Cname%2CdatasetId').json())
df_ind_metadata = df_ind_metadata[df_ind_metadata['datasetId'] == 71]
df_ind_metadata = df_ind_metadata.drop('datasetId', axis=1).reset_index(drop=True)

df_final = df_all.merge(df_ind_metadata, how='left', left_on='Indicator', right_on='name').drop(['name'], axis=1)
df_final.to_csv("%s-WEF GCI Most Problematic Factors 2017.csv" % str(date_today), index=False)