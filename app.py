import numpy as np
import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html,  State
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from dash.exceptions import PreventUpdate


mapbox_token = 'pk.eyJ1IjoiYW5kcmVhc29zdGVkIiwiYSI6ImNsbmJxMjFndDA4dm8ybXJrMzhia2NqdnoifQ.fXDNIJ1LelhA1ypNiaJE9w'


### Data wrangling
df = pd.read_csv('Data/homicide_data.csv')
citydata = pd.read_csv('Data/us-cities-top-1k.csv')
statedata = pd.read_csv('Data/states.csv')

citydata=pd.merge(citydata, statedata, on = "State", how = "left")
df['victim_full_name'] = df['victim_first'] +  ' ' + df['victim_last']

df = df.sort_values('city')

df['reported_date'] = pd.to_datetime(df['reported_date'], format='%Y%m%d')

# Extract month from date and convert to string
df['month'] = df['reported_date'].dt.strftime('%Y-%m')
df['quarter'] = df['reported_date'].dt.to_period('Q').dt.strftime('%Y-Q%q')

df['year'] = df['reported_date'].dt.strftime('%y')
df['month2'] = df['reported_date'].dt.strftime('%m')


#join on data about cities
df = pd.merge(df, citydata.rename(columns={"lat": "avg_lat", "lon": "avg_lon","Abbreviation":"state","State":"Long_state"}), on = ['city',"state"], how = 'left')


df['years_range'] = df.groupby('city')['reported_date'].transform(lambda x: (x.max() - x.min()).days / 365)
df['No_homicides_norm_pr1000'] = (df.groupby('city')['city'].transform('count'))/(df["Population"]*df['years_range'])*1000


df['reported_date_only']=df['reported_date'].dt.strftime('%Y-%m-%d')

avg_city_coords = df[['city','avg_lat','avg_lon','No_homicides_norm_pr1000','Population','state']].drop_duplicates().reset_index()
avg_city_coords = avg_city_coords.drop(49)

obs = df.groupby(['disposition', 'city']).size().reset_index(name='n_obs')

# Pivot the DataFrame to have 'disposition' as columns and 'city' as index
obs_pivot = obs.pivot(index='city', columns='disposition', values='n_obs')

# Calculate the proportion of 'Open/No arrest' over the sum of all dispositions
obs_pivot['open_prop'] = obs_pivot['Open/No arrest'] / obs_pivot.sum(axis=1)
obs_pivot = obs_pivot.reset_index()


city_df =pd.merge(avg_city_coords,obs_pivot[["city","open_prop"]],on="city",how="left")



### Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

cityoptions = [{'label': 'Select all', 'value': 'all cities'}]+[{'label': city, 'value': city} for city in sorted(df['city'].unique())]
raceoptions = [{'label': 'Select all', 'value': 'all'}]+[{'label': r, 'value': r} for r in sorted(df['victim_race'].unique())]
sexoptions = [{'label': 'Select all', 'value': 'all'}]+[{'label': s, 'value': s} for s in sorted(df['victim_sex'].unique())]

# Define layout
# Define layout
app.layout = html.Div([
    html.H4(id='title-output',style={"margin-bottom":"5px","margin-top":"1px","font-size":"24px","text-align":"center"}),
    html.Hr(style={"margin":"0px","marginBottom":"4px"}),
    html.Div([
    html.Label(["Select city:"],style={"marginBottom":"5px","marginLeft":"5px","marginRight":"5px","font-weight":"bold"}),
    dcc.Dropdown(
        id='city_dropdown',
        options = cityoptions,
        value = 'all cities', #default
        #value = None,
        #placeholder = "Select city",
        clearable=False,
        style={"width": "200px", "display": "inline-block","margin-top":"0"},
    ),
    html.Label(["Select race:"],style={"marginBottom":"5px","marginLeft":"18px","marginRight":"5px","font-weight":"bold"}),
        dcc.Dropdown(
        id='race_dropdown',
        options = raceoptions,
        value = 'all', #default
        #value = None,
        #placeholder = "Select race",
        clearable=False,
        style={"width": "200px", "display": "inline-block","margin-top":"0"}
    ),
    html.Label(["Select gender:"],style={"marginBottom":"5px","marginLeft":"18px","marginRight":"5px","font-weight":"bold"}),

        dcc.Dropdown(
        id='sex_dropdown',
        options = sexoptions,
        value = 'all', #default
        #value = None,
        #placeholder = "Select gender",
        clearable=False,
        style={"width": "200px", "display": "inline-block","margin-top":"0"}
    )],style={"display": "flex", "flex-direction": "row","align-items":"center"}),
    dbc.Card([dcc.Graph(id = 'murder-map',style={"height":"47.8vh"})]
             ,style={"width": "60%","height":"48vh","display":"inline-block","marginRight":"20px","marginBottom":"5px"}),
    dbc.Card([dcc.Graph(id = 'time-spiral',style={"height":"47.8vh"})],style={"width": "35%","height":"48vh","display":"inline-block","marginBottom":"5px"}),
    dbc.Card([dcc.Graph(id = 'disp-colchart',style={"height":"37.8vh"})],style={"width": "30%","height":"38vh","marginRight":"20px","marginTop":"5px","display":"inline-block"}),
    dbc.Card([dcc.Graph(id = 'sankey',style={"height":"37.8vh"})],style={"width": "65%","height":"38vh","marginTop":"5px","display":"inline-block"}),
dcc.Store(id='selected-city', data = 'all cities')
],
style={"marginLeft":"50px"})


