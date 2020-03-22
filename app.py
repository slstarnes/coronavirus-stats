import dash
import dash_core_components as dcc
import dash_html_components as html
from plotly.subplots import make_subplots
from data import get_data, country_filter
from constants import PLOT_LOOKAHEAD, JHU_DATA_FILE_URL, TRACE_COLORS
from data_mod_date import get_data_mod_date

dcc.Graph.responsive = True
df = get_data()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Coronavirus Stats'
server = app.server

data_mod_date = get_data_mod_date(JHU_DATA_FILE_URL)

x_max = min(df[df['location'] == 'United States']['since_t0'].max() + PLOT_LOOKAHEAD,
            df['since_t0'].max())

countries = df.groupby('location').max()['total_cases'].sort_values(ascending=False).keys().values

app.layout = html.Div([
    dcc.Markdown('# Coronavirus Confirmed Cases\n' +
                 '_(based on data from Johns Hopkins\' Coronavirus Resource Center - ' +
                 '[https://coronavirus.jhu.edu](https://coronavirus.jhu.edu))_'),
    html.Div([
        html.Div(
            dcc.Dropdown(
                id="CountrySelector",
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
                id="LogSelector",
                options=[
                    {'label': 'Log Scale', 'value': 'log'},
                    {'label': 'Linear Scale', 'value': 'linear'}
                ],
                value='log',
                labelStyle={'display': 'inline-block',
                            'horizontal-align': 'right'}),
            style={'width': '50%',
                   'display': 'inline-block'})
        ],
        style={'width': '100%',
               'display': 'inline-block'}),
    dcc.Graph(id='case-graph',
              style={'display': 'inline-block',
                     'height': '90vh',
                     'width': '100%'}),
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

@app.callback(
    dash.dependencies.Output('case-graph', 'figure'),
    [dash.dependencies.Input('CountrySelector', 'value'),
     dash.dependencies.Input('LogSelector', 'value')])
def update_graph(country_selection, log_selection):
    colors = TRACE_COLORS[:len(countries)]
    fig = make_subplots(rows=2, cols=1,
                        vertical_spacing=0.08,
                        # shared_xaxes=True,
                        horizontal_spacing=0)
    # line chart
    for i, c in enumerate(country_selection):
        fig.append_trace({
            'x': df[df['location'] == c]['since_t0'],
            'y': df[df['location'] == c]['total_cases'],
            'text': df[df['location'] == c]['date'].map(lambda x: f'{x:%m-%d-%Y}'),
            'name': c,
            'mode': 'lines',
            'type': 'scatter',
            'opacity': 1 if c == 'United States' else 0.7,
            'line': {'width': 3 if c == 'United States' else 2,
                     'color': TRACE_COLORS[i]},
            'hovertemplate': '%{text} (Day %{x})<br>'
                             'Confirmed Cases: %{y:,.0f}<br>',
        }, 1, 1)

    # bar chart
    for i, c in enumerate(country_selection):
        fig.append_trace({
            'x': df[df['location'] == c]['since_t0'],
            'y': df[df['location'] == c]['total_cases'],
            'text': df[df['location'] == c]['date'].map(lambda x: f'{x:%m-%d-%Y}'),
            'name': c,
            'type': 'bar',
            'marker_color': TRACE_COLORS[i],
            'opacity': 1 if c == 'United States' else 0.7,
            'hovertemplate': '%{text} (Day %{x})<br>'
                             'Confirmed Cases: %{y:,.0f}<br>',
        }, 2, 1)

    fig['layout'].update(
        showlegend=True,
        legend_title='<b> Legend <b>',
        legend=dict(x=1.01, y=0.5),
        hovermode='x',
        margin={'t': 0.1, 'b': 0.1},
        colorway=colors,
        template='plotly_white'
    )

    y_title = 'Total Confirmed Cases'
    x_title = 'Days Since Cases = 100'
    fig.update_yaxes(title_text=y_title, showgrid=True,
                     type=log_selection, row=1, col=1)
    fig.update_yaxes(title_text=y_title, showgrid=True,
                     type=log_selection, row=2, col=1)
    fig.update_xaxes(title_text=x_title, showgrid=True,
                     range=[0, x_max], row=1, col=1)
    fig.update_xaxes(title_text=x_title, showgrid=True,
                     range=[0, x_max], row=2, col=1)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)