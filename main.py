import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash
from dash import html, dcc, Output, Input
import urllib
import re

data = pd.read_csv("dataset_ts.csv", sep=";")

# Read the data and preprocess
def preprocess_data():
    # Read the data into a DataFrame and grop the cities
    data = pd.read_csv("dataset_ts.csv", sep=";")
    city_sales = data.groupby('city')['tick_sales'].sum().reset_index()

    # Preprocessing songs
    songs_1 = data[['city', 'surp_1']].dropna()
    songs_2 = data[['city', 'surp_2']].dropna()

    songs_1['surp_1'] = songs_1['surp_1'].str.replace(r"[!?]", "", regex=True)
    songs_2['surp_2'] = songs_2['surp_2'].str.replace(r"[!?]", "", regex=True)

    songs_1['surp_1'] = songs_1['surp_1'].str.split(' / ')
    songs_2['surp_2'] = songs_2['surp_2'].str.split(' / ')

    songs_1 = songs_1.explode('surp_1').rename(columns={'surp_1': 'Song'})
    songs_2 = songs_2.explode('surp_2').rename(columns={'surp_2': 'Song'})

    # Combine the two song lists into a single DataFrame
    song_plays = pd.concat([songs_1, songs_2])

    # Count song occurrences
    song_counts_df = song_plays['Song'].value_counts().reset_index()
    song_counts_df.columns = ['Song', 'Count']

    # Map song to cities
    song_to_cities = song_plays.groupby('Song')['city'].apply(list).to_dict()

    # Map data for coordinates
    coordinates = data[["city", "x", "y"]]

    return city_sales, song_counts_df, coordinates, song_to_cities

city_sales, song_counts_df, coordinates, song_to_cities = preprocess_data()

def tour_map(locations):

    map_fig = go.Figure()

    map_fig.add_trace(go.Scattergeo(
        lon = locations["x"],
        lat = locations["y"],
        text = locations["city"],  # Appears on hover
        mode = 'markers',
        marker = dict(size=15, color='red'),
        hoverinfo = 'text',
    ))

    map_fig.update_layout(
        title={
            "text": "Eras Tour Map",
            "font": {"family": "Times New Roman, Times, serif", "size": 80, "color": "black"}
        },
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(
            showland=True,
            landcolor="rgb(217, 217, 217)",
            projection_type="natural earth",
            bgcolor="rgba(0,0,0,0)",
            oceancolor="#ffffff",
            showocean=True,
            projection=dict(scale=1.8),  # Adjust to fit your points better
            center=dict(lat=30, lon=-15),
            resolution=50,  # Higher resolution for a cleaner map
        ),
        hoverlabel=dict(
        font_size=60),
        margin={"l": 0, "r": 0, "t": 120, "b": 0},  # Remove excess margins
        )
    return map_fig

map_fig = tour_map(coordinates)

def create_bar_chart(df, x, y, title, val, var):
    fig = px.bar(df, x=x, y=y,
                barmode='group', title=title,
                 labels={'value': val, 'variable': var})
    
    fig.update_layout(
        xaxis_title="City",
        yaxis_title="Tickets sold",
        paper_bgcolor="#ffffff",
        width=5500,
        height=1600,
        font_size=45,
        title={
            "font": {"family": "Times New Roman, Times, serif",
                     "size": 80,
                     "color": "black"}
        },
        hoverlabel=dict(
        font_size=60))
    fig.update_traces(
        marker_color="#ff6279"
    )

    return fig

def create_city_chart(df, x, y, title, val, var):
    fig = px.bar(df, x=x, y=y,
                barmode='group', title=title,
                 labels={'value': val, 'variable': var})
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Tickets sold",
        paper_bgcolor="#ffffff",
        width=2000,
        height=1000,
        font_size=45,
        title={
            "font": {"family": "Times New Roman, Times, serif",
                     "size": 80,
                     "color": "black"}
        },
        hoverlabel=dict(
        font_size=60))
    
    fig.update_traces(
        marker_color="#ff6279"
    )

    return fig

def surprise_song_list(city):
    def encode_song_name(song):
        # Replace problematic characters with URL-safe versions
        # Remove special characters that can break the URL
        safe_song = re.sub(r"[?!&%#/@:;]", "", song)
        return urllib.parse.quote_plus(safe_song.strip())
    
    if city == "general":
        song_list = [
            html.Li(
                dcc.Link(
                    f"{row['Song']} ({row['Count']})", 
                    href=f"/song/{encode_song_name(row['Song'])}"
                )
            )
            for _, row in song_counts_df.iterrows()
        ]

    return [html.H2(f"How many times each surprise song was played:",style={"fontSize":"60px"}),
            html.H3(f"Click to see in which cities.",style={"fontSize":"50px"}),
            html.Ul(song_list)]