def make_colchart(df,city):
    
       
    # Get value counts and reset index
    value_counts = df["disposition"].value_counts().reset_index().sort_values('disposition', ascending = False)
    
    color_map={
        'Open/No arrest':'#CD30F4', 
        'Closed without arrest':'#FF8A00', 
        'Closed by arrest':'#46F30F'
    }

    items=value_counts["disposition"]
    colors=[color_map[category] for category in items]

    fig = go.Figure(data=go.Bar(x=value_counts['disposition'], 
                                y=value_counts['count'],
                                marker_color=colors if city!='all cities' else "#696969",
                                ))

    fig.update_layout(margin={"r": 5, "t": 5, "l": 5, "b": 5}) 
    fig.update_layout(autosize = True,template="plotly_white")
    return fig



def make_spiral_plot(df):
    df['year'] = df['reported_date'].dt.strftime('%y')
    df['month2'] = df['reported_date'].dt.strftime('%m')
    df_summary = df.groupby(['year', 'month2']).size().reset_index(name = 'num_murders_year_month')
    
    ## håndterer fejl som ellers opstår ved valg af city med klik på stort kort
    if df_summary.empty:
        # Return a default or empty figure
        fig = px.bar_polar()
        return fig

    q0, q0_25, q0_5, q0_75, q1 = np.percentile(df_summary['num_murders_year_month'], [0, 25, 50, 75, 100])



    all_years = df['year'].unique()
    all_months = df['month2'].unique()
    all_combinations = pd.DataFrame([(year, month) for year in all_years for month in all_months], columns=['year', 'month2']).sort_values(['year', 'month2'])

    # Merge with df_summary to include zeros for missing combinations
    df_summary = pd.merge(all_combinations, df_summary, on=['year', 'month2'], how='left').fillna(0)
    df_summary['constant_value'] = 1


    df_summary['hovertemplate'] = df_summary.apply(lambda row: 'Year: %s<br>Month: %s<br>Homicides: %d' % (row['year'], row['month2'], row['num_murders_year_month'])
                                                  if row['num_murders_year_month'] > 0 else '',
                                                  axis=1)


    fig = px.bar_polar(df_summary, 
                       r = 'constant_value', 
                       custom_data=['year', 'month2', 'num_murders_year_month'], 
                       theta='month2', 
                       color = 'num_murders_year_month',  
                       color_continuous_scale=[(0, 'rgba(0,0,0,0)'), #hide zero counts
                                               (0, '#C0F2F3'),
                                               (q0/q1, '#81DBDB'), 
                                               (q0_25/q1, '#48CBC5'),
                                               (q0_5/q1, '#1E9C99'),
                                               (q0_75/q1, '#187C7A'),
                                               (1, '#064D51')],
                       range_color = [q0, q1],
                       labels={"num_murders_year_month": "Number of <br>homicides per month"},
                       direction = 'clockwise',
                       category_orders={'month2': np.sort(df_summary['month2'].unique()),
                                        'year': np.sort(df_summary['year'].unique())}  # Specify the order of months
                   )
    fig.update_polars(hole = 0.25, radialaxis=dict(showticklabels=False, ticks='', linewidth=0)) 
    #fig.update_traces(hovertemplate='Year: %{customdata[0]}<br>Month: %{customdata[1]}<br>Murders: %{customdata[2]}') 
    fig.update_traces(hovertemplate=df_summary['hovertemplate'])
    fig.update_traces(hoverinfo = 'none')
    fig.update_layout(autosize = True)

    return fig


