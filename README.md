# WEF-GCI-MostProblematicFactors-PDFscrape
Scrapes WEF GCI Most Problematic Factors data from country PDFs on the WEF site

**Inputs:**
- countryISO3.csv -- contains mapping of scraped Country names against actual Country ISO3 codes in TCdata360 API
- mapping.csv -- contains mapping of scraped Indicator names against actual Indicator names in TCdata360 API
- URL of WEF GCI downloads page where the country PDFs are located

**Output:** CSV file with scraped data.
- CSV file has 4 columns:
  - Indicator = Indicator name based on TCdata360 API
  - 2017 = Value of the indicator for the specified country for the year 2017
  - Country ISO3 = Country ISO3 code based on TCdata360 API
  - id = indicator ID based on TCdata360 API
- sample output file as of Dec. 21, 2017: `2017-12-22-WEF GCI Most Problematic Factors 2017`
