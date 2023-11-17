from email import header
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import json, urllib
import pandas as pd

app = Dash(__name__)

app.layout = html.Div([
    html.H4('Murders in America'),
    dcc.Graph(id="graph", style={"height": "70vh"}),
    html.P("Opacity"),
    dcc.Slider(id='slider', min=0, max=1, 
               value=0.5, step=0.1)
])

def genSankey(df,cat_cols=[],value_cols='',title='Sankey Diagram'):
    df['victim_age'].mask(df['victim_age'] == 'Unknown', 0, inplace=True)
    mask = df['victim_age'] == 0
    df = df[~mask]
    df['victim_sex'].mask(df['victim_sex'] == 'Unknown', 'Unknown sex', inplace=True)
    df['victim_race'].mask(df['victim_race'] == 'Unknown', 'Unknown race', inplace=True)
    df['victim_age'] = pd.to_numeric(df['victim_age'])
    df['age_binned'] = pd.cut(x=df['victim_age'], bins=[-1,9,19, 29, 39, 49, 59, 69, 79, 89, 99, 109], labels=['1-9','10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-99','100+'])
    df = df.sort_values(by=['victim_age'], ascending=True)
    df = df.groupby(['disposition','victim_race','victim_sex','age_binned']).size().reset_index(name='n_obs')

    # maximum of 6 value cols -> 6 colors
    colorPalette = ['#000000','#000000','#000000','#000000','#000000']
    labelList = []
    colorNumList = []
    for catCol in cat_cols:
        labelListTemp =  list(set(df[catCol].values))
        if catCol=='age_binned':
            labelListTemp = ['1-9','10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-99','100+']
        colorNumList.append(len(labelListTemp))
        labelList = labelList + labelListTemp
        
    # remove duplicates from labelList
    del labelList[12:23]
    labelList = list(dict.fromkeys(labelList))
    labelList = labelList + ['1-9','10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-99','100+']
    
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
    raceList = list(df['victim_race'].unique())
    ageList = list(df['age_binned'].unique())
    presentList = dispList + genderList + raceList + ageList
    x = [0.001, 0.001, 0.001, 0.33, 0.33, 0.33, 0.66, 0.66, 0.66, 0.66, 0.66, 0.66, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999]
    y = [0.3, 0.5, 0.8, 0.2, 0.6, 0.8, 0.1, 0.3, 0.4, 0.6, 0.8, 0.9, 0.001, 1/10, 2/10, 3/10, 4/10, 5/10, 6/10, 7/10, 8/10, 9/10, 0.999]
    deleteList = []

    allList = ['Closed by arrest','Open/No arrest', 'Closed without arrest', 'Male', 'Female', 'Unknown sex', 'Black', 'Hispanic', 'White', 'Other', 'Asian', 'Unknown race','1-9','10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-99','100+']
    
    for i in range(len(allList)):
        if allList[i] not in presentList:
            deleteList.append(i)
    
    for j in range(len(deleteList)):
        del allList[deleteList[j]-j]
        del y[deleteList[j]-j]
        del x[deleteList[j]-j]

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
        color = colorList,
        label = labelList
    ),
    link = dict(
          source = sourceTargetDf['sourceID'],
          target = sourceTargetDf['targetID'],
          value = sourceTargetDf['count']
        ))])
       
    #fig = go.sankey(dict(data=[data], layout=layout))

    return fig

data = pd.read_csv("https://raw.githubusercontent.com/AndreasOstedAU/data-vis-project/main/Data/homicide_data.csv")
data['victim_age'].mask(data['victim_age'] == 'Unknown', 0, inplace=True)
mask = data['victim_age'] == 0
data = data[~mask]
data['victim_sex'].mask(data['victim_sex'] == 'Unknown', 'Unknown sex', inplace=True)
data['victim_race'].mask(data['victim_race'] == 'Unknown', 'Unknown race', inplace=True)
data['victim_age'] = pd.to_numeric(data['victim_age'])
data['age_binned'] = pd.cut(x=data['victim_age'], bins=[-1,9,19, 29, 39, 49, 59, 69, 79, 89, 99, 109], labels=['1-9','10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-99','100+'])
data = data.sort_values(by=['victim_age'], ascending=True)
grouped_df = data.groupby(['disposition','victim_race','victim_sex','age_binned']).size().reset_index(name='n_obs')
#grouped_df = grouped_df.rename(columns={"uid":"count"})
#print(grouped_df['n_obs'].sum())
#print(grouped_df.sum())
data = pd.read_csv("https://raw.githubusercontent.com/AndreasOstedAU/data-vis-project/main/Data/homicide_data.csv")
grouped_df = data

#my_sankey = get_sankey(grouped_df, ['disposition','victim_sex','victim_race','age_binned'],'count')

@app.callback(
    Output("graph", "figure"), 
    Input("slider", "value"))


def display_sankey(opacity):
    return genSankey(grouped_df,['disposition','victim_sex','victim_race','age_binned'],'n_obs')

app.run_server(debug=True)