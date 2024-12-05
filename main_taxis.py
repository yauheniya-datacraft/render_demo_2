# Plotly and Dash 2: Callbacks

# 1. Modulimporte
#import warnings
#warnings.filterwarnings("ignore", category=DeprecationWarning)

from dash import Dash, dcc, html, Input, Output, callback, dash_table
import plotly.express as px
import pandas as pd
import geopandas as gpd
import geodatasets
import json
import seaborn as sns

# 2. App erstellen
app = Dash(__name__, title="Taxis Dashboard")
server = app.server
# 3. Daten vorbereiten
df = sns.load_dataset("taxis")
df['pickup']=pd.to_datetime(df['pickup'])

pfad = geodatasets.get_path("nybb")
data_nyc = gpd.read_file(pfad)
central_boroughs = data_nyc[data_nyc['BoroName'].isin(['Manhattan', 'Brooklyn', 'Bronx', 'Queens'])]

central_boroughs = central_boroughs.to_crs(epsg=4326)
geojson = json.loads(central_boroughs.to_json())

print(central_boroughs)
# 4. App-Komponenten definieren
fig_nyc = px.choropleth_mapbox(
    central_boroughs, 
    geojson=geojson, 
    locations='BoroCode', 
    featureidkey='properties.BoroCode',
    color='BoroName',opacity=0.5, 
    mapbox_style='carto-darkmatter',
    zoom=9,
    center={"lat":40.7128, "lon":-74.0060}, 
    labels={'BoroName':'Borough'}
)

# 5. App-Layout zusammensetzen
app.layout = html.Div([
    html.Div([
        html.H1("NYC Taxi Dashboard"),
        html.Br(),
        html.Br(),
        dash_table.DataTable(data=df.to_dict('records'), page_size=5,
                                style_table={'overflowX':'auto'}),
        dcc.Graph(id='nyc-karte', figure=fig_nyc, style={'height':'600px'}),
        html.Div(id='borough-stats'),
        html.Br(),
        html.Br()
    ], style={
    'backgroundColor':'white',
    'width':'100%',
    'maxWidth':'800px',
    'text-align':'center',
    'padding':'20px'
    })
], style={
    'backgroundColor':'black',
    'min-height':'100vh',
    'width':'100%',
    'display':'flex',
    'justify-content':'center',
    'margin': '0 !important', 
    'padding': '0 !important'
})

# 6. Callbacks
@callback(
    Output('borough-stats','children'),
    Input('nyc-karte','clickData')
)
def zeige_statistik(klick):
    if klick is None:
        return "Klicke auf die Karte, um die Statistik für den Berzirk anzeigen zu lassen"
    
    boro_code = klick['points'][0]['location']
    boro_name = central_boroughs.loc[central_boroughs['BoroCode']==boro_code, 'BoroName'].values[0]
    
    bezirksdaten = df[df['pickup_borough'] == boro_name]

    total_fare = bezirksdaten['fare'].sum()
    total_trips = bezirksdaten['fare'].count()
    total_distance = bezirksdaten['distance'].sum()

    statistik = [
        html.P(f"Bezirk: {boro_name}", style={'font-weight':'bold'}),
        html.P(f"Gesamteinnahmen: ${total_fare:,.2f}"),
        html.P(f"Anzahl der Fahrten: {total_trips:,.0f}"),
        html.P(f"Gesamtdistanz: {total_distance:,.0f} Meilen"),
        html.P(f"Durchschnittlicher Preis: ${total_fare/total_trips:.2f}"),
        html.P(f"Durchschnittlicher Distanz: {total_distance/total_trips:.0f} Meilen")
    ]

    return statistik

# Die if __name__ == "__main__": Abfrage 

if __name__ == "__main__":
    app.run(debug=True)
