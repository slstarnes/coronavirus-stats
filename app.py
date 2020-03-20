import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import requests
from dateutil.parser import parse as date_parser
from lxml import html as html_parser
import pytz

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Coronavirus Stats' 
server = app.server


def get_data_mod_date(url):
    r = requests.get(url)
    if r.status_code == 200:
        tree = html_parser.fromstring(r.content)
        t = tree.xpath('/html/body/div[4]/div/main/div[2]/div/div[3]/div[1]/span[2]/relative-time')
        d = date_parser(t[0].attrib['datetime'])
        tz = pytz.timezone('America/New_York')
        d = d.astimezone(tz)
        return f'{d:%m-%d-%Y @ %-I:%M %p %Z}'
    return


jhu_data = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/'+
                       'COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/'+
                       'time_series_19-covid-Confirmed.csv')
# this is the URL to the CSV file in GitHub so you can parse date of last commit. (the REST API required auth)
data_file_url = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv'

t0_threshold = 100
country_filter = ['China', 'South Korea', 'United States', 'Italy', 'France', 'Spain']
country_mapper = {
        'Korea, South': 'South Korea',
        'US': 'United States'    
}

jhu_data['Country/Region'] = jhu_data['Country/Region'].map(country_mapper).fillna(jhu_data['Country/Region'])
assert set(country_filter) - set(jhu_data['Country/Region']) == set()

jhu_data_reduced = jhu_data.drop(columns=['Lat', 'Long'])
jhu_data_reduced = jhu_data_reduced.groupby('Country/Region').sum()
jhu_data_reduced = jhu_data_reduced.stack().reset_index()
jhu_data_reduced.columns = ['location', 'date', 'total_cases']
jhu_data_reduced['date'] = pd.to_datetime(jhu_data_reduced['date'])

jhu_data_t0 = jhu_data_reduced.query('total_cases >= @t0_threshold')

t0_date = jhu_data_t0.groupby('location').min()['date']
jhu_data_t0.loc[:, 't0_date'] = jhu_data_t0['location'].map(t0_date)
jhu_data_t0.loc[:, 'since_t0'] = jhu_data_t0['date'] - jhu_data_t0['t0_date']
jhu_data_t0.loc[:, 'since_t0'] = jhu_data_t0['since_t0'].map(lambda x: x.days)
jhu_data_t0.loc[:, 'since_t0'] = jhu_data_t0.loc[:, 'since_t0'].where(jhu_data_t0['since_t0'] > 0, 0)

countries = list(set(jhu_data_t0.sort_values(by='total_cases', ascending=False)['location']))

dcc.Graph.responsive = True

x_max = min(jhu_data_t0[jhu_data_t0['location'] == 'United States']['since_t0'].max() + 14, 
            jhu_data_t0['since_t0'].max()) 

data_mod_date = get_data_mod_date(data_file_url)

app.layout = html.Div([
    dcc.Markdown('# Coronavirus Confirmed Cases\n'+
                 '_(based on data from Johns Hopkins\' Coronavirus Resource Center - '+
                 '[https://coronavirus.jhu.edu](https://coronavirus.jhu.edu))_'),
    dcc.Tabs([
        dcc.Tab(label='Line Chart (Log)', children=[
            dcc.Graph(
                id='coronavirus-t0-line-log',
                figure={
                    'data': [
                        dict(
                            x=jhu_data_t0[jhu_data_t0['location'] == i]['since_t0'],
                            y=jhu_data_t0[jhu_data_t0['location'] == i]['total_cases'],
                            text=jhu_data_t0[jhu_data_t0['location'] == i]['date'].map(lambda x: f'{x:%m-%d-%Y}'),
                            mode='lines',
                            opacity=1 if i == 'United States' else 0.7,
                            line={'width': 3 if i == 'United States' else 1.5},
                            name=i,
                            hovertemplate='%{text} (Day %{x})<br>'
                                          'Confirmed Cases: %{y:,.0f}<br>'
                                          
                        ) for i in country_filter
                    ],
                    'layout': dict(
                        xaxis={'title': 'Days Since Cases = 100', 'range': [0, x_max], 'zeroline': False},
                        yaxis={'type': 'log', 'title': 'Total Confirmed Cases'},
                        margin={'l': 100, 'b': 40, 't': 10, 'r': 10},
                        hovermode='compare'
                    )
                }
            ),
        ]),
        dcc.Tab(label='Line Chart (Linear)', children=[
            dcc.Graph(
                id='coronavirus-t0-line-linear',
                figure={
                    'data': [
                        dict(
                            x=jhu_data_t0[jhu_data_t0['location'] == i]['since_t0'],
                            y=jhu_data_t0[jhu_data_t0['location'] == i]['total_cases'],
                            text=jhu_data_t0[jhu_data_t0['location'] == i]['date'].map(lambda x: f'{x:%m-%d-%Y}'),
                            mode='lines',
                            opacity=1 if i == 'United States' else 0.7,
                            line={'width': 3 if i == 'United States' else 1.5},
                            name=i,
                            hovertemplate='%{text} (Day %{x})<br>'
                                          'Confirmed Cases: %{y:,.0f}<br>'

                        ) for i in country_filter
                    ],
                    'layout': dict(
                        xaxis={'title': 'Days Since Cases = 100', 'range': [0, x_max], 'zeroline': False},
                        yaxis={'type': 'linear', 'title': 'Total Confirmed Cases'},
                        margin={'l': 100, 'b': 40, 't': 10, 'r': 10},
                        hovermode='compare'
                    )
                }
            ),
        ]),
        dcc.Tab(label='Bar Chart', children=[
            dcc.Graph(
                id='coronavirus-t0-bar',
                figure={
                    'data': [
                        dict(
                            x=jhu_data_t0[jhu_data_t0['location'] == i]['since_t0'],
                            y=jhu_data_t0[jhu_data_t0['location'] == i]['total_cases'],
                            name=i,
                            text=jhu_data_t0[jhu_data_t0['location'] == i]['date'].map(lambda x: f'{x:%m-%d-%Y}'),
                            type='bar',
                            opacity=1 if i == 'United States' else 0.7,
                            hovertemplate='%{text} (Day %{x})<br>'
                                          'Confirmed Cases: %{y:,.0f}<br>'
                                          
                        ) for i in country_filter
                    ],
                    'layout': dict(
                        xaxis={'title': 'Days Since Cases = 100', 'range': [0, x_max]},
                        yaxis={'type': 'log', 'title': 'Total Confirmed Cases'},
                        margin={'l': 100, 'b': 40, 't': 10, 'r': 10},
                        hovermode='compare'
                    )
                }
            ),
        ])
    ]),
    html.P([html.I(f'data last updated on {data_mod_date}'),
            html.Br(), 
            html.B('Note: '), 'the countries shown above were selected for comparative purposes.',
            html.Br(), 
            html.B('data source: '),
            html.A("https://github.com/CSSEGISandData/COVID-19", 
                   href="https://github.com/CSSEGISandData/COVID-19"), 
            html.Br(), 
            html.B('code source: '),
            html.A("https://github.com/slstarnes/coronavirus-stats", 
                   href="https://github.com/slstarnes/coronavirus-stats")
    ]),
])

if __name__ == '__main__':
    app.run_server(debug=True)