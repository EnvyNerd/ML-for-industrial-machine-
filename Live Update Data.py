import dash
from dash import dcc, html, Input, Output, State, ctx
from dash import dash_table
import pandas as pd
import plotly.graph_objects as go
import io
import base64

# Initialize Dash
app = dash.Dash(__name__)
app.title = "Real-Time Machine Sensor Dashboard"

# Layout
app.layout = html.Div([
    html.H1("📡 Real-Time Machine Sensor Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select Machine:"),
        dcc.Dropdown(id='machine-dropdown', options=[], value=None, style={'width': '300px'}),
    ], style={'padding': '20px'}),

    dcc.Graph(id='live-sensor-graph'),
    html.Div(id='live-alert-output', style={'color': 'red', 'textAlign': 'center'}),

    html.Hr(),

    html.Div([
        html.H4("📋 Live Sensor Data Table"),
        dash_table.DataTable(
            id='sensor-table',
            columns=[],
            data=[],
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
            filter_action="native",
            sort_action="native",
        ),
        html.Br(),
        html.Div([
            html.Button("⬇ Export CSV", id="btn-csv"),
            html.Button("⬇ Export Excel", id="btn-xlsx"),
            dcc.Download(id="download-data")
        ], style={'marginTop': '10px'})
    ], style={'padding': '20px'}),

    dcc.Interval(id='interval-component', interval=3000, n_intervals=0)
])

# Update dropdown with available machine IDs
@app.callback(
    [Output('machine-dropdown', 'options'),
     Output('machine-dropdown', 'value')],
    Input('interval-component', 'n_intervals')
)
def load_machine_dropdown(_):
    df = pd.read_csv("https://raw.githubusercontent.com/EnvyNerd/ML-for-industrial-machine-/refs/heads/main/Machine_sensor_data.csv")
    machine_ids = sorted(df['machine_id'].unique())
    options = [{"label": m, "value": m} for m in machine_ids]
    return options, machine_ids[0] if machine_ids else None

# Update graph, alerts, table
@app.callback(
    [Output('live-sensor-graph', 'figure'),
     Output('live-alert-output', 'children'),
     Output('sensor-table', 'columns'),
     Output('sensor-table', 'data')],
    [Input('interval-component', 'n_intervals'),
     Input('machine-dropdown', 'value')]
)
def update_live_outputs(n, machine_id):
    if not machine_id:
        return go.Figure(), "No machine selected.", [], []

    df = pd.read_csv("https://raw.githubusercontent.com/EnvyNerd/ML-for-industrial-machine-/refs/heads/main/Machine_sensor_data.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    dff = df[df['machine_id'] == machine_id]

    # Graph
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dff['timestamp'], y=dff['temperature'], mode='lines', name='Temperature'))
    fig.add_trace(go.Scatter(x=dff['timestamp'], y=dff['pressure'], mode='lines', name='Pressure'))
    fig.add_trace(go.Scatter(x=dff['timestamp'], y=dff['vibration'], mode='lines+markers', name='Vibration', marker=dict(color='orange')))
    fig.add_trace(go.Scatter(x=dff['timestamp'], y=dff['rpm'], mode='lines', name='RPM'))

    # Alert condition
    alert_df = dff[dff['vibration'] > 1.0]
    if not alert_df.empty:
        fig.add_trace(go.Scatter(x=alert_df['timestamp'], y=alert_df['vibration'],
                                 mode='markers', name='⚠️ High Vibration',
                                 marker=dict(color='red', size=10, symbol='x')))
        alert_msg = f"⚠️ ALERT: {len(alert_df)} high vibration points (> 1 mm/s)"
    else:
        alert_msg = "✅ Vibration Normal"

    fig.update_layout(title=f"Live Sensor Data for {machine_id}",
                      xaxis_title="Timestamp",
                      yaxis_title="Sensor Value",
                      template='plotly_dark')

    # Data table
    columns = [{"name": col, "id": col} for col in dff.columns]
    data = dff.sort_values("timestamp", ascending=False).head(100).to_dict("records")

    return fig, alert_msg, columns, data

# Export CSV or Excel
@app.callback(
    Output("download-data", "data"),
    [Input("btn-csv", "n_clicks"),
     Input("btn-xlsx", "n_clicks")],
    State("machine-dropdown", "value"),
    prevent_initial_call=True
)
def export_data(csv_clicks, xlsx_clicks, machine_id):
    df = pd.read_csv("https://raw.githubusercontent.com/EnvyNerd/ML-for-industrial-machine-/refs/heads/main/Machine_sensor_data.csv")
    dff = df[df["machine_id"] == machine_id]

    trigger_id = ctx.triggered_id
    if trigger_id == "btn-csv":
        return dcc.send_data_frame(dff.to_csv, filename=f"{machine_id}_data.csv", index=False)
    elif trigger_id == "btn-xlsx":
        return dcc.send_data_frame(dff.to_excel, filename=f"{machine_id}_data.xlsx", index=False)

# Run the app
app.run_server(debug=False)

