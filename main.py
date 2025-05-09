import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash
from dash import html, dcc, Output, Input

data = pd.read_csv("dataset_ts.csv", sep=";")

# Read the data and create a DataFrame
def preprocess_data():
    data = pd.read_csv("dataset_ts.csv", sep=";")

    city_sales = data.groupby('city')['tick_sales'].sum().reset_index()

    # Preprocessing songs
    songs_1 = data['surp_1'].dropna().str.split(' / ')
    songs_2 = data['surp_2'].dropna().str.split(' / ')

    # Flatten both lists
    all_songs = songs_1.explode().tolist() + songs_2.explode().tolist()

    song_counts = pd.Series(all_songs).value_counts()

    song_counts_df = song_counts.reset_index()
    song_counts_df.columns = ['Song', 'Count']

    # Map data
    coordinates = data[["city", "x", "y"]]

    return city_sales, song_counts_df, coordinates

city_sales, song_counts_df, coordinates = preprocess_data()

def tour_map(locations):

    map_fig = go.Figure()

    map_fig.add_trace(go.Scattergeo(
        lon = locations["x"],
        lat = locations["y"],
        text = locations["city"],  # Appears on hover
        mode = 'markers',
        marker = dict(size=8, color='red'),
        hoverinfo = 'text',
    ))

    map_fig.update_layout(
        title={"text":"Eras Tour Map",
               "font": {"family": "Times New Roman, Times, serif",
                "size": 28,"color": "black"}},
        paper_bgcolor="#ffb6c1",
        width=2000,
        height=900,
        geo = dict(
            showland = True,
            landcolor = "rgb(217, 217, 217)",
            projection_type = "natural earth",
            bgcolor="#ffb6c1",
            oceancolor="#ffffff",
            showocean=True
        )
    )
    return map_fig

map_fig = tour_map(coordinates)

def create_bar_chart(df, x, y, title, val, var):
    fig = px.bar(df, x=x, y=y,
                barmode='group', title=title,
                 labels={'value': val, 'variable': var})
    fig.update_layout(
        paper_bgcolor="#ffffff",
        width=2000,
        height=900,
        font_size=25,
        title={
            "font": {"family": "Times New Roman, Times, serif",
                     "size": 28,
                     "color": "black"}
        }
    )
    fig.update_traces(
        marker_color="#ff6279"
    )

    return fig

# 1. Bar Chart of City Sales
ticket_sale_fig = create_bar_chart(city_sales, 'city', 'tick_sales', 'Ticket sale in each concerts', 'Sales ($)', 'Category')

# 2. Bar Chart of Surprise Songs
#surprs_fig = create_bar_chart(song_counts_df, 'Song', 'Count', 'How many times each Surprise song was played?', 'Song', 'Category')

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="main_page", children=[
    html.H1("Oh hi! Welcome to the Eras Tour (Data Visualition's Version)!"),
    html.Div(dcc.Graph(id="world-map", figure=map_fig)),
    html.Div(
        children=[
            html.Div(dcc.Graph(id="general_ticket_sale",figure=ticket_sale_fig), className="graphs")],
            #html.Div(dcc.Graph(id="general_surpr_songs", figure=surprs_fig), className="graphs")],
        id="general_charts",
        style={"marginTop":"20px"})], style={"display":"block"}),
    
    html.Div(id="city_page", style={"display": "none", "marginTop": "20px"})])

@app.callback(
        [Output("main_page", "style"),
        Output("city_page", "style"),
        Output("city_page", "children")],
        [Input("world-map", "clickData"),
        Input("url", "pathname")]) 

def display_city_info(clickData, pathname):

    if (clickData is None) and (pathname=="/"):
        return {"display": "block"}, {"display": "none"}, []
    if clickData:
        city = clickData["points"][0]["text"]
        return {"display": "none"}, {"display": "block"}, city_page(city)
    if pathname and pathname != "/":
        city=pathname.strip("/")
        return {"display": "none"}, {"display": "block"}, city_page(city)

    return {"display": "block"}, {"display": "none"}, []


def city_page(city):
    data = pd.read_csv("dataset_ts.csv", sep=";")
    city_stats = data.loc[data["city"]==city]
    city_chart = create_bar_chart(city_stats, 'date', 'tick_sales', f'Ticket sales in {city}', 'Sales ($)', 'Category')
    
    songs_1 = city_stats['surp_1']
    songs_2 = city_stats['surp_2']
    #songs_1 = list(city_stats['surp_1'].str.split(' / '))
    #songs_2 = list(city_stats['surp_2'].str.split(' / '))
    song_list = [html.Li(x) for x in songs_1]
    song_list += [html.Li(x) for x in songs_2]

    return [html.H1(f"{city} - Eras Tour Data"),
            dcc.Graph(figure=city_chart),
            html.H2("Surprise Songs"),
            html.Ul(song_list),
            html.A("Back to main page", href="/", style={"marginTop": "20px", "display": "block"})]

# Run the server
if __name__ == '__main__':
    app.run(debug=True)