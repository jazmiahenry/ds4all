import dash # v 1.16.2
import dash_core_components as dcc # v 1.12.1
import dash_bootstrap_components as dbc # v 0.10.3
import dash_html_components as html # v 1.1.1
import pandas as pd
import plotly.express as px # plotly v 4.7.1
import plotly.graph_objects as go
import numpy as np
from dash.dependencies import Input, Output

app = dash.Dash(__name__, title='STEM Bills Passed by Congress since 1973')

df = pd.read_csv('stembillsus.csv')
features = ['Intro_bills', 'passed_house', 'paassed_senate', 'enacted_signed_by_pres', 'enacted_included_in_other_bill']
total_passed = df.sum(axis=0)
df.values
df.sort_values(by = ['congress'])

app.layout = html.Div([
    html.Div([

        html.Div([

            html.Div([
                html.Label('STEM Bills Passed'),], style={'font-size': '18px'}),

            dcc.Dropdown(
                id='first-model',
                options=[
                    {'label': 'STEM Bills Passed: Overall', 'value': 'Total Bills'},
                    {'label': 'STEM Bills Passed: Per Congress', 'value': 'Bills Passed Per Congress'},
                    {'label': 'STEM Bills Passed: Included in Another Bill', 'value': 'Bills Rolled Into One'},
                    {'label': 'STEM Bills Passed: One Term President vs. Two Term President', 'value': 'One Term President vs. Two Term President'}
                ],
                value='Total Bills',
                clearable=False

            )], style={'width': '49%', 'display': 'inline-block'}
        ),

        html.Div([

            html.Div([
                html.Label('Bills Passed Split vs. Unified Goverment'),], style={'font-size': '18px', 'width': '40%', 'display': 'inline-block'}),

            html.Div([
                dcc.RadioItems(
                    id='gradient-scheme',
                    options=[
                        {'label': 'Split Government', 'value': 'Split'},
                        {'label': 'Unified Government', 'value': 'Unified'},
                    ],
                    value='Split',
                    labelStyle={'float': 'right', 'display': 'inline-block', 'margin-right': 10}
                ),
            ], style={'width': '49%', 'display': 'inline-block', 'float': 'right'}),

            dcc.Dropdown(
                id='crossfilter-feature',
                options=[{'label': i, 'value': i} for i in features],
                value='None',
                clearable=False
            )], style={'width': '49%', 'float': 'right', 'display': 'inline-block'}

        )], style={'backgroundColor': 'rgb(17, 17, 17)', 'padding': '10px 5px'}
    ),

    html.Div([

        dcc.Graph(
            id='scatter-plot',
            hoverData={'points': [{'billspassed': 0}]}
        )

    ], style={'width': '100%', 'height':'90%', 'display': 'inline-block', 'padding': '0 20'}),

    html.Div([
        dcc.Graph(id='point-plot'),
    ], style={'display': 'inline-block', 'width': '100%'}),

    ], style={'backgroundColor': 'rgb(17, 17, 17)'},
)
html.Div([
    dcc.Graph(id='graph-with-slider'),
    dcc.Slider(
        id='congress-slider',
        min=df['congress'].min(),
        max=df['congress'].max(),
        value=df['enacted_signed_by_pres'].sum(),
        marks={str(year): str(year) for year in df['congress'].unique()},
        step=None
    )
])

@app.callback(
    dash.dependencies.Output('scatter-plot', 'figure'),
    [
        dash.dependencies.Input('crossfilter-feature', 'value'),
        dash.dependencies.Input('first-model', 'value'),
        dash.dependencies.Input('gradient-scheme', 'value')
    ]
)
def update_graph(feature, model, gradient):

    if feature == 'None':
        cols = None
        sizes = None
        hover_names = [f'Bills Passed {ix:03d}' for ix in df.index.values]
    else:
        cols = df[features].values
        sizes = [np.max([max_val/10, x]) for x in df[feature].values]
        hover_names = []
        for ix, val in zip(df.index.values, df[feature].values):
            hover_names.append(f'Bills Passed {ix:03d}<br>{feature} value of {val}')

    fig = px.scatter(
        df,
        x=df['congress'],
        y=df[f'enacted_signed_by_pres'],
        color=cols,
        size=sizes,
        opacity=0.8,
        hover_name=hover_names,
        hover_data=features,
        template='plotly_dark',
        color_continuous_scale=gradient,
    )

    fig.update_traces(congress=df.index)

    fig.update_layout(
        coloraxis_colorbar={'Bills Passed': f'{feature}'},
        # coloraxis_showscale=False,
        legend_title_text='Congress',
        height=650, margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
        hovermode='closest',
        template='plotly_dark'
    )

    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)

    return fig


def create_point_plot(df, title):

    fig = go.Figure(
        data=[
            go.Bar(name='Bills Introduced', x=df['Intro_bills'], y=df['congress'], marker_color='#c178f6'),
            go.Bar(name='Bills Passed by House, Senate, and President', x=df['congress'], y=features, marker_color='#89efbd')
        ]
    )

    fig.update_layout(
        barmode='group',
        height=225,
        margin={'l': 20, 'b': 30, 'r': 10, 't': 10},
        template='plotly_dark'
    )

    fig.update_xaxes(showgrid=False)

    return fig


@app.callback(
    dash.dependencies.Output('point-plot', 'figure'),
    [
        dash.dependencies.Input('scatter-plot', 'hoverData')
    ]
)
def update_point_plot(hoverData):
    index = hoverData['points'][0]['billspassed']
    title = f'STEM Bills In Congress since 1973'
    return create_point_plot(df, title)

@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('congress-slider', 'value')])
def update_figure(Split_Gov):
    filtered_df = df[df.congress == congressional_term, df.Split_Gov == split_gov]

    fig = px.scatter(filtered_df, x='congressional_term', y='split_gov',
                     size="pop", color="prism", hover_name="split vs. unified government",
                     log_x=True, size_max=55)

    fig.update_layout(transition_duration=500)

    return fig
    

if __name__ == '__main__':
    app.run_server(debug=True)
