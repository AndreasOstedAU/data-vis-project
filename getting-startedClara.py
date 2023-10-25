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

df = pd.read_csv("https://raw.githubusercontent.com/AndreasOstedAU/data-vis-project/main/Data/homicide_data.csv?token=GHSAT0AAAAAACIEN73X6W7JSGZ3MSRL46H2ZIUACCA", encoding="ISO-8859-1")
df['victim_full_name'] = df['victim_first'] +  ' ' + df['victim_last']
arrest = df["disposition"]
raceall = df["victim_race"]
race = np.unique(raceall)
sexall = df["victim_sex"]
sex = np.unique(sexall)
app = Dash(__name__)

raceoptions=[{'label': 'Select all', 'value': 'all_values'}]+[{'label': r, 'value': r} for r in race]
sexoptions=[{'label': 'Select all', 'value': 'all_values'}]+[{'label': r, 'value': r} for r in sex]
cityoptions=[{'label': 'Select all', 'value': 'all_values'}]+[{'label': city, 'value': city} for city in sorted(df['city'].unique())]

app.layout = html.Div([
    html.H4(id='title-output',style={"margin-bottom":"5px","margin-top":"1px","font-size":"20px","text-align":"center"}),
    html.Hr(),
    html.Div([
        dcc.Dropdown(
            id="race-dropdown",
            placeholder="Select race",
            options=raceoptions,
            value=None,
            clearable=False,
            style={"width": "200px", "display": "inline-block","margin-top":"0"}
        ),
        dcc.Dropdown(
            id="sex-dropdown",
            options=sexoptions,
            placeholder="Select sex",
            value=None,
            clearable=False,
            style={"width": "200px", "display": "inline-block","margin-top":"0"}
        ),
        dcc.Dropdown(
            id='city-dropdown',
            placeholder="Select city",
            options=cityoptions,
            value=None,  # Set the default value
            style={"width": "200px", "display": "inline-block","margin-top":"0"}
        ),
    ],
    style={"display":"flex",'vertical-align': 'top'}),
    html.Div([
    html.Div(dcc.Graph(id='murder-map'),style={"width":"auto"}),
    html.Div(dcc.Graph(id='getting-started-x-graph'),style={"width":"auto"}),
    html.Div(dcc.Graph(id='getting-started-x-graph2'),style={"width":"auto"}),
    html.Button('Reset Selection', id='reset-button', n_clicks=0)
    ],
    style={"display":"flex",'vertical-align': 'top','width':"100%","height":"100%","flex-wrap": "wrap"},
),
dcc.Store(id='selected-city')])

