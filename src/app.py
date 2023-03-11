# pip install dash  (2.1 or higher)
import datetime
import dash
from dash import html, dcc, Input, Output, State, dash_table
# pip install pandas
import pandas as pd
import plotly.express as px
# pip install "pymongo[srv]"
import pymongo
from bson.objectid import ObjectId

# Connect to server on the cloud
client = pymongo.MongoClient(
    "mongodb+srv://Kriss:Kriss206206@cluster0.rauq32w.mongodb.net/?retryWrites=true&w=majority")
db = client["NDT"]
collection = db["NDT"]
app = dash.Dash(__name__, suppress_callback_exceptions=True,
                external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
server = app.server

app.layout = html.Div([

    html.Div(id='mongo-datatable', children=[]),

    # activated once/week or when page refreshed
    dcc.Interval(id='interval_db', interval=86400000 * 7, n_intervals=0),

    html.Button("Save csv to DB", id="save-csv",),
    html.Button("Save above table to csv & DB", id="save-it"),
    html.Button('Add Row', id='adding-rows-btn', n_clicks=0),

    html.Div(id='markdown-csv'),
    html.Div(id='markdown-it'),

    html.Div(id="placeholder"),
    html.Div(id="placeholder2")

])

# Display Datatable with data from Mongo database *************************


@app.callback(Output('mongo-datatable', 'children'),
              [Input('interval_db', 'n_intervals')])
def populate_datatable(n_intervals):
    # Convert the Collection (table) date to a pandas DataFrame
    df = pd.DataFrame(list(collection.find()))
    # Drop the _id column generated automatically by Mongo
    df = df.iloc[:, 1:]

    return [
        dash_table.DataTable(
            id='my-table',
            columns=[{
                'name': x,
                'id': x,
            } for x in df.columns],
            data=df.to_dict('records'),
            editable=True,
            row_deletable=True,
            filter_action="native",
            filter_options={"case": "sensitive"},
            sort_action="native",  # give user capability to sort columns
            sort_mode="single",  # sort across 'multi' or 'single' columns
            page_current=0,  # page number that user is on
            page_size=1000,  # number of rows visible per page
            style_cell={'textAlign': 'left', 'minWidth': '100px',
                        'width': '100px', 'maxWidth': '100px'},
        )
    ]

# Add new rows to DataTable ***********************************************


@app.callback(
    Output('my-table', 'data'),
    [Input('adding-rows-btn', 'n_clicks')],
    [State('my-table', 'data'),
     State('my-table', 'columns')],
)
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


# Save new DataTable data to the Mongo database ***************************
@app.callback(
    Output("placeholder", "children"),
    Output("markdown-it", "children"),
    Input("save-it", "n_clicks"),
    State("my-table", "data"),
    prevent_initial_call=True
)
def save_data(n_clicks, data):
    dff = pd.DataFrame(data)
    collection.delete_many({})
    collection.insert_many(dff.to_dict('records'))

    dff.to_csv('.\\src\\parameters.csv', index=False)

    return "", dcc.Markdown(f'Saved Table {datetime.datetime.now()}')


# Save new DataTable data to the Mongo database ***************************
@app.callback(
    Output("placeholder2", "children"),
    Output("markdown-csv", "children"),
    Input("save-csv", "n_clicks"),
    prevent_initial_call=True
)
def save_data(n_clicks):
    parameters = pd.read_csv('.\\src\\parameters.csv')
    collection.delete_many({})
    collection.insert_many(parameters.to_dict('records'))

    return "", dcc.Markdown(f'Saved CSV {datetime.datetime.now()}')


if __name__ == '__main__':
    app.run_server(debug=True)
