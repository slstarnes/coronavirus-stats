import requests
import pandas as pd

browser_header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

population_data_url = 'http://api.geonames.org/countryInfoJSON?username=smith'

r = requests.get(population_data_url)
population_data = pd.DataFrame(r.json()['geonames'])

population_dict = (population_data[['countryName', 'population']]
                   .set_index('countryName').squeeze().to_dict())

us_population_data_url = 'https://datausa.io/api/data?drilldowns=State&measures=Population&year=latest'
r = requests.get(us_population_data_url, headers=browser_header)
us_population_data = pd.DataFrame(r.json()['data'])

us_population_dict = (us_population_data[['State', 'Population']]
                      .set_index('State').squeeze().to_dict())
