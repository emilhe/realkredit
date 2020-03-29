import dash
import dash_core_components as dcc
import dash_html_components as html

from flask import Flask
from dash.exceptions import PreventUpdate
from dash.dependencies import Output, Input
from datetime import datetime as datetime, timedelta
from data_helpers import fetch_data, parse_data

# Component IDs.
DD_ID = "dd-id"
GRAPH_ID = "graph-id"
STORE_ID = "store-id"
LABEL_ID = "label-id"
DATE_PICKER_ID = "date-picker-id"

# Data mappings.
instrument_mappings = {
    "05NYK01EA50": "XCSE0%3A5NYK01EA50",
    "1NYK01EA50": "XCSE1NYK01EA50",
    "15NYK01EA50": "XCSE1%3A5NYK01EDA50",
    "20NYK01EA50": "XCSE2NYK01EA50",
}
label_mappings = {
    "05NYK01EA50": "0.5% 30 år",
    "1NYK01EA50": "1.0%  30 år",
    "15NYK01EA50": "1.5%  30 år",
    "20NYK01EA50": "2.0%  30 år",
}
dt_format = "%Y-%m-%d"
all_targets = ["05NYK01EA50", "1NYK01EA50", "15NYK01EA50", "20NYK01EA50"]

# Default values.
default_dt_to = datetime.today()
dt = timedelta(days=0)
if default_dt_to.weekday() == 5:  # saturday
    dt = timedelta(days=1)
if default_dt_to.weekday() == 6:  # sunday
    dt = timedelta(days=2)
default_dt_from = (datetime.now() - dt)
default_targets = ["1NYK01EA50", "15NYK01EA50"]


def make_figure_and_label_data(dt_from, dt_to, targets):
    graph_data = []
    label_data = {}
    for key in targets:
        data = fetch_data(dt_from, dt_to, instrument_mappings[key])
        times, prices = parse_data(data)
        graph_data.append(dict(x=times, y=prices, name=label_mappings[key], mode='lines+markers'))
        label_data[key] = (times[-1], prices[-1])
    graph_layout = dict(title="Kurser på danske realkredit obligationer",
                        xaxis=dict(title="Tid"), yaxis=dict(title="Kurs"))
    hide_labels = [key not in targets for key in all_targets]
    labels = ["{}: {} @ {}".format(label_mappings[key], label_data[key][1], label_data[key][0].strftime(dt_format))
              if key in targets else "" for key in all_targets]
    return dict(data=graph_data, layout=graph_layout), labels, hide_labels


def label_id(key):
    return "{}{}".format(LABEL_ID, key)


# Get initial data.
figure, labels, hide_labels = make_figure_and_label_data(default_dt_from, default_dt_to, default_targets)
# Create app.
server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"])
app.layout = html.Div([
    html.Div([
        dcc.DatePickerRange(id=DATE_PICKER_ID, start_date=default_dt_from, end_date=default_dt_to,
                            max_date_allowed=default_dt_to),
        dcc.Dropdown(options=[{"value": key, "label": label_mappings[key]} for key in all_targets],
                     multi=True, value=default_targets, id=DD_ID)
    ], style={"display": "grid", "grid-template-columns": "1fr 5fr", "grid-gap": "10px"}),
    dcc.Graph(id=GRAPH_ID, figure=figure),
    dcc.Markdown("**Seneste kurser**"),
    html.Div([html.P(labels[i], hidden=hide_labels[i], id=label_id(key)) for i, key in enumerate(all_targets)])
])


@app.callback([Output(GRAPH_ID, "figure")] + [Output(label_id(key), "children") for key in all_targets] +
              [Output(label_id(key), "hidden") for key in all_targets],
              [Input(DATE_PICKER_ID, 'start_date'), Input(DATE_PICKER_ID, 'end_date'), Input(DD_ID, "value")])
def update_figure(str_from, str_to, targets):
    if str_from is None or str_to is None:
        raise PreventUpdate
    dt_from = datetime.strptime(str_from.split("T")[0], dt_format)
    dt_to = datetime.strptime(str_to.split("T")[0], dt_format)
    figure, labels, hide_labels = make_figure_and_label_data(dt_from, dt_to, targets)
    return [figure] + labels + hide_labels


if __name__ == '__main__':
    app.run_server(debug=True)
