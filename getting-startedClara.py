from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime as dt
import plotly.express as px
from dash import Dash, dcc
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate


mapbox_token = 'pk.eyJ1IjoiYW5kcmVhc29zdGVkIiwiYSI6ImNsbmJxMjFndDA4dm8ybXJrMzhia2NqdnoifQ.fXDNIJ1LelhA1ypNiaJE9w'

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
    html.Div(dcc.Graph(id='getting-started-x-graph2'))
    ],
    style={"display":"flex"},
),
dcc.Store(id='selected-city')])

    

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
        
    city_data = filtered_data.groupby('city').agg({'lat': 'mean', 'lon': 'mean'}).reset_index()

    city_list = [city for city in data['city'].unique()]

    city_data_zoom = filtered_data[filtered_data['city'] == city]
    # Check if the selected city is in the list of cities
    # Calculate the latitude and longitude bounds
    min_lat = city_data_zoom['lat'].min()
    max_lat = city_data_zoom['lat'].max()
    min_lon = city_data_zoom['lon'].min()
    max_lon = city_data_zoom['lon'].max()
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2
    # Calculate the zoom level based on the bounds

    figall = px.scatter_mapbox(
        city_data,  # Use the aggregated data
        lat="lat",
        lon="lon",
        hover_name="city",  # Show the city name in the hover text
        hover_data=[],
        zoom=7,
        height=500,
    )
    # Remove lat and lon from hover information
    figall.update_traces(hovertemplate='%{hovertext}')
    figzoom = px.scatter_mapbox(
            filtered_data,
            lat="lat",
            lon="lon",
            hover_name="victim_full_name",
            hover_data=["victim_race", "victim_age", "victim_sex"],
            color = "victim_race",
            center={"lat": center_lat, "lon": center_lon},
            #color_discrete_sequence=["blue"],
            height=500,
        )
    title=f'Murders in {city}' if city in city_list else f'Murders in the US'
    figall.update_layout(mapbox_style="light", mapbox_accesstoken=mapbox_token, title = title,mapbox_zoom=2.6,mapbox_center={"lat": 37.0902, "lon": -95.7129})
    figall.update_layout(margin={"r": 5, "t": 40, "l": 5, "b": 5})
    figall.update_layout(showlegend = True) 
    figall.update_layout(width=500, height=340)

    figzoom.update_layout(mapbox_style="light", mapbox_accesstoken=mapbox_token,title =title,mapbox_zoom=9)
    figzoom.update_layout(margin={"r": 5, "t": 40, "l": 5, "b": 5})
    figzoom.update_layout(showlegend = True,legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01
)) 
    figzoom.update_layout(width=500, height=340)

    fig1 = go.Figure(
        data=go.Bar(x=np.unique(filtered_data["disposition"]), y=filtered_data["disposition"].value_counts(),
                    marker_color="Gold"))
    fig1.update_layout(dragmode='zoom')

    fig2 = go.Figure(
        data=go.Bar(x=np.unique(filtered_data["victim_age"]), y=filtered_data["victim_age"].value_counts(),
                    marker_color="Gold"))
    fig2.update_layout(dragmode='zoom')



    # Check if the selected city is in the list of cities
    if city in city_list:
        # Create and return the figure you want to display for selected cities
        # Here, we are using the same fig1 and fig2 figures, but you can replace them with your own
        return figzoom, fig1, fig2
    else:
        # Create and return the default figure (the map) for other cities
        return figall, fig1, fig2

@app.callback(
    Output('selected-city', 'data'),
    [Input('murder-map', 'clickData')]
)
def update_selected_city(click_data):
    if click_data:
        selected_city = click_data['points'][0]['hovertext']
        return selected_city
    else:
        raise PreventUpdate
    
@app.callback(
    Output('city-dropdown', 'value'),
    Input('selected-city', 'data')
)
def update_city_dropdown(selected_city):
    return selected_city


if __name__ == "__main__":
    app.run_server(debug=True)