# 1. Bar Chart of City Sales
ticket_sale_fig = create_bar_chart(city_sales, 'city', 'tick_sales', 'Ticket sale in each concert', 'Sales ($)', 'Category')

app = dash.Dash(
    __name__,
    requests_pathname_prefix="/IDV_Eras_Tour_Tool/"
)

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    
    # Main Page Content
    html.Div(id="main_page", children=[
        html.H1("Oh hi! Welcome to the Eras Tour (Data Visualization's Version)!"),
        
        html.Div([
            dcc.Graph(id="world-map", figure=map_fig, 
                      style={"flex": "1", "height": "80vh", "minWidth": "60%"}), 
            html.Div(id="general_song_list", 
                style={
                    "flex": "1",
                    "paddingLeft": "50px",
                    "maxHeight": "30vh",
                    "overflowY": "auto",
                    "border": "1px solid #ccc",
                    "padding": "10px",
                    "borderRadius": "8px",
                    "backgroundColor": "#ffffff",
                    "fontSize": "70px",
                    "minWidth": "30%"
                })
        ], style={"display":"flex", "flexDirection":"row", "gap":"20px"}),
    ], style={"marginBottom": "20px"}),

    # Ticket Sales Chart
    html.Div(id="general_charts", children=[
        dcc.Graph(id="general_ticket_sale", figure=ticket_sale_fig)
    ], style={
        "marginTop": "20px",
        "width": "100%",
        "padding": "20px",
        "backgroundColor": "#ffffff",
        "borderRadius": "8px",
        "boxShadow": "0 2px 15px rgba(0,0,0,0.15)"
    }),
    # City Page (Hidden by Default)
    html.Div(id="city_page", style={"display": "none", "marginTop": "20px"})
])

@app.callback(
    [
        Output("main_page", "style"),
        Output("city_page", "style"),
        Output("city_page", "children"),
        Output("general_song_list", "children"),
        Output("general_charts", "style")
    ],
    [
        Input("world-map", "clickData"),
        Input("url", "pathname")
    ]
)

def display_city_info(clickData, pathname):
    if pathname and pathname.startswith("/song/"):
        # Decode the song name and remove the special character filter
        song_name = urllib.parse.unquote_plus(pathname.split("/song/")[1])
        if song_name in song_to_cities:
            cities = song_to_cities[song_name]
            return {"display": "none"}, {"display": "block"}, song_page(song_name, cities), [], {"display": "none"}

    if (clickData is None) and (pathname == "/"):
        return {"display": "block"}, {"display": "none"}, [], surprise_song_list("general"), {"display": "block"}

    if clickData:
        city = clickData["points"][0]["text"]
        return {"display": "none"}, {"display": "block"}, city_page(city), [], {"display": "none"}

    if pathname and pathname != "/":
        city = pathname.strip("/")
        return {"display": "none"}, {"display": "block"}, city_page(city), [], {"display": "none"}

    return {"display": "block"}, {"display": "none"}, [], surprise_song_list("general"), {"display": "block"}


def song_page(song_name, cities):
    return [
        html.H1(f"{song_name} - Eras Tour Data", style={"fontSize":"60px"}),
        html.Ul([html.Li(city) for city in cities], style={"fontSize":"100px", "paddingLeft":"20px"}),
        html.A("Back to main page", href="/", style={"marginTop": "20px", "display": "block", "fontSize":"50px"})
    ]


def city_page(city):
    data = pd.read_csv("dataset_ts.csv", sep=";")
    city_stats = data.loc[data["city"]==city]
    city_chart = create_city_chart(city_stats, 'date', 'tick_sales', f'Ticket sales in {city}', 'Sales ($)', 'Category')
    
    songs = city_stats[['surp_1','surp_2','date']]
    songs  = songs.sort_values(by="date")
    songs_list = []

    for index, row in songs.iterrows():
        date = html.H3(row['date'])
        surp1= html.Li(row['surp_1'])
        surp2= html.Li(row['surp_2'])
        songs_list.append(date)
        songs_list.append(surp1)
        songs_list.append(surp2)

    return [html.H1(f"{city} - Eras Tour Data"),
            html.Div([
                html.Div(dcc.Graph(figure=city_chart), style={"flex":"1"}),
                html.Div([
                    html.H2("Surprise Songs", style={"fontSize":"70px"}),
                    html.Ul(songs_list, style={"fontSize":"60px", "paddingLeft":"80px"})],
                    style={
                        "flex":"1",
                        "border":"1px solid #ccc",
                        "padding":"10px",
                        "borderRadius":"8px",
                        "backgroundColor":"#ffffff"})],
                    style={"display":"flex", "flexDirection":"row", "gap":"20px"}),
                html.A("Back to main page", href="/", style={"marginTop": "20px", "display": "block", "fontSize":"50px"})]

# Run the server
if __name__ == "__main__":
    with open("index.html", "w") as f:
        f.write(app.index())
    print("Exported to index.html")