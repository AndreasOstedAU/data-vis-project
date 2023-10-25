from turtle import width
import pandas as pd
from dash import dcc
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output
import plotly.express as px
import numpy as np

print("new run")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
data = pd.read_csv("https://raw.githubusercontent.com/AndreasOstedAU/data-vis-project/main/Data/homicide_data.csv")


grouped_df = data[['victim_age', 'victim_race', 'victim_first', 'city', 'victim_sex']].groupby(['victim_race','victim_age','city', 'victim_sex'], as_index = False)['victim_first'].count()
grouped_df = grouped_df.rename(columns={"victim_first":"count"})

mask = grouped_df['victim_age'] == 'Unknown'
grouped_df = grouped_df[~mask]

grouped_df['victim_age'] = pd.to_numeric(grouped_df['victim_age'])

arrest = data["disposition"]
raceall = data["victim_race"]
race = np.unique(raceall)
sexall = data["victim_sex"]
sex = np.unique(sexall)

raceoptions=[{'label': 'Select all', 'value': 'All races'}]+[{'label': r, 'value': r} for r in race]
sexoptions=[{'label': 'Select all', 'value': 'All sexes'}]+[{'label': r, 'value': r} for r in sex]
cityoptions=[{'label': 'Select all', 'value': 'all_values'}]+[{'label': city, 'value': city} for city in sorted(data['city'].unique())]

original_data = grouped_df
current_data = grouped_df
current_race = 'All races'
current_sex = 'All sexes'

# all vendors sales pie chart
def race_pie_all():
    df = grouped_df.groupby('victim_race').sum().reset_index()
    fig = px.pie(df, names='victim_race',
                 values='count', hole=0.4, 
                 category_orders={"victim_race": ['Asian' 'Black' 'Hispanic' 'Other' 'Unknown' 'White']},
                 color_discrete_sequence=["deeppink", "blue", "orange", "purple", "red","green"])
    fig.update_layout(template='presentation', title='Homicides by race')
    fig.update_traces(textfont_size=10, marker=dict(line=dict(color='#000000', width=1)))
    return fig


def age_hist_all():
    df = grouped_df.groupby('victim_age').sum().reset_index()
    fig = px.histogram(df, x='victim_age',
                 y='count', color_discrete_sequence=["lightgrey"])
    fig.update_layout(template='presentation', title='Homicides by age')
    return fig

city_list = sorted(grouped_df.city.unique())

def city_bar_all():
    df = grouped_df.groupby('city').sum().reset_index()
    fig = px.bar(df, y='city',
                 x='count', color='city',
                 category_orders={"city": city_list}, color_discrete_sequence=["lightgrey"])
    fig.update_layout(template='presentation', title='Homicides by city', showlegend=False, yaxis={'automargin': True})
    return fig

# creating app layout
app.layout = dbc.Container([
    dbc.Card([
            dbc.Button('Go back to overview', id='back-button', outline=False, size="sm",
                       className='mt-2 ml-2 col-1', style={'display': 'none'}, color="black"),
            dbc.Row([dcc.Dropdown(
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
        ),]),
            dbc.Row([
            dbc.Col([
                dcc.Graph(
                        id='graph',
                        figure=age_hist_all()
            )], width=6
            ),
            dbc.Col([
                dcc.Graph(
                        id='graphage',
                        figure=city_bar_all()
            )], width=6
            )
            ,]),
            dbc.Row(
                dcc.Graph(
                        id='graphcity',
                        figure=race_pie_all(),
                        style={"width": "1200px"}
                    ), justify='center', style={"height": "1500px"}
            ),
    ], className='mt-3')
])

