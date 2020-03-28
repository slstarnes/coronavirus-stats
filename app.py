import dash
import dash_core_components as dcc
import dash_html_components as html
from plotly.subplots import make_subplots
from data import get_data, country_filter, state_filter
from constants import (PLOT_LOOKAHEAD, JHU_DATA_FILE_URL, JHU_DEATH_DATA_FILE_URL,
                       NYT_STATE_DATA_FILE_URL, TRACE_COLORS,
                       COUNTRY_T0_CASES_THRESHOLD, CASES_PER_CAPITA_VALUE,
                       DEATHS_PER_CAPITA_VALUE)
from data_mod_date import get_data_mod_date
from population_data import population_dict, us_population_dict
from utilities import human_format


dcc.Graph.responsive = True
data = get_data('country')
data_us = get_data('state')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Coronavirus Stats'
server = app.server

data_mod_date_country = get_data_mod_date(JHU_DATA_FILE_URL)
data_mod_date_country_deaths = get_data_mod_date(JHU_DEATH_DATA_FILE_URL)

country_time_delta = (get_data_mod_date(JHU_DATA_FILE_URL, datetime=True) -
                      get_data_mod_date(JHU_DEATH_DATA_FILE_URL, datetime=True)).total_seconds()
country_same_time = country_time_delta < 20 * 60  # 20 minutes

data_mod_date_state = get_data_mod_date(NYT_STATE_DATA_FILE_URL)

data_updated_str = 'data last updated on '
if country_same_time:
    data_updated_str += f'{data_mod_date_country} [country data] & '
else:
    data_updated_str += f'{data_mod_date_country} [country cases] & ' \
                        f'{data_mod_date_country_deaths} [country deaths] & '
data_updated_str += f'{data_mod_date_state} [state data]'

x_max = min(data[data['location'] == 'United States']['since_t0'].max() + PLOT_LOOKAHEAD,
            data['since_t0'].max())

countries = data.groupby('location').max()['total'].sort_values(ascending=False).keys().values
states = data_us.groupby('state').max()['total'].sort_values(ascending=False).keys().values

app.layout = html.Div([
    dcc.Markdown('# Coronavirus Confirmed Cases\n' +
                 '_(based on data from Johns Hopkins\' Coronavirus Resource Center - ' +
                 '[https://coronavirus.jhu.edu](https://coronavirus.jhu.edu))_ and ' +
                 'the NY Times'),
    html.P([
        html.I(data_updated_str),
        html.Br(),
    ]),
    html.P([
        '| ',
        html.A('Cases by Country', href='#country-line'),
        ' | ',
        html.A('Deaths by Country', href='#country-deaths'),
        ' | ',
        html.A('Cases by State', href='#state-line'),
        ' |',
    ], style={'textAlign': 'center', 'fontSize': 18}),
    html.Hr(),
    html.A(id='country-line'),
    html.H3(f'Confirmed Cases of COVID-19 by Country Since Reaching {COUNTRY_T0_CASES_THRESHOLD} Cases',
            style={
                'textAlign': 'center'
            }),
    html.Div([
        html.Div(
            dcc.Dropdown(
                id="CountrySelector1",
                options=[{
                    'label': i,
                    'value': i
                } for i in countries],
                multi=True,
                value=country_filter),
            style={'width': '50%',
                   'display': 'inline-block'}),
        html.Div(
            dcc.RadioItems(
                id="PerCapitaSelector1",
                options=[
                    {'label': 'Raw', 'value': 'total'},
                    {'label': f'By Population (per {human_format(CASES_PER_CAPITA_VALUE)})',
                     'value': 'per_capita'}
                ],
                value='total',
                labelStyle={'display': 'inline-block'}),
            style={
                   'float': 'right',
                   'margin-right': '10%',
                   'display': 'inline-block'}),
        html.Div(
            dcc.RadioItems(
                id="LogSelector1",
                options=[
                    {'label': 'Log Scale', 'value': 'log'},
                    {'label': 'Linear Scale', 'value': 'linear'}
                ],
                value='log',
                labelStyle={'display': 'inline-block',
                            'horizontal-align': 'right'}),
            style={
                   'float': 'right',
                   'margin-right': '10%',
                   'display': 'inline-block'})
        ],
        style={'width': '100%',
               'display': 'inline-block'}),
    html.Div([
        dcc.Graph(id='case-line-graph',
                  style={'display': 'inline-block',
                         'height': '70vh',
                         'width': '100%'}),
    ], style={'width': '95%', 'float': 'center', 'display': 'inline-block'}),
    html.Hr(),
    html.A(id='country-deaths'),
    html.H3(f'Deaths due to COVID-19 by Country Since Reaching {COUNTRY_T0_CASES_THRESHOLD} Cases',
            style={
                'textAlign': 'center'
            }),
    html.Div([
        html.Div(
            dcc.Dropdown(
                id="CountrySelector2",
                options=[{
                    'label': i,
                    'value': i
                } for i in countries],
                multi=True,
                value=country_filter),
            style={'width': '50%',
                   'display': 'inline-block'}),
        html.Div(
            dcc.RadioItems(
                id="PerCapitaSelector2",
                options=[
                    {'label': 'Raw', 'value': 'total'},
                    {'label': f'By Population (per {human_format(DEATHS_PER_CAPITA_VALUE)})',
                     'value': 'per_capita'}
                ],
                value='total',
                labelStyle={'display': 'inline-block'}),
            style={
                   'float': 'right',
                   'margin-right': '10%',
                   'display': 'inline-block'}),
        html.Div(
            dcc.RadioItems(
                id="LogSelector2",
                options=[
                    {'label': 'Log Scale', 'value': 'log'},
                    {'label': 'Linear Scale', 'value': 'linear'}
                ],
                value='log',
                labelStyle={'display': 'inline-block',
                            'horizontal-align': 'right'}),
            style={
                'float': 'right',
                'margin-right': '10%',
                'display': 'inline-block'})
    ],
        style={'width': '100%',
               'display': 'inline-block'}),

    html.Div([
        dcc.Graph(id='country-death-graph',
                  style={'display': 'inline-block',
                         'height': '70vh',
                         'width': '100%'}),
    ], style={'width': '95%', 'float': 'center', 'display': 'inline-block'}),
    html.Hr(),
    html.A(id='state-line'),
    html.H3('Confirmed Cases of COVID-19 by State',
            style={
                'textAlign': 'center'
            }),
    html.Div([
        html.Div(
            dcc.Dropdown(
                id="StateSelector",
                options=[{
                    'label': i,
                    'value': i
                } for i in states],
                multi=True,
                value=state_filter),
            style={'width': '50%',
                   'display': 'inline-block'}),
        html.Div(
            dcc.RadioItems(
                id="StatePerCapitaSelector1",
                options=[
                    {'label': 'Raw', 'value': 'total'},
                    {'label': f'By Population (per {human_format(CASES_PER_CAPITA_VALUE)})',
                     'value': 'per_capita'}
                ],
                value='total',
                labelStyle={'display': 'inline-block'}),
            style={
                   'float': 'right',
                   'margin-right': '10%',
                   'display': 'inline-block'}),
        html.Div(
            dcc.RadioItems(
                id="LogSelector3",
                options=[
                    {'label': 'Log Scale', 'value': 'log'},
                    {'label': 'Linear Scale', 'value': 'linear'}
                ],
                value='log',
                labelStyle={'display': 'inline-block',
                            'horizontal-align': 'right'}),
            style={
                'float': 'right',
                'margin-right': '10%',
                'display': 'inline-block'})
        ],
        style={'width': '100%',
               'display': 'inline-block'}),
    html.Div([
        dcc.Graph(id='state-case-line-graph',
                  style={'display': 'inline-block',
                         'height': '70vh',
                         'width': '100%'}),
    ], style={'width': '95%', 'float': 'center', 'display': 'inline-block'}),
    html.P([html.B('data sources: '),
            html.A("https://github.com/CSSEGISandData/COVID-19",
                   href="https://github.com/CSSEGISandData/COVID-19"),
            ', ',
            html.A("https://github.com/nytimes/covid-19-data",
                   href="https://github.com/nytimes/covid-19-data"),
            html.Br(),
            html.B('code source: '),
            html.A("https://github.com/slstarnes/coronavirus-stats",
                   href="https://github.com/slstarnes/coronavirus-stats")
            ]),
])


