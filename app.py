import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd

# Here is my generalized recipe for those who would like to implement this as well:


# # layout portion 

# dcc.Store(id='dropdown-cache', data='initial value'),

# dcc.Tabs(
#     id='tabs',
#     value='tab-1',
#     parent_className='custom-tabs',
#     className='custom-tabs-container',
#     children=[

#     dcc.Tab(
#         label='Tab 1',
#         value='tab-1',
#         className='custom-tab',
#         selected_className='custom-tab--selected',
#         children=[
#             dcc.Dropdown(
#                 id='tab-1-dropdown',
#             ),
#         ]
#     ),
#     dcc.Tab(
#         label='Tab 2',
#         value='tab-2',
#         className='custom-tab',
#         selected_className='custom-tab--selected',
#         children=[
#             dcc.Dropdown(
#                 id='tab-2-dropdown',
#             ),
#         ]
#     )
# )

# # callback portion for synchronizing dropdown across tabs. 

# @app.callback(Output('dropdown-cache', 'data'),
#               [Input('tab-1-dropdown', 'value'),
#                Input('tab-2-dropdown', 'value')],
#                [State('tabs', 'value')])
# def store_dropdown_cache(tab_1_drodown_sel, tab_2_drodown_sel, tab):
#     if tab == 'tab-1':
#         return tab_1_drodown_sel
#     elif tab == 'tab-2':
#         return tab_2_drodown_sel


# # Note that using drodowns-cache as an input to change the 
# # dropdown value breaks the layout. I feel this has something 
# # to do with circular reference, but using the state w/tab 
# # value as the input callback trigger works!

# @app.callback(Output('tab-1-dropdown', 'value'),
#               [Input('tabs', 'value')],
#               [State('dropdown-cache', 'data')])
# def synchronize_dropdowns(_, cache):
#     return cache

# @app.callback(Output('tab-2-dropdown', 'value'),
#               [Input('tabs', 'value')],
#               [State('dropdown-cache', 'data')])
# def synchronize_dropdowns(_, cache):
#     return cache


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Coronavirus Stats' 
server = app.server

who_data = pd.read_csv('https://covid.ourworldindata.org/data/full_data.csv')
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
    dcc.Store(id='dropdown-cache', data=country_filter),
    dbc.Tabs(
        id="tabs",
        # parent_className='custom-tabs',
        # value='Line Chart',
        # className='custom-tabs-container',
        children=[
            dbc.Tab(
                label='Line Chart', 
                id='line-tab',
                className='custom-tab',
                # selected_className='custom-tab--selected',
            ),
            dbc.Tab(
                label='Bar Chart', 
                id='bar-tab',
                className='custom-tab',
                # selected_className='custom-tab--selected',
            )
        ],
        active_tab="line-tab"
    ),
    html.Div(id='tabs-content'),
    html.Div([
        dcc.Dropdown(
            id='dropdown',
            options=[{'label': i, 'value': i} for i in countries],
            multi=True,
            value='China'
        ),
    ]),
    html.P(["data source: https://ourworldindata.org/coronavirus-source-data", html.Br(), 
               "code source: https://github.com/slstarnes/coronavirus-stats"]),
])

@app.callback(Output('dropdown-cache', 'data'),
              [Input('dropdown', 'value')],
               [State('tabs', 'id')])
def store_dropdown_cache(dropdown_sel, tab):
    print('store_dropdown_cache')
    print('dropdown_sel', dropdown_sel)
    print('tab', tab)
    if tab == 'line-tab':
        return dropdown_sel
    elif tab == 'bar-tab':
        return dropdown_sel

# @app.callback(Output('dropdown', 'value'),
#               [Input('tabs', 'value')],
#               [State('dropdown-cache', 'data')])
# def synchronize_dropdowns(_, cache):
#     print('synchronize_dropdowns')
#     print('cache', cache)
#     return cache

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'id'), Input('dropdown-cache', 'data')])
def update_figure(tab, country_list):
    print('update_figure')
    print('country_list', country_list)
    if country_list == None:
        print('NONE')
        country_list = country_filter
    if tab == 'bar-tab':
        return dbc.Graph(
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
                                              
                            ) for i in country_list
                        ],
                        'layout': dict(
                            xaxis={'title': 'Days Since Cases = 100', 'range': [0, x_max]},
                            yaxis={'type': 'log', 'title': 'Total Confirmed Cases'},
                            margin={'l': 100, 'b': 40, 't': 10, 'r': 10},
                            hovermode='compare'
                        )
                    }
                )
    elif tab == 'line-tab':
        return dbc.Graph(
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
                                              
                            ) for i in country_list
                        ],
                        'layout': dict(
                            xaxis={'title': 'Days Since Cases = 100', 'range': [0, x_max], 'zeroline': False},
                            yaxis={'type': 'log', 'title': 'Total Confirmed Cases'},
                            margin={'l': 100, 'b': 40, 't': 10, 'r': 10},
                            hovermode='compare'
                        )
                    }
                ),

if __name__ == '__main__':
    app.run_server(debug=True)