#Callback
@app.callback(
    Output('graph', 'figure'),
    Output('graphage', 'figure'),
    Output('graphcity', 'figure'),
    Output('back-button', 'style'), #to hide/unhide the back button
    Output('race-dropdown', 'value'),
    Input('graph', 'clickData'),    #for getting the vendor name from graph
    Input('back-button', 'n_clicks'),
    Input("race-dropdown", "value"),
    Input("sex-dropdown", "value"),
    Input("city-dropdown", "value")
)
def drilldown(click_data, n_clicks, selected_race, selected_sex, selected_city):

    # using callback context to check which input was fired
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    global current_data
    global current_race
    global current_sex

    if trigger_id == 'graph':

        # get vendor name from clickData
        if click_data is not None:
            race = click_data['points'][0]['label']

            if race in data.victim_race.unique():
                # creating df for clicked race
                current_race = race
                current_data = grouped_df[grouped_df['victim_race'] == race].sort_values(by=['victim_age'])
                if current_sex != "All sexes":
                    current_data = current_data[current_data['victim_sex'] == current_sex]

                index_col_list = ["deeppink", "blue", "orange", "purple", "red","green"]
                index_chosen_race_list = grouped_df.victim_race.unique()
                index_chosen_race = np.where(index_chosen_race_list == race)[0][0]
                print(index_chosen_race)

                # generating product sales bar graph
                fig = px.histogram(current_data, x='victim_age',
                             y='count', color='victim_race', color_discrete_sequence=[index_col_list[index_chosen_race]])

                fig.update_layout(title='<b>Homicides by age<b>',
                                  showlegend=False, template='presentation')
            

                col_list = ["lightgrey", "lightgrey", "lightgrey", "lightgrey", "lightgrey"]
                col_list.insert(index_chosen_race, index_col_list[index_chosen_race])
                print(col_list)

                pie_fig = px.pie(grouped_df, names='victim_race',
                                    values='count', hole=0.4, color_discrete_sequence=col_list, category_orders={"victim_race": ['Asian' 'Black' 'Hispanic' 'Other' 'Unknown' 'White']})
                pie_fig.update_traces(textfont_size=10, marker=dict(line=dict(color='#000000', width=1)))
                pie_fig.update_layout(template='presentation', title='<b>Homicides by race <b>')

                city_fig = px.bar(current_data.groupby('city').sum().reset_index(), y='city',
                                    x='count', category_orders={"city": city_list}, color_discrete_sequence=[index_col_list[index_chosen_race]])
                city_fig.update_layout(template='presentation', title='<b>Homicides by city <b>', yaxis={'automargin': True})
                return pie_fig, fig, city_fig, {'display':'block'}, race  #returning the fig and unhiding the back button

            else:
                current_data = original_data
                return race_pie_all(), age_hist_all(), city_bar_all(), {'display': 'none'}, 'Select all'     #hiding the back button

    if trigger_id == "race-dropdown":
        current_race = selected_race
        if selected_race is None:
            selected_race = raceall[0]["value"]  # Set default race

        if selected_race=="All races":
            current_data=grouped_df.sort_values(by=['victim_age'])
            if current_sex != "All sexes":
                current_data = current_data[current_data['victim_sex'] == current_sex]
            col_list = ["deeppink", "blue", "orange", "purple", "red","green"]
            chosen_color = "lightgrey"
        else:
            current_data = grouped_df[grouped_df['victim_race'] == selected_race].sort_values(by=['victim_age'])
            if current_sex != "All sexes":
                current_data = current_data[current_data['victim_sex'] == current_sex]
            index_col_list = ["deeppink", "blue", "orange", "purple", "red","green"]
            index_chosen_race_list = grouped_df.victim_race.unique()
            index_chosen_race = np.where(index_chosen_race_list == selected_race)[0][0]
            chosen_color = index_col_list[index_chosen_race]
            col_list = ["lightgrey", "lightgrey", "lightgrey", "lightgrey", "lightgrey"]
            col_list.insert(index_chosen_race, chosen_color)
        
        # generating product sales bar graph
        fig_hist = px.histogram(current_data, x='victim_age',
                        y='count', color='victim_race', color_discrete_sequence=[chosen_color])

        fig_hist.update_layout(title='<b>Homicides by age<b>',
                            showlegend=False, template='presentation')

        print(col_list)

        fig_pie = px.pie(grouped_df, names='victim_race',
                            values='count', hole=0.4, color_discrete_sequence=col_list, category_orders={"victim_race": ['Asian' 'Black' 'Hispanic' 'Other' 'Unknown' 'White']})
        fig_pie.update_traces(textfont_size=10, marker=dict(line=dict(color='#000000', width=1)))
        fig_pie.update_layout(template='presentation', title='<b>Homicides by race <b>')

        city_fig = px.bar(current_data.groupby('city').sum().reset_index(), y='city',
                            x='count', category_orders={"city": city_list}, color_discrete_sequence=[chosen_color])
        city_fig.update_layout(template='presentation', title='<b>Homicides by city <b>', yaxis={'automargin': True})

        return fig_pie, fig_hist, city_fig, {'display':'block'}, selected_race

    if trigger_id == "sex-dropdown":
        current_sex = selected_sex
        print(current_sex)
        if selected_sex is None:
            selected_sex = sexall[0]["value"]  # Set default race

        if selected_sex=="All sexes":
            current_data=grouped_df.sort_values(by=['victim_age'])
            gender_df = grouped_df.sort_values(by=['victim_age'])
            if current_race != "All races":
                current_data = current_data[current_data['victim_race'] == current_race]
                index_col_list = ["deeppink", "blue", "orange", "purple", "red","green"]
                index_chosen_race_list = grouped_df.victim_race.unique()
                index_chosen_race = np.where(index_chosen_race_list == current_race)[0][0]
                chosen_color = index_col_list[index_chosen_race]
                col_list = ["lightgrey", "lightgrey", "lightgrey", "lightgrey", "lightgrey"]
                col_list.insert(index_chosen_race, chosen_color)
            else:
                col_list = ["deeppink", "blue", "orange", "purple", "red","green"]
                chosen_color = "lightgrey"
        else:
            gender_df = grouped_df[grouped_df['victim_sex'] == selected_sex].sort_values(by=['victim_age'])
            current_data = grouped_df[grouped_df['victim_sex'] == selected_sex].sort_values(by=['victim_age'])
            if current_race != "All races":
                current_data = current_data[current_data['victim_race'] == current_race]
                index_col_list = ["deeppink", "blue", "orange", "purple", "red","green"]
                index_chosen_race_list = grouped_df.victim_race.unique()
                index_chosen_race = np.where(index_chosen_race_list == current_race)[0][0]
                chosen_color = index_col_list[index_chosen_race]
                col_list = ["lightgrey", "lightgrey", "lightgrey", "lightgrey", "lightgrey"]
                col_list.insert(index_chosen_race, chosen_color)
            else:
                col_list = ["deeppink", "blue", "orange", "purple", "red","green"]
                chosen_color = "lightgrey"
            
        # generating product sales bar graph
        fig_hist = px.histogram(current_data, x='victim_age',
                        y='count', color='victim_race', color_discrete_sequence=[chosen_color])

        fig_hist.update_layout(title='<b>Homicides by age<b>',
                            showlegend=False, template='presentation')


        fig_pie = px.pie(gender_df, names='victim_race',
                            values='count', hole=0.4, color_discrete_sequence=col_list, category_orders={"victim_race": ['Asian' 'Black' 'Hispanic' 'Other' 'Unknown' 'White']})
        fig_pie.update_traces(textfont_size=10, marker=dict(line=dict(color='#000000', width=1)))
        fig_pie.update_layout(template='presentation', title='<b>Homicides by race<b>')

        city_fig = px.bar(current_data.groupby('city').sum().reset_index(), y='city',
                            x='count', category_orders={"city": city_list}, color_discrete_sequence=[chosen_color])
        city_fig.update_layout(template='presentation', title='<b>Homicides by city <b>', yaxis={'automargin': True})

        return fig_pie, fig_hist, city_fig, {'display':'block'}, selected_race

    else:
        print(trigger_id)
        current_data = original_data
        return race_pie_all(), age_hist_all(), city_bar_all(), {'display':'none'}, 'Select all'



if __name__ == '__main__':
    app.run(debug=True)