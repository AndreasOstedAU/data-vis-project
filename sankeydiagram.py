from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import json, urllib
import pandas as pd

app = Dash(__name__)

app.layout = html.Div([
    html.H4('Murders in America'),
    dcc.Graph(id="graph"),
    html.P("Opacity"),
    dcc.Slider(id='slider', min=0, max=1, 
               value=0.5, step=0.1)
])

def get_sankey(data,path,value_col):
    sankey_data = {
    'label':[],
    'source': [],
    'target' : [],
    'value' : []
    }
    counter = 0
    while (counter < len(path) - 1):
        for parent in data[path[counter]].unique():
            sankey_data['label'].append(parent)
            for sub in data[data[path[counter]] == parent][path[counter+1]].unique():
                sankey_data['source'].append(sankey_data['label'].index(parent))
                sankey_data['label'].append(sub)
                sankey_data['target'].append(sankey_data['label'].index(sub))
                sankey_data['value'].append(data[data[path[counter+1]] == sub][value_col].sum())
                
        counter +=1
    return sankey_data

data = pd.read_csv("https://raw.githubusercontent.com/AndreasOstedAU/data-vis-project/main/Data/homicide_data.csv")
mask = data['victim_age'] == 'Unknown'
data = data[~mask]
data['victim_sex'].mask(data['victim_sex'] == 'Unknown', 'Unknown sex', inplace=True)
data['victim_race'].mask(data['victim_race'] == 'Unknown', 'Unknown race', inplace=True)
data['victim_age'] = pd.to_numeric(data['victim_age'])
data['age_binned'] = pd.cut(x=data['victim_age'], bins=[0,9,19, 29, 39, 49, 59, 69, 79, 89, 99, 109], labels=['0-9','10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-99','100+'])
grouped_df = data[['disposition', 'victim_sex', 'victim_first', 'age_binned', 'victim_race']].groupby(['victim_race','age_binned','disposition', 'victim_sex'], as_index = False)['victim_first'].count()
grouped_df = grouped_df.rename(columns={"victim_first":"count"})

my_sankey = get_sankey(grouped_df, ['disposition','victim_sex','victim_race','age_binned'],'count')

@app.callback(
    Output("graph", "figure"), 
    Input("slider", "value"))

def display_sankey(opacity):
    
    
    fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 40,
      line = dict(color = "black", width = 0.5),
      label = my_sankey['label'],
      color = "blue"
    ),
    link = dict(
      source = my_sankey['source'],
      target = my_sankey['target'],
      value = my_sankey['value']
  ))])

    fig.update_layout(font_size=10)
    return fig

app.run_server(debug=True)