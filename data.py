import pandas as pd
from constants import JHU_DATA

data = pd.read_csv(JHU_DATA)

t0_threshold = 100
country_filter = ['China', 'South Korea', 'United States', 'Italy', 'France', 'Spain']
country_mapper = {
        'Korea, South': 'South Korea',
        'US': 'United States'    
}

data['Country/Region'] = data['Country/Region'].map(country_mapper).fillna(data['Country/Region'])
assert set(country_filter) - set(data['Country/Region']) == set()

data_reduced = data.drop(columns=['Lat', 'Long'])
data_reduced = data_reduced.groupby('Country/Region').sum()
data_reduced = data_reduced.stack().reset_index()
data_reduced.columns = ['location', 'date', 'total_cases']
data_reduced['date'] = pd.to_datetime(data_reduced['date'])

data_t0 = data_reduced.query('total_cases >= @t0_threshold')

t0_date = data_t0.groupby('location').min()['date']
data_t0.loc[:, 't0_date'] = data_t0['location'].map(t0_date)
data_t0.loc[:, 'since_t0'] = data_t0['date'] - data_t0['t0_date']
data_t0.loc[:, 'since_t0'] = data_t0['since_t0'].map(lambda x: x.days)
data_t0.loc[:, 'since_t0'] = data_t0.loc[:, 'since_t0'].where(data_t0['since_t0'] > 0, 0)


def get_data():
    return data_t0