def make_sankey(df, cat_cols=['disposition','victim_sex','victim_race','age_binned'], value_cols = 'n_obs'):
    df['victim_age'].mask(df['victim_age'] == 'Unknown', -2, inplace=True)
    mask = df['victim_age'] == 'Unknown'
    df = df[~mask]
    df['victim_sex'].mask(df['victim_sex'] == 'Unknown', 'Unknown sex', inplace=True)
    df['victim_race'].mask(df['victim_race'] == 'Unknown', 'Unknown race', inplace=True)
    df['victim_age'] = pd.to_numeric(df['victim_age'])
    df['age_binned'] = pd.cut(x=df['victim_age'], bins=[-3,-1,9,19, 29, 39, 49, 59, 69, 79, 89, 99, 109], labels=['Unknown age','0-9','10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-99','100+'])
    df = df.sort_values(by=['victim_age'], ascending=True)
    df = df.groupby(['disposition','victim_race','victim_sex','age_binned']).size().reset_index(name='n_obs')
    zeromask = df['n_obs'] == 0
    df = df[~zeromask]

    # maximum of 6 value cols -> 6 colors
    colorPalette = ['#bd0026']*20
    labelList = []
    colorNumList = []
    for catCol in cat_cols:
        labelListTemp =  list(set(df[catCol].values))
        if catCol=='age_binned':
            labelListTemp = ['Unknown age','0-9','10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-99','100+']
        colorNumList.append(len(labelListTemp))
        labelList = labelList + labelListTemp
        
    # remove duplicates from labelList
    del labelList[12:23]
    labelList = list(dict.fromkeys(labelList))
    labelList = labelList + ['Unknown age','0-9','10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-99','100+']
    
    # define colors based on number of levels
    colorList = []
    for idx, colorNum in enumerate(colorNumList):
        colorList = colorList + [colorPalette[idx]]*colorNum
        
    # transform df into a source-target pair
    for i in range(len(cat_cols)-1):
        if i==0:
            sourceTargetDf = df[[cat_cols[i],cat_cols[i+1],value_cols]]
            sourceTargetDf.columns = ['source','target','count']
        else:
            tempDf = df[[cat_cols[i],cat_cols[i+1],value_cols]]
            tempDf.columns = ['source','target','count']
            sourceTargetDf = pd.concat([sourceTargetDf,tempDf])
        sourceTargetDf = sourceTargetDf.groupby(['source','target']).agg({'count':'sum'}).reset_index()

    dispList = list(df['disposition'].unique())
    genderList = list(df['victim_sex'].unique())
    num_gender = len(genderList)
    raceList = list(df['victim_race'].unique())
    num_race = len(raceList)
    ageList = list(df['age_binned'].unique())

    presentList = dispList + genderList + raceList + ageList
    

    x = [0.001, 0.001, 0.001, 0.33, 0.33, 0.33, 0.66, 0.66, 0.66, 0.66, 0.66, 0.66, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999]
    y = [0.2, 0.5, 0.8, 0.8, 0.6, 0.2, 0.4, 0.6, 0.7, 0.3, 0.8, 0.9, 0.999, 0.001, 1.5/11, 2.5/11, 4/11, 5/11, 6/11, 7/11, 0.7, 0.75, 0.8, 0.9]

    deleteList = []

    allList = ['Closed by arrest','Open/No arrest', 'Closed without arrest', 'Male', 'Female', 'Unknown sex', 'Black', 'Hispanic', 'White', 'Other', 'Asian', 'Unknown race','100+','Unknown age','0-9','10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-99']
    
    for i in range(len(allList)):
        if allList[i] not in presentList:
            deleteList.append(i)
    

    for j in range(len(deleteList)):
        del allList[deleteList[j]-j]
        del y[deleteList[j]-j]
        del x[deleteList[j]-j]

    if num_gender == 1:
        idx = allList.index(genderList[0])
        y[idx] = 0.5
    
    if num_race == 1:
        idx = allList.index(raceList[0])
        y[idx] = 0.5

    #new stuff
    sourceTargetDf['source'] = pd.Categorical(sourceTargetDf['source'], allList)
    sourceTargetDf['target'] = pd.Categorical(sourceTargetDf['target'], allList)
    sourceTargetDf.sort_values(['source', 'target'], inplace = True)
    sourceTargetDf.reset_index(drop=True)
        
    # add index for source-target pair
    sourceTargetDf['sourceID'] = sourceTargetDf['source'].apply(lambda x: labelList.index(x))
    sourceTargetDf['targetID'] = sourceTargetDf['target'].apply(lambda x: labelList.index(x))

    

    fig = go.Figure(data=[go.Sankey(
        arrangement = "snap",
    node = dict(
        pad = 15,
        thickness = 20,
        x = x,
        y = y,
        line = dict(
        color = "black",
        width = 0.5
        ),
        color = "black",#aa9183",#'#bd0026',
        label = labelList
    ),
    link = dict(
          source = sourceTargetDf['sourceID'],
          target = sourceTargetDf['targetID'],
          value = sourceTargetDf['count']
        ))],
        layout=dict(
    margin=dict(l=48, r=48, b=45, t=10),
    height=378)
        )


    return fig

