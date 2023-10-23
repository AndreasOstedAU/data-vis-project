from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime as dt
import plotly.express as px
from dash import Dash, dcc
import dash_bootstrap_components as dbc

username = 'ClaraWolff'
repository = 'Gittest'
file_path = 'Kanaler.csv'
access_token = "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"

data = pd.read_csv("https://raw.githubusercontent.com/AndreasOstedAU/data-vis-project/main/Data/homicide_data.csv?token=GHSAT0AAAAAACIEN73X6W7JSGZ3MSRL46H2ZIUACCA", encoding="ISO-8859-1")

data['victim_full_name'] = data['victim_first'] +  ' ' + data['victim_last']
arrest = data["disposition"]
raceall = data["victim_race"]
race = np.unique(raceall)
sexall = data["victim_sex"]
sex = np.unique(sexall)
app = Dash(__name__)

raceoptions=[{'label': 'Select all', 'value': 'all_values'}]+[{'label': r, 'value': r} for r in race]
sexoptions=[{'label': 'Select all', 'value': 'all_values'}]+[{'label': r, 'value': r} for r in sex]
cityoptions=[{'label': 'Select all', 'value': 'all_values'}]+[{'label': city, 'value': city} for city in sorted(data['city'].unique())]

app.layout = html.Div([
    html.H4('Homocides'),
    html.Div([
        dcc.Dropdown(
            id="race-dropdown",
            placeholder="Select race",
            options=raceoptions,
            value=None,
            clearable=False,
            style={"width": "200px", "display": "inline-block"}
        ),
        dcc.Dropdown(
            id="sex-dropdown",
            options=sexoptions,
            placeholder="Select sex",
            value=None,
            clearable=False,
            style={"width": "200px", "display": "inline-block"}
        ),
        dcc.Dropdown(
            id='city-dropdown',
            placeholder="Select city",
            options=cityoptions,
            value=None,  # Set the default value
            style={"width": "200px", "display": "inline-block"}
        ),
    ],
    style={"display":"flex"}),
    html.Div([
    html.Div(dcc.Graph(id='murder-map')),
    html.Div(dcc.Graph(id='getting-started-x-graph')),
    html.Div(dcc.Graph(id='getting-started-x-graph2')),
    ],
    style={"display":"flex"},
)])

    

@app.callback(
    [Output("murder-map", "figure"),
     Output("getting-started-x-graph", "figure"),
     Output("getting-started-x-graph2", "figure"),
     ],
    [Input("race-dropdown", "value"),
    Input("sex-dropdown", "value"),
    Input("city-dropdown", "value")])
def display_race(selected_race,selected_sex,city):
    if selected_race is None:
        selected_race = raceoptions[0]["value"]  # Set default race
    if selected_sex is None:
        selected_sex = sexoptions[0]["value"]  # Set default sex
    if city is None:
        city = cityoptions[0]["value"]  # Set default state

    if selected_race=="all_values":
        filtered_data1=data
    else:
        filtered_data1 = data[data["victim_race"] == selected_race]
    if selected_sex=="all_values":
        filtered_data2=filtered_data1
    
    else:
        filtered_data2=filtered_data1[filtered_data1["victim_sex"]==selected_sex]
    if city=="all_values":
        filtered_data=filtered_data2
    else:
        filtered_data = filtered_data2[filtered_data2['city'] ==city]
    fig = px.scatter_mapbox(
            filtered_data,
            lat="lat",
            lon="lon",
            hover_name="victim_full_name",
            hover_data=["victim_race", "victim_age", "victim_sex"],
            color = "victim_race",
            #color_discrete_sequence=["blue"],
            zoom=7,
            height=500,
        )
    fig.update_layout(mapbox_style="open-street-map", title = f'Murders in {city}',mapbox_zoom=3)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_layout(showlegend = False) 
    fig.update_layout(width=500, height=300)

    fig1 = go.Figure(
        data=go.Bar(x=np.unique(filtered_data["disposition"]), y=filtered_data["disposition"].value_counts(),
                    marker_color="Gold"))
    fig1.update_layout(dragmode='zoom')

    fig2 = go.Figure(
        data=go.Bar(x=np.unique(filtered_data["victim_age"]), y=filtered_data["victim_age"].value_counts(),
                    marker_color="Gold"))
    fig2.update_layout(dragmode='zoom')

    return fig, fig1, fig2

if __name__ == "__main__":
    app.run_server(debug=True)

