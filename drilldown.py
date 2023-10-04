import pandas as pd
from dash import dcc
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output
import plotly.express as px
import numpy as np


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
data = pd.read_csv("https://raw.githubusercontent.com/AndreasOstedAU/data-vis-project/main/Data/homicide_data.csv")


grouped_df = data[['victim_age', 'victim_race', 'victim_first', 'city']].groupby(['victim_race','victim_age','city'], as_index = False)['victim_first'].count()
grouped_df = grouped_df.rename(columns={"victim_first":"count"})

mask = grouped_df['victim_age'] == 'Unknown'
# select all rows except the ones that contain 'Coca Cola'
grouped_df = grouped_df[~mask]

grouped_df['victim_age'] = pd.to_numeric(grouped_df['victim_age'])
print(grouped_df.victim_race.unique())


# all vendors sales pie chart
def race_pie():
    df = grouped_df.groupby('victim_race').sum().reset_index()
    fig = px.pie(df, names='victim_race',
                 values='count', hole=0.4, 
                 category_orders={"victim_race": ['Asian' 'Black' 'Hispanic' 'Other' 'Unknown' 'White']})
    fig.update_layout(template='presentation', title='Homicides per race')
    fig.update_traces(textfont_size=10, marker=dict(line=dict(color='#000000', width=1)))
    return fig


def age_hist():
    df = grouped_df.groupby('victim_age').sum().reset_index()
    fig = px.histogram(df, x='victim_age',
                 y='count')
    fig.update_layout(template='presentation', title='Homicides per age')
    return fig

city_list = sorted(grouped_df.city.unique())
print(city_list)

def city_bar():
    df = grouped_df.groupby('city').sum().reset_index()
    fig = px.bar(df, x='city',
                 y='count', color='city',
                 category_orders={"city": city_list})
    fig.update_layout(template='presentation', title='Homicides per city', showlegend=False)
    return fig

# creating app layout
app.layout = dbc.Container([
    dbc.Card([
            dbc.Button('Go back to overview', id='back-button', outline=False, size="sm",
                       className='mt-2 ml-2 col-1', style={'display': 'none'}, color="primary"),
            dbc.Row([
            dbc.Col([
                dcc.Graph(
                        id='graph',
                        figure=age_hist()
            )], width=6
            ),
            dbc.Col([
                dcc.Graph(
                        id='graphage',
                        figure=city_bar()
            )], width=6
            )
            ,]),
            dbc.Row(
                dcc.Graph(
                        id='graphcity',
                        figure=race_pie()
                    ), justify='center'
            ),
    ], className='mt-3')
])

#Callback
@app.callback(
    Output('graph', 'figure'),
    Output('graphage', 'figure'),
    Output('graphcity', 'figure'),
    Output('back-button', 'style'), #to hide/unhide the back button
    Input('graph', 'clickData'),    #for getting the vendor name from graph
    Input('back-button', 'n_clicks')
)
def drilldown(click_data, n_clicks):

    # using callback context to check which input was fired
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == 'graph':

        # get vendor name from clickData
        if click_data is not None:
            race = click_data['points'][0]['label']

            if race in data.victim_race.unique():
                # creating df for clicked race
                race_df = grouped_df[grouped_df['victim_race'] == race].sort_values(by=['victim_age'])

                # generating product sales bar graph
                fig = px.histogram(race_df, x='victim_age',
                             y='count', color='victim_race', color_discrete_sequence=["blue"])
                fig.update_layout(title='<b>{} - Homicides by age<b>'.format(race),
                                  showlegend=False, template='presentation')

                index_chosen_race_list = grouped_df.victim_race.unique()
                index_chosen_race = np.where(index_chosen_race_list == race)[0][0]
                print(index_chosen_race)

                col_list = ["lightgrey", "lightgrey", "lightgrey", "lightgrey", "lightgrey"]
                col_list.insert(index_chosen_race, "blue")
                print(col_list)

                pie_fig = px.pie(grouped_df, names='victim_race',
                                    values='count', hole=0.4, color_discrete_sequence=col_list, category_orders={"victim_race": ['Asian' 'Black' 'Hispanic' 'Other' 'Unknown' 'White']})
                pie_fig.update_traces(textfont_size=10, marker=dict(line=dict(color='#000000', width=1)))

                city_fig = px.bar(race_df.groupby('city').sum().reset_index(), x='city',
                                    y='count', category_orders={"city": city_list}, color_discrete_sequence=["blue"])
                city_fig.update_layout(template='presentation', title='<b>{} - Homicides per city <b>'.format(race))
                return pie_fig, fig, city_fig, {'display':'block'}     #returning the fig and unhiding the back button

            else:
                return race_pie(), age_hist(), city_bar(), {'display': 'none'}     #hiding the back button

    else:
        return race_pie(), age_hist(), city_bar(), {'display':'none'}

if __name__ == '__main__':
    app.run(debug=True)