import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import threading
import paho.mqtt.client as mqtt
import json
import time
from collections import deque

# Store incoming data
data_buffer = deque(maxlen=1000)

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Real-Time Machine Sensor Dashboard"

# Layout
app.layout = html.Div([
    html.H1("Live Machine Sensor Data", style={'textAlign': 'center'}),
    
    dcc.Dropdown(id='machine-dropdown', placeholder="Select a Machine"),
    dcc.Graph(id='live-graph'),
    
    html.H3("Live Sensor Data Table"),
    dash_table.DataTable(
        id='live-data-table',
        columns=[
            {'name': 'Timestamp', 'id': 'timestamp'},
            {'name': 'Machine ID', 'id': 'machine_id'},
            {'name': 'Temperature', 'id': 'temperature'},
            {'name': 'Pressure', 'id': 'pressure'},
            {'name': 'Vibration', 'id': 'vibration'}
        ],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center'},
        page_size=10,
    ),

    html.Br(),
    html.Button("Download CSV", id="btn-download"),
    dcc.Download(id="download-dataframe-csv"),

    dcc.Interval(id='update-interval', interval=2000, n_intervals=0)
])

# Load machine IDs for dropdown
@app.callback(
    Output('machine-dropdown', 'options'),
    Input('update-interval', 'n_intervals')
)
def load_machine_dropdown(_):
    if not data_buffer:
        return []
    df = pd.DataFrame(list(data_buffer))
    options = [{'label': m, 'value': m} for m in sorted(df['machine_id'].unique())]
    return options

# Update graph and table
@app.callback(
    [Output('live-graph', 'figure'),
     Output('live-data-table', 'data')],
    [Input('update-interval', 'n_intervals'),
     Input('machine-dropdown', 'value')]
)
def update_graph(n, selected_machine):
    if not data_buffer:
        return px.scatter(title="Waiting for data..."), []

    df = pd.DataFrame(list(data_buffer))
    if selected_machine:
        df = df[df['machine_id'] == selected_machine]

    fig = px.line(df, x='timestamp', y=['temperature', 'pressure', 'vibration'], 
                  title=f"Live Sensor Readings - Machine {selected_machine or 'All'}")

    return fig, df.tail(10).to_dict('records')

# Export to CSV
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn-download", "n_clicks"),
    prevent_initial_call=True
)
def download_data(n_clicks):
    df = pd.DataFrame(list(data_buffer))
    return dcc.send_data_frame(df.to_csv, "live_machine_data.csv")

# MQTT callback functions
def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected to MQTT broker")
    client.subscribe("factory/machine")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        payload['timestamp'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        data_buffer.append(payload)
    except Exception as e:
        print(f"Error in message handling: {e}")

# Start MQTT Client in separate thread
def mqtt_thread():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("test.mosquitto.org", 1883, 60)
    client.loop_forever()

threading.Thread(target=mqtt_thread, daemon=True).start()

# Run the Dash app
if __name__ == '__main__':
    app.run(debug=False)