def make_map(df, city):
    jitter_factor = 0.0005  # Adjust the jitter factor as needed
    df['lat'] = df['lat'] + np.random.uniform(-jitter_factor, jitter_factor, len(df))
    df['lon'] = df['lon'] + np.random.uniform(-jitter_factor, jitter_factor, len(df))

    fig = px.scatter_mapbox(
        df if city != 'all cities' else city_df,
        lat="lat" if city != 'all cities' else 'avg_lat',
        lon="lon" if city != 'all cities' else 'avg_lon',
        hover_name="victim_full_name" if city != 'all cities' else 'city',
        hover_data=["victim_race", "victim_age", "victim_sex", "reported_date_only"] if city != 'all cities' else None,
        custom_data = ['disposition', 'lat', 'lon', 'victim_race', 'victim_age', 'victim_sex', 'reported_date_only'] if city != 'all cities'\
            else ['No_homicides_norm_pr1000', 'open_prop'],

        color = "disposition"  if city != 'all cities' else "open_prop",
        opacity=0.65 if city != 'all cities' else None,
        color_continuous_scale="YlOrRd" if city=='all cities' else None, #"Rdbu_r" 
        labels={"open_prop": "% Open cases"},
        #labels = hover_labels,
        size='No_homicides_norm_pr1000' if city=='all cities' else None,
        center={"lat": 39.8283-2, "lon": -98.5795} if city=='all cities' else None,
        range_color=[min(city_df["open_prop"])-0.15,max(city_df["open_prop"])] if city=='all cities' else None,
        color_continuous_midpoint=0.5 if city=='all cities' else None,
        category_orders={"disposition": ['Open/No arrest', 'Closed without arrest', 'Closed by arrest']} if city != 'all cities' else None,
        color_discrete_sequence=['#CD30F4','#FF8A00','#46F30F']
    )

    fig.update_coloraxes(colorbar_tickformat='.0%')
    fig.update_layout(mapbox_style="light", 
                      mapbox_accesstoken=mapbox_token, 
                      autosize = True,
                      legend_title_text=" Disposition",
                      legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="right",
                        x=0.99,
                        font=dict(size=16
                                        )
                      )

)
    
    fig.update_layout(mapbox_zoom = 9.5 if city != 'all cities' else 3.2)
    fig.update_traces(uirevision='persist')

    if city == 'all cities':
        fig.update_traces(hovertemplate = "<b>%{hovertext}</b> <br> # Homicides per 1000 capita per year: %{customdata[0]:.3f} <br>Open cases: %{customdata[1]:.1%}"),
    else:
        fig.update_traces(hovertemplate = "<b>%{hovertext}</b> <br> Lat: %{customdata[1]:.3f} <br> Lon: %{customdata[2]:.3f} <br> Race: %{customdata[3]} <br> Age: %{customdata[4]} <br> Gender: %{customdata[5]} <br> Reported date: %{customdata[6]}")


    
    #fig.update_layout(margin={"r": 0, "l": 0, "b": 0})
    fig.update_layout(margin={"r": 0, "l": 15, "b": 5,"t":5})
    fig.update_layout(clickmode='event+select',
                      hovermode='closest')

    return fig



#helper function to filter data based on city, race, sex
def filter_df(selected_city, selected_race = 'all', selected_sex = 'all', df = df):
    all_cities_filter = selected_city == 'all cities'
    all_race_filter = selected_race == 'all'
    all_sex_filter = selected_sex == 'all'

    if all_cities_filter and all_race_filter and all_sex_filter:
        # Handle the case when all filters are 'all'
        filtered_df = df  # Include all data
    else:
        city_filter = df['city'] == selected_city if not all_cities_filter else True
        race_filter = df['victim_race'] == selected_race if not all_race_filter else True
        sex_filter = df['victim_sex'] == selected_sex if not all_sex_filter else True

        filtered_df = df[city_filter & race_filter & sex_filter]
    return filtered_df


