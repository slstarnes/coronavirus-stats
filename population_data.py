import requests
import pandas as pd

population_data_url = 'http://api.geonames.org/countryInfoJSON?username=smith'

r = requests.get(population_data_url)
population_data = pd.DataFrame(r.json()['geonames'])

population_dict = (population_data[['countryName', 'population']]
                   .set_index('countryName').squeeze().to_dict())

