import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Coronavirus Stats' 
server = app.server

who_data = pd.read_csv('https://covid.ourworldindata.org/data/full_data.csv')
jhu_data = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/'+
                       'COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/'+
                       'time_series_19-covid-Confirmed.csv')
t0_threshold = 100

who_data_t0 = who_data.query('total_cases >= @t0_threshold')
who_data_t0['date'] = pd.to_datetime(who_data_t0['date'])

t0_date = who_data_t0.groupby('location').min()['date']
who_data_t0.loc[:, 't0_date'] = who_data_t0['location'].map(t0_date)
who_data_t0.loc[:, 'since_t0'] = who_data_t0['date'] - who_data_t0['t0_date']
who_data_t0.loc[:, 'since_t0']  = who_data_t0['since_t0'].map(lambda x: x.days)

country_filter = ['China', 'South Korea', 'Italy', 'Iran', 'United States']
countries = list(set(who_data_t0.sort_values(by='total_cases', ascending=False)['location']))

dcc.Graph.responsive = True

x_max = min(who_data_t0[who_data_t0['location'] == 'United States']['since_t0'].max() + 14, 
            who_data_t0['since_t0'].max()) 


app.layout = html.Div([
    html.H1("Coronavirus Confirmed Cases"),
    dcc.Tabs([
        dcc.Tab(label='Line Chart', children=[
            dcc.Graph(
                id='coronavirus-t0-line',
                figure={
                    'data': [
                        dict(
                            x=who_data_t0[who_data_t0['location'] == i]['since_t0'],
                            y=who_data_t0[who_data_t0['location'] == i]['total_cases'],
                            text=who_data_t0[who_data_t0['location'] == i]['date'].map(lambda x: f'{x:%m-%d-%Y}'),
                            mode='lines',
                            opacity=0.7,
                            marker={
                                'size': 15,
                                'line': {'width': 0.5, 'color': 'white'}
                            },
                            name=i,
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
        ]),
        dcc.Tab(label='Bar Chart', children=[
            dcc.Graph(
                id='coronavirus-t0-bar',
                figure={
                    'data': [
                        dict(
                            x=who_data_t0[who_data_t0['location'] == i]['since_t0'],
                            y=who_data_t0[who_data_t0['location'] == i]['total_cases'],
                            name=i,
                            text=who_data_t0[who_data_t0['location'] == i]['date'].map(lambda x: f'{x:%m-%d-%Y}'),
                            type='bar',
                            opacity=0.7,
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
        html.P(['data source: ',
                html.A("https://ourworldindata.org/coronavirus-source-data", 
                       href="https://ourworldindata.org/coronavirus-source-data"), 
                html.Br(), 
                'code source: ',
                html.A("https://github.com/slstarnes/coronavirus-stats", 
                       href="https://github.com/slstarnes/coronavirus-stats")
                ]),
])

if __name__ == '__main__':
    app.run_server(debug=True)