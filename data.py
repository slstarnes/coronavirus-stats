import pandas as pd
import numpy as np
from constants import JHU_DATA
from population_data import population_dict, us_population_dict

data = pd.read_csv(JHU_DATA)

t0_threshold = 100
country_filter = ['China', 'South Korea', 'United States', 'Italy', 'France', 'Spain']
country_mapper = {
        'Korea, South': 'South Korea',
        'US': 'United States'    
}
state_filter = ['New York', 'Washington', 'Ohio', 'Georgia']


def _drop_cities(place):
    if place is None or place is np.nan:
        return None
    if place.find(',') > 0:
        return None
    else:
        return place


def data_processing(df, pop_dict, t0_threshold=100,
                    population_group_size=100_000, states_data=False):
    loc = 'location' if not states_data else 'state'
    df['Country/Region'] = df['Country/Region'].map(country_mapper).fillna(df['Country/Region'])
    if states_data:
        df = df[df['Country/Region'] == 'United States']
        df['Province/State'] = df['Province/State'].map(_drop_cities).dropna()
        df = df.drop(columns=['Lat', 'Long', 'Country/Region'])
        df = df.groupby('Province/State').max()
    else:
        df = df.drop(columns=['Lat', 'Long', 'Province/State'])
        df = df.groupby('Country/Region').max()
    df = df.stack().reset_index()
    df.columns = [loc, 'date', 'total']
    df['date'] = pd.to_datetime(df['date'])
    df['population'] = df[loc].map(pop_dict).fillna(1).astype(int)
    df['per_100k'] = (df['total'].fillna(0).astype(int)
                      .div(df['population']).mul(population_group_size))
    df = df.query('total >= @t0_threshold')
    t0_date = df.groupby(loc).min()['date']
    df.loc[:, 't0_date'] = pd.to_datetime(df[loc].map(t0_date))
    df.loc[:, 'since_t0'] = df['date'] - df['t0_date']
    df.loc[:, 'since_t0'] = df['since_t0'].map(lambda x: x.days)
    df.loc[:, 'since_t0'] = df.loc[:, 'since_t0'].where(df['since_t0'] > 0, 0)
    return df


data_t0 = data_processing(data, population_dict,
                          t0_threshold=100)
data_us_t0 = data_processing(data, us_population_dict,
                             t0_threshold=1, states_data=True)


def get_data(data_set='country'):
    if data_set == 'country':
        # data_t0.to_csv('data_t0_2.csv')
        return data_t0
    elif data_set == 'state':
        # data_us_t0.to_csv('data_us_t0_2.csv')
        return data_us_t0