@app.callback(
    [Output('murder-map', 'figure'),
    Output('disp-colchart', 'figure'),
    Output('time-spiral', 'figure'),
    Output('sankey', 'figure')
    ],
    
    [Input('city_dropdown', 'value'),
     Input('race_dropdown', 'value'),
     Input('sex_dropdown', 'value')
    ]
)
def update_figs_on_dropdowns(selected_city, selected_race, selected_sex):
    filtered_df = filter_df(selected_city, selected_race, selected_sex)

    fig_map = make_map(filtered_df, selected_city)
    fig_col = make_colchart(filtered_df,selected_city)
    fig_spiral = make_spiral_plot(filtered_df)
    fig_sankey = make_sankey(filtered_df)
    return fig_map, fig_col, fig_spiral, fig_sankey


@app.callback(
    [Output('disp-colchart', 'figure', allow_duplicate = True),
     Output('time-spiral', 'figure', allow_duplicate = True),
     Output('sankey', 'figure', allow_duplicate = True)
     ], 
    [Input('murder-map', 'selectedData')],
    [State('city_dropdown', 'value'), State('race_dropdown', 'value'), State('sex_dropdown', 'value')],
    prevent_initial_call = True
)
def update_figures_on_map_selection(selected_data, selected_city, selected_race, selected_sex):
    if selected_data:
        # Extract the selected points from the map
        selected_points = selected_data['points']

        # Get the victim_full_name(s) from the selected points
        selected_names = [point['hovertext'] for point in selected_points]

        # Filter the DataFrame based on selected names, city, race, and sex
        filtered_df = df[df['victim_full_name'].isin(selected_names)]
        filtered_df = filter_df(selected_city, selected_race, selected_sex, filtered_df)

        # Generate new figs based on filtered data
        fig_col = make_colchart(filtered_df,selected_city)
        fig_spiral = make_spiral_plot(filtered_df)
        fig_sankey = make_sankey(filtered_df)
        return fig_col, fig_spiral, fig_sankey
    else:
        fig_col = make_colchart(filter_df(selected_city, selected_race, selected_sex),selected_city)
        fig_spiral = make_spiral_plot(filter_df(selected_city, selected_race, selected_sex))
        fig_sankey = make_sankey(filter_df(selected_city, selected_race, selected_sex))
        return fig_col, fig_spiral, fig_sankey
    



@app.callback(
    Output('city_dropdown', 'value'),
    Input('selected-city', 'data'),
    prevent_initial_call = True
)
def update_city_dropdown(selected_city):
    return selected_city

@app.callback(
    Output('selected-city', 'data'),
    [Input('murder-map', 'clickData')],
    [State('city_dropdown', 'value')]
)
def update_on_click(click_data, selected_city):
    if selected_city == 'all cities':
        if click_data:
            selected_city = click_data['points'][0]['hovertext']
            return selected_city
    raise PreventUpdate

@app.callback(
    [Output('murder-map', 'figure', allow_duplicate=True),
     Output('disp-colchart', 'figure', allow_duplicate = True),
     Output('sankey', 'figure', allow_duplicate = True)], 
    [Input('time-spiral', 'selectedData')],
    [State('city_dropdown', 'value'), State('race_dropdown', 'value'), State('sex_dropdown', 'value')],
    prevent_initial_call = True
)
def update_figs_on_spiral_select(selected_data, selected_city, selected_race, selected_sex):
    if selected_data: 
        d = selected_data['points']

        years = np.unique([y for y,m,n in [c['customdata'] for c in d]]).tolist()
        months = np.unique([m for y,m,n in [c['customdata'] for c in d]]).tolist()
        

        filtered_df = df[df['month2'].isin(months) & df['year'].isin(years)]
        filtered_df = filter_df(selected_city, selected_race, selected_sex, filtered_df)

        fig_map = make_map(filtered_df, selected_city)
        fig_col = make_colchart(filtered_df,selected_city)
        fig_sankey = make_sankey(filtered_df)
        return fig_map, fig_col, fig_sankey
    else:
        filtered_df = filter_df(selected_city, selected_race, selected_sex)

        fig_map = make_map(filtered_df, selected_city)
        fig_col = make_colchart(filtered_df,selected_city)
        fig_sankey = make_sankey(filtered_df)
        return fig_map, fig_col, fig_sankey

#####


@app.callback(
    Output('title-output', 'children'),
    [Input('city_dropdown', 'value')]
)
def update_title(city):
    city_list = [city for city in df['city'].unique()]
    if city in city_list:
        return f'Homicides in {city}' 
    else:
        return 'Homicides in 50 large cities in the US'


if __name__ == '__main__':
    app.run_server(debug=False, port = 8050)


