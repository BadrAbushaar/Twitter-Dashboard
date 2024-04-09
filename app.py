from dash import Dash, dcc, html, Input, Output, callback, dash_table
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd

app = Dash(__name__)

df = pd.read_csv('ProcessedTweets.csv')
months = df['Month'].unique()
options = [{'label': month, 'value': month} for month in months]

dropdown = html.Div(className="dropdown", children=[html.P("Month "), dcc.Dropdown(id='dropdown_id', options=options, value=None, style=dict(width=150, marginLeft=2))])
sentimentSlider = html.Div(className="slider", children=[html.P("Sentiment"), dcc.RangeSlider(id='sentiment_slider_id', min=df['Sentiment'].min(), max=df['Sentiment'].max(), value=[-1, 1])])
subjectivitySlider = html.Div(className="slider", children=[html.P("Subjectivity"), dcc.RangeSlider(id='subjectivity_slider_id', min=df['Subjectivity'].min(), max=df['Subjectivity'].max(), value=[0, 1])])
fig = px.scatter(df, x='Dimension 1', y='Dimension 2', labels={'Dimension 1':' ', 'Dimension 2':' '}, color_discrete_sequence = ['#A9A9A9'])
fig.update_layout(dragmode='lasso', xaxis=dict(showticklabels=False), yaxis=dict(showticklabels=False))

app.layout = html.Div(className="container", children = [
    html.Div(className='filters', children=[
        html.Div(id="dropdown", className="filter-item filter-dropdown", children=[dropdown]), 
        html.Div(id="sentimentSlider", className="filter-item", children=[sentimentSlider]),
        html.Div(id="subjectivitySlider", className="filter-item", children=[subjectivitySlider])]),
    html.Div(className='graph', children=[
        dcc.Graph(id='scatterplot', figure=fig, style={'width': '100%', 'height': '100%'})
        ]),
    html.Div(className='table', children=[
        dash_table.DataTable(id='table', columns=[{'name': 'RawTweet', 'id': 'RawTweet'}], 
                             style_table={'width': '100%', 'maxWidth':'100%'},
                             style_header={'textAlign': 'center'},
                             style_cell={'textAlign': 'center', 'whiteSpace': 'normal', 'height': 'auto', 'overflow': 'hidden', 'textOverflow': 'ellipsis', 'padding': '7px'}, 
                             page_size=10)        
        ]),
    ])


@app.callback(Output('scatterplot', 'figure'), [Input('dropdown_id', 'value'), Input('sentiment_slider_id', 'value'), Input('subjectivity_slider_id', 'value')])
def update_graph(selected_month, sentiment_values, subjectivity_values):
    global fig
    if selected_month is None and sentiment_values == [-1, 1] and subjectivity_values == [0, 1]:
        raise PreventUpdate
    
    filtered_df = df.copy()
    if selected_month is not None:
        filtered_df = filtered_df[filtered_df['Month'] == selected_month]
    if sentiment_values is not None:
        filtered_df = filtered_df[(filtered_df['Sentiment'] >= sentiment_values[0]) & (filtered_df['Sentiment'] <= sentiment_values[1])]
    if subjectivity_values is not None:
        filtered_df = filtered_df[(filtered_df['Subjectivity'] >= subjectivity_values[0]) & (filtered_df['Subjectivity'] <= subjectivity_values[1])]

    fig = px.scatter(filtered_df, x='Dimension 1', y='Dimension 2', labels={'Dimension 1':' ', 'Dimension 2':' '}, color_discrete_sequence = ['#A9A9A9'])
    fig.update_layout(xaxis=dict(showticklabels=False), yaxis=dict(showticklabels=False))
    return fig

@app.callback(Output('table', 'data'), [Input('scatterplot', 'selectedData')])
def update_table(selectedData):
    if selectedData is None:
        raise PreventUpdate

    selected_points = selectedData['points']
    selected_info = []
    for point in selected_points:
        selected_info.append(df.iloc[point['pointIndex']]['RawTweet'])
    return [{'RawTweet': tweet} for tweet in selected_info]

if __name__ == '__main__':
    app.run(debug=False)


