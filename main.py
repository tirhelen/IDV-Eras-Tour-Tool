import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash
from dash import html, dcc, Output, Input

# Read the data and create a DataFrame
def preprocess_data():
    data = pd.read_csv("dataset_ts.csv", sep=";")
    print(data.columns)

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
        title = 'Eras Tour Map',
        geo = dict(
            showland = True,
            landcolor = "rgb(217, 217, 217)",
            projection_type = "natural earth"
        )
    )
    return map_fig

map_fig = tour_map(coordinates)

def create_bar_chart(df, x, y, title, val, var):
    fig = px.bar(df, x=x, y=y,
                barmode='group', title=title,
                 labels={'value': val, 'variable': var})
    return fig

# 1. Bar Chart of City Sales
ticket_sale_fig = create_bar_chart(city_sales, 'city', 'tick_sales', 'Ticket sale in each concerts', 'Sales ($)', 'Category')

# 2. Bar Chart of Surprise Songs
surprs_fig = create_bar_chart(song_counts_df, 'Song', 'Count', 'How many times each Surprise song was played?', 'Song', 'Category')

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(figure=map_fig),
    dcc.Graph(figure=ticket_sale_fig),
    dcc.Graph(figure=surprs_fig)
])

"""
app.layout = html.Div([
    html.H1(children="Oh hi! Welcome to the Eras Tour (Data Visualition's Version)!"),
    dcc.Graph(id="world-map", figure=map_fig),
    html.Div(id="info-box", style={"marginTop": "20px", "fontSize": "18px"})
])"""

@app.callback(
    Output("info-box", "children"),
    Input("world-map", "clickData")
)


def display_city_info(clickData):
    if clickData is None:
        return "Click a city to see more details."
    city = clickData["points"][0]["text"]

    return city


# Run the server
if __name__ == '__main__':
    app.run(debug=True)