@app.callback(
    dash.dependencies.Output('case-line-graph', 'figure'),
    [dash.dependencies.Input('CountrySelector1', 'value'),
     dash.dependencies.Input('LogSelector1', 'value'),
     dash.dependencies.Input('PerCapitaSelector1', 'value')])
def update_country_line_graph(country_selection, log_selection, per_capita_selection, df=data):
    colors = TRACE_COLORS[:len(countries)]
    fig = make_subplots(rows=1, cols=1,
                        vertical_spacing=0.08,
                        horizontal_spacing=0)
    per_x = human_format(CASES_PER_CAPITA_VALUE)
    for i, c in enumerate(country_selection):
        fig.append_trace({
            'x': df[df['location'] == c]['since_t0'],
            'y': df[df['location'] == c][per_capita_selection],
            'text': df[df['location'] == c]['date'].map(lambda x: f'{x:%m-%d-%Y}'),
            'customdata': [f'Confirmed Cases: {cases:,}<br>'
                           f'Population: {pop:,}<br>'
                           f'Cases Per {per_x}: {cpc:.2f}' for pop, cases, cpc in zip(
                                [int(population_dict.get(c, 0))] * len(df[df['location'] == c]),
                                df[df['location'] == c]['total'].astype(int).values,
                                df[df['location'] == c]['per_capita'].values)],
            'name': c,
            'mode': 'lines',
            'type': 'scatter',
            'opacity': 1 if c == 'United States' else 0.7,
            'line': {'width': 3 if c == 'United States' else 2,
                     'color': TRACE_COLORS[i]},
            'hovertemplate': '%{text} (Day %{x})<br>'
                             '%{customdata}',
            'marker_size': df[df['location'] == c]['total'],
        }, 1, 1)

    fig['layout'].update(
        showlegend=True,
        legend_title='<b> Legend <b>',
        hovermode='x',
        margin={'t': 0.1, 'b': 0.1},
        colorway=colors,
        template='plotly_white'
    )

    y_title = 'Total Confirmed Cases'
    x_title = f'Days Since Cases = {COUNTRY_T0_CASES_THRESHOLD}'
    fig.update_yaxes(title_text=y_title, showgrid=True,
                     type=log_selection, row=1, col=1)
    fig.update_xaxes(title_text=x_title, showgrid=True,
                     range=[0, x_max], row=1, col=1)

    return fig


@app.callback(
    dash.dependencies.Output('country-death-graph', 'figure'),
    [dash.dependencies.Input('CountrySelector2', 'value'),
     dash.dependencies.Input('LogSelector2', 'value'),
     dash.dependencies.Input('PerCapitaSelector2', 'value')])