def make_map(df):
    #filtered_df = df[df['city'] == city] if city != 'all cities' else df
  
    fig = px.scatter_mapbox(
        df,  # Use the aggregated data
        lat="lat",
        lon="lon",
        hover_name="city",  # Show the city name in the hover text
        hover_data=[],
        height=500

    )
    return fig

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
        filtered_data1=df
    else:
        filtered_data1 = df[df["victim_race"] == selected_race]
    if selected_sex=="all_values":
        filtered_data2=filtered_data1
    
    else:
        filtered_data2=filtered_data1[filtered_data1["victim_sex"]==selected_sex]
    if city=="all_values":
        filtered_data=filtered_data2
    else:
        filtered_data = filtered_data2[filtered_data2['city'] ==city]
        
    city_data = filtered_data.groupby('city').agg({'lat': 'mean', 'lon': 'mean'}).reset_index()

    city_list = [city for city in df['city'].unique()]

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

    if city in city_list:
        datamap=filtered_data
    else:
        datamap=city_data

    fig=make_map(datamap)
   #figall = px.scatter_mapbox(
   #    city_data,  # Use the aggregated data
   #    lat="lat",
   #    lon="lon",
   #    hover_name="city",  # Show the city name in the hover text
   #    hover_data=[],
   #    zoom=7,
   #    height=500,
   #)
   ## Remove lat and lon from hover information
   #figall.update_traces(hovertemplate='%{hovertext}')
   #figzoom = px.scatter_mapbox(
   #        filtered_data,
   #        lat="lat",
   #        lon="lon",
   #        hover_name="victim_full_name",
   #        hover_data=["victim_race", "victim_age", "victim_sex"],
   #        color = "victim_race",
   #        center={"lat": center_lat, "lon": center_lon},
   #        #color_discrete_sequence=["blue"],
   #        height=500,
   #    )
    #title=f'Murders in {city}' if city in city_list else f'Murders in the US'
    fig.update_layout(mapbox_style="light", mapbox_accesstoken=mapbox_token,mapbox_zoom=9 if city in city_list else 2.6)
    fig.update_layout(margin={"r": 5, "t": 5, "l": 5, "b": 5})
    #figall.update_layout(showlegend = True) 
    fig.update_layout(width=500, height=290)

    #figzoom.update_layout(mapbox_style="light", mapbox_accesstoken=mapbox_token,mapbox_zoom=9)
    if city in city_list:
        fig.update_layout(showlegend = True,legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01
)) 
    else:
        fig.update_layout(mapbox_center={"lat": 37.0902, "lon": -95.7129})
        fig.update_traces(hovertemplate='%{hovertext}')

    #figzoom.update_layout(width=500, height=290)

    fig1 = go.Figure(
        data=go.Bar(x=np.unique(filtered_data["disposition"]), y=filtered_data["disposition"].value_counts(),
                    marker_color="Gold"))
    fig1.update_layout(dragmode='zoom',width=500, height=290)
    fig1.update_layout(margin={"r": 5, "t": 5, "l": 5, "b": 5})

    fig2 = go.Figure(
        data=go.Bar(x=np.unique(filtered_data["victim_age"]), y=filtered_data["victim_age"].value_counts(),
                    marker_color="Gold"))
    fig2.update_layout(dragmode='zoom',width=500, height=290)
    fig2.update_layout(margin={"r": 5, "t": 5, "l": 5, "b": 5})



    # Check if the selected city is in the list of cities
    #if city in city_list:
        # Create and return the figure you want to display for selected cities
        # Here, we are using the same fig1 and fig2 figures, but you can replace them with your own
    return fig, fig1, fig2
    #else:
        # Create and return the default figure (the map) for other cities
        #return fig, fig1, fig2

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

@app.callback(
    Output('title-output', 'children'),
    [Input('city-dropdown', 'value')]
)
def update_title(city):
    city_list = [city for city in df['city'].unique()]
    if city in city_list:
        return f'Murders in {city}' 
    else:
        return 'Murders in the US'
    

# Define callback to update the map when dropdown selection changes
@app.callback(
    [Output('murder-map', 'figure',allow_duplicate=True),
    Output('reset-button', 'n_clicks')],
    [Input('city-dropdown', 'value'),
     Input('murder-map','figure'),
     Input('murder-map', 'selectedData'),
     Input('reset-button', 'n_clicks')],prevent_initial_call=True
)
def update_map(selected_city, mapfig,selected_data, n_clicks):
        fig = mapfig
        print(mapfig)
        

        if selected_data:
            latitudes = [point['lat'] for point in selected_data['points']]
            longitudes = [point['lon'] for point in selected_data['points']]
            #print(selected_data['points'])
            center = {
                "lat": np.mean(latitudes),
                "lon": np.mean(longitudes)
            }
            zoom = 12 
            
            fig.update_layout(mapbox_center=center, mapbox_zoom=zoom)

            
            selected_points = [(point['pointIndex'], point['curveNumber']) for point in selected_data['points']]
            unique_curves = range(len(fig.data)) #all possible curves (legend items )

            selected_dict = {c: [] for c in unique_curves}
            for p,c in selected_points:
                selected_dict[c].append(p)
            
            for u in unique_curves:
                fig.data[u].update(selectedpoints = selected_dict[u])

        if n_clicks is not None and n_clicks > 0:
            fig = mapfig#make_map(selected_city)
            n_clicks = 0
            return fig,0

        return fig,0



if __name__ == "__main__":
    app.run_server(debug=True)
