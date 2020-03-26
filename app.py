import dash
import dash_core_components as dcc
import dash_html_components as html
from plotly.subplots import make_subplots
from data import get_data, country_filter, state_filter
from constants import PLOT_LOOKAHEAD, JHU_DATA_FILE_URL, TRACE_COLORS
from data_mod_date import get_data_mod_date
from population_data import population_dict, us_population_dict


dcc.Graph.responsive = True
df = get_data('country')
df_us = get_data('state')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Coronavirus Stats'
server = app.server

data_mod_date = get_data_mod_date(JHU_DATA_FILE_URL)

x_max = min(df[df['location'] == 'United States']['since_t0'].max() + PLOT_LOOKAHEAD,
            df['since_t0'].max())

countries = df.groupby('location').max()['total'].sort_values(ascending=False).keys().values
states = df_us.groupby('state').max()['total'].sort_values(ascending=False).keys().values

app.layout = html.Div([
    dcc.Markdown('# Coronavirus Confirmed Cases\n' +
                 '_(based on data from Johns Hopkins\' Coronavirus Resource Center - ' +
                 '[https://coronavirus.jhu.edu](https://coronavirus.jhu.edu))_'),
    html.P([
        html.I(f'data last updated on {data_mod_date}'),
        html.Br(),
    ]),
    html.P([
        '| ',
        html.A('Country Line Plot', href='#country-line'),
        ' | ',
        html.A('Country Bar Plot', href='#country-bar'),
        ' | ',
        html.A('State Line Plot', href='#state-line'),
        ' |',
    ], style={'textAlign': 'center', 'fontSize': 18}),
    html.Hr(),
    html.A(id='country-line'),
    html.H3('Confirmed Cases of COVID-19 by Country Since Reaching 100 Cases',
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
                id="PerCapitaSelector",
                options=[
                    {'label': 'Raw', 'value': 'total'},
                    {'label': 'By Population (per 100K)', 'value': 'per_100k'}
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
    html.A(id='country-bar'),
    html.H3('Confirmed Cases of COVID-19 by Country Since Reaching 100 Cases',
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
        dcc.Graph(id='case-bar-graph',
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
                id="StatePerCapitaSelector",
                options=[
                    {'label': 'Raw', 'value': 'total'},
                    {'label': 'By Population (per 100K)', 'value': 'per_100k'}
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
    html.P([html.B('data source: '),
            html.A("https://github.com/CSSEGISandData/COVID-19",
                   href="https://github.com/CSSEGISandData/COVID-19"),
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
     dash.dependencies.Input('PerCapitaSelector', 'value')])
def update_country_line_graph(country_selection, log_selection, per_capita_selection):
    colors = TRACE_COLORS[:len(countries)]
    fig = make_subplots(rows=1, cols=1,
                        vertical_spacing=0.08,
                        horizontal_spacing=0)
    # line chart
    for i, c in enumerate(country_selection):
        fig.append_trace({
            'x': df[df['location'] == c]['since_t0'],
            'y': df[df['location'] == c][per_capita_selection],
            'text': df[df['location'] == c]['date'].map(lambda x: f'{x:%m-%d-%Y}'),
            'customdata': [f'Confirmed Cases: {cases:,}<br>'
                           f'Population: {pop:,}<br>'
                           f'Cases Per 100K: {cpc:.2f}' for pop, cases, cpc in zip(
                                [int(population_dict.get(c, 0))] * len(df[df['location'] == c]),
                                df[df['location'] == c]['total'].astype(int).values,
                                df[df['location'] == c]['per_100k'].values)],
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
    x_title = 'Days Since Cases = 100'
    fig.update_yaxes(title_text=y_title, showgrid=True,
                     type=log_selection, row=1, col=1)
    fig.update_xaxes(title_text=x_title, showgrid=True,
                     range=[0, x_max], row=1, col=1)

    return fig


@app.callback(
    dash.dependencies.Output('case-bar-graph', 'figure'),
    [dash.dependencies.Input('CountrySelector2', 'value'),
     dash.dependencies.Input('LogSelector2', 'value')])
def update_country_bar_graph(country_selection, log_selection):
    colors = TRACE_COLORS[:len(countries)]
    fig = make_subplots(rows=1, cols=1,
                        vertical_spacing=0.08,
                        horizontal_spacing=0)

    # bar chart
    for i, c in enumerate(country_selection):
        fig.append_trace({
            'x': df[df['location'] == c]['since_t0'],
            'y': df[df['location'] == c]['total'],
            'text': df[df['location'] == c]['date'].map(lambda x: f'{x:%m-%d-%Y}'),
            'name': c,
            'type': 'bar',
            'marker_color': TRACE_COLORS[i],
            'opacity': 1 if c == 'United States' else 0.7,
            'hovertemplate': '%{text} (Day %{x})<br>'
                             'Confirmed Cases: %{y:,.0f}<br>',
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
    x_title = 'Days Since Cases = 100'
    fig.update_yaxes(title_text=y_title, showgrid=True,
                     type=log_selection, row=1, col=1)
    fig.update_xaxes(title_text=x_title, showgrid=True,
                     range=[0, x_max], row=1, col=1)

    return fig


@app.callback(
    dash.dependencies.Output('state-case-line-graph', 'figure'),
    [dash.dependencies.Input('StateSelector', 'value'),
     dash.dependencies.Input('LogSelector3', 'value'),
     dash.dependencies.Input('StatePerCapitaSelector', 'value')])
def update_state_line_graph(state_selection, log_selection, per_capita_selection):
    colors = TRACE_COLORS[:len(states)]
    fig = make_subplots(rows=1, cols=1,
                        vertical_spacing=0.08,
                        horizontal_spacing=0)
    # line chart
    for i, s in enumerate(state_selection):
        fig.append_trace({
            'x': df_us[df_us['state'] == s]['date'],
            'y': df_us[df_us['state'] == s][per_capita_selection],
            'text': df_us[df_us['state'] == s]['date'].map(lambda x: f'{x:%m-%d-%Y}'),
            'customdata': [f'Confirmed Cases: {cases:,}<br>'
                           f'Population: {pop:,}<br>'
                           f'Cases Per 100K: {cpc:.2f}' for pop, cases, cpc in zip(
                                [int(us_population_dict.get(s, 0))] * len(df_us[df_us['state'] == s]),
                                df_us[df_us['state'] == s]['total'].astype(int).values,
                                df_us[df_us['state'] == s]['per_100k'].values)],
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