def update_country_death_graph(country_selection, log_selection, per_capita_selection, df=data):
    per_capita_selection = 'deaths_' + per_capita_selection
    colors = TRACE_COLORS[:len(countries)]
    fig = make_subplots(rows=1, cols=1,
                        vertical_spacing=0.08,
                        horizontal_spacing=0)

    df = df.query('deaths_total > 0')
    per_x = human_format(DEATHS_PER_CAPITA_VALUE)
    for i, c in enumerate(country_selection):
        fig.append_trace({
            'x': df[df['location'] == c]['since_t0'],
            'y': df[df['location'] == c][per_capita_selection],
            'text': df[df['location'] == c]['date'].map(lambda x: f'{x:%m-%d-%Y}'),
            'customdata': [f'Deaths: {deaths:,}<br>'
                           f'Population: {pop:,}<br>'
                           f'Deaths Per {per_x}: {cpc:.2f}' for pop, deaths, cpc in zip(
                [int(population_dict.get(c, 0))] * len(df[df['location'] == c]),
                df[df['location'] == c]['deaths_total'].astype(int).values,
                df[df['location'] == c]['deaths_per_capita'].values)],
            'name': c,
            'mode': 'lines',
            'type': 'scatter',
            'opacity': 1 if c == 'United States' else 0.7,
            'line': {'width': 3 if c == 'United States' else 2,
                     'color': TRACE_COLORS[i]},
            'hovertemplate': '%{text} (Day %{x})<br>'
                             '%{customdata}',
            # 'marker_size': df[df['location'] == c]['total'],
        }, 1, 1)

    fig['layout'].update(
        showlegend=True,
        legend_title='<b> Legend <b>',
        hovermode='x',
        margin={'t': 0.1, 'b': 0.1},
        colorway=colors,
        template='plotly_white'
    )

    y_title = 'Total Deaths'
    x_title = f'Days Since Cases = {COUNTRY_T0_CASES_THRESHOLD}'
    fig.update_yaxes(title_text=y_title, showgrid=True,
                     type=log_selection, row=1, col=1)
    fig.update_xaxes(title_text=x_title, showgrid=True,
                     range=[0, x_max], row=1, col=1)

    return fig


@app.callback(
    dash.dependencies.Output('state-case-line-graph', 'figure'),
    [dash.dependencies.Input('StateSelector', 'value'),
     dash.dependencies.Input('LogSelector3', 'value'),
     dash.dependencies.Input('StatePerCapitaSelector1', 'value')])
def update_state_line_graph(state_selection, log_selection, per_capita_selection, df=data_us):
    colors = TRACE_COLORS[:len(states)]
    fig = make_subplots(rows=1, cols=1,
                        vertical_spacing=0.08,
                        horizontal_spacing=0)
    per_x = human_format(CASES_PER_CAPITA_VALUE)
    # filter out all values less than 2. this is to get rid of the weeks of NY having 1 case
    df = df.query('total > 1')
    for i, s in enumerate(state_selection):
        fig.append_trace({
            'x': df[df['state'] == s]['date'],
            'y': df[df['state'] == s][per_capita_selection],
            'text': df[df['state'] == s]['date'].map(lambda x: f'{x:%m-%d-%Y}'),
            'customdata': [f'Confirmed Cases: {cases:,}<br>'
                           f'Population: {pop:,}<br>'
                           f'Cases Per {per_x}: {cpc:.2f}' for pop, cases, cpc in zip(
                                [int(us_population_dict.get(s, 0))] * len(df[df['state'] == s]),
                                df[df['state'] == s]['total'].astype(int).values,
                                df[df['state'] == s]['per_capita'].values)],
            'name': s,
            'mode': 'lines',
            'type': 'scatter',
            'opacity': 1,
            'line': {'width': 2,
                     'color': TRACE_COLORS[i]},
            'hovertemplate': '%{text}<br>'
                             '%{customdata}',
        }, 1, 1)

    fig['layout'].update(
        showlegend=True,
        legend_title='<b> Legend <b>',
        hovermode='x',
        margin={'t': 0.1, 'b': 0.1},
        colorway=colors,
        template='plotly_white'
    )

    y_title = 'Total Confirmed Cases'
    x_title = 'Date'
    fig.update_yaxes(title_text=y_title, showgrid=True,
                     type=log_selection, row=1, col=1)
    fig.update_xaxes(title_text=x_title, showgrid=True,
                     row=1, col=1)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
