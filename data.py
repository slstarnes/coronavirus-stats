import pandas as pd
from constants import JHU_DATA
from population_data import population_dict, us_population_dict

data = pd.read_csv(JHU_DATA)

t0_threshold = 100
country_filter = ['China', 'South Korea', 'United States', 'Italy', 'France', 'Spain']
country_mapper = {
        'Korea, South': 'South Korea',
        'US': 'United States'    
}


def _drop_cities(place):
    if place.find(',') > 0:
        return None
    else:
        return place


data['Country/Region'] = data['Country/Region'].map(country_mapper).fillna(data['Country/Region'])
assert set(country_filter) - set(data['Country/Region']) == set()

data_reduced = data.drop(columns=['Lat', 'Long'])
data_reduced = data_reduced.groupby('Country/Region').sum()
data_reduced = data_reduced.stack().reset_index()
data_reduced.columns = ['location', 'date', 'total_cases']
data_reduced['date'] = pd.to_datetime(data_reduced['date'])

data_reduced['population'] = data_reduced['location'].map(population_dict).fillna(0).astype(int)
data_reduced['cases_per_100k'] = (data_reduced['total_cases'].fillna(0).astype(int)
                                  .div(data_reduced['population']).mul(100_000))

data_t0 = data_reduced.query('total_cases >= @t0_threshold')

t0_date = data_t0.groupby('location').min()['date']
data_t0.loc[:, 't0_date'] = data_t0['location'].map(t0_date)
data_t0.loc[:, 'since_t0'] = data_t0['date'] - data_t0['t0_date']
data_t0.loc[:, 'since_t0'] = data_t0['since_t0'].map(lambda x: x.days)
data_t0.loc[:, 'since_t0'] = data_t0.loc[:, 'since_t0'].where(data_t0['since_t0'] > 0, 0)

state_filter = ['New York', 'Washington', 'Florida', 'Georgia']

data_us = data[data['Country/Region'] == 'United States']
data_us['Province/State'] = data_us['Province/State'].map(_drop_cities).dropna()
data_us_reduced = data_us.drop(columns=['Lat', 'Long', 'Country/Region'])
data_us_reduced = data_us_reduced.groupby('Province/State').max()
data_us_reduced = data_us_reduced.stack().reset_index()
data_us_reduced.columns = ['state', 'date', 'total_cases']
data_us_reduced['date'] = pd.to_datetime(data_us_reduced['date'])

data_us_reduced['population'] = data_us_reduced['state'].map(us_population_dict).fillna(0).astype(int)
data_us_reduced['cases_per_100k'] = (data_us_reduced['total_cases'].fillna(0).astype(int)
                                     .div(data_us_reduced['population']).mul(100_000))

data_us_t0 = data_us_reduced.query('total_cases >= 1')

t0_date_us = data_us_t0.groupby('state').min()['date']
data_us_t0.loc[:, 't0_date'] = data_us_t0['state'].map(t0_date_us)
data_us_t0.loc[:, 'since_t0'] = pd.to_datetime(data_us_t0['date']) - pd.to_datetime(data_us_t0['t0_date'])
data_us_t0.loc[:, 'since_t0'] = data_us_t0['since_t0'].map(lambda x: x.days)
data_us_t0.loc[:, 'since_t0'] = data_us_t0.loc[:, 'since_t0'].where(data_us_t0['since_t0'] > 0, 0)


def get_data(data_set='country'):
    if data_set == 'country':
        return data_t0
    elif data_set == 'state':
        return data_us_t0
