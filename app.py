import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# External stylesheets for readability and design
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
app.title = "Financial Dashboard"

# Placeholder data
stocks_data = pd.DataFrame({
    "Symbol": ["AAPL", "MSFT", "AMZN", "GOOGL", "NVDA"],
    "Close Price": [230, 250, 3300, 2800, 700],
    "Change (%)": [1.5, 1.5, -0.5, 2, 3]
})

crypto_data = pd.DataFrame({
    "Crypto": ["Bitcoin", "Ethereum", "Tether", "BNB", "XRP"],
    "Price (USD)": [50000, 3500, 1, 400, 0.5],
    "Change (%)": [1.2, -0.3, 0.0, 2.1, 3.5]
})

commodities_data = pd.DataFrame({
    "Commodity": ["Gold", "Silver", "Crude Oil", "Natural Gas", "Platinum"],
    "Price (USD)": [1800, 23, 80, 3.5, 900],
    "Change (%)": [0.5, -0.2, 1.1, -0.4, 2.3]
})

# Layout components
tabs = dbc.Tabs([
    dbc.Tab(label="Stocks", tab_id="stocks", active_label_style={"fontWeight": "bold", "color": "yellow"}),
    dbc.Tab(label="Markets", tab_id="markets", active_label_style={"fontWeight": "bold", "color": "yellow"}),
    dbc.Tab(label="Crypto", tab_id="crypto", active_label_style={"fontWeight": "bold", "color": "yellow"}),
    dbc.Tab(label="Forex", tab_id="forex", active_label_style={"fontWeight": "bold", "color": "yellow"}),
    dbc.Tab(label="Commodities", tab_id="commodities", active_label_style={"fontWeight": "bold", "color": "yellow"})
])

app.layout = dbc.Container(
    [
        html.H1("Financial Dashboard", className="text-center text-warning my-4"),
        tabs,
        html.Div(id="content", className="mt-4"),
    ],
    fluid=True,
    className="bg-dark text-light",
)

# Callbacks for dynamic content
@callback(Output("content", "children"), [Input(tabs, "active_tab")])
def update_content(active_tab):
    if active_tab == "stocks":
        fig = px.bar(stocks_data, x="Symbol", y="Close Price", color="Change (%)",
                     title="Top 5 Stocks", labels={"Close Price": "Price (USD)"})
        return html.Div([
            html.H3("Top 5 Stocks", className="text-warning"),
            dbc.Table.from_dataframe(stocks_data, bordered=True, dark=True, striped=True),
            dcc.Graph(figure=fig)
        ])
    elif active_tab == "crypto":
        fig = px.line(crypto_data, x="Crypto", y="Price (USD)", color="Change (%)",
                      title="Top Cryptocurrencies")
        return html.Div([
            html.H3("Top Cryptocurrencies", className="text-warning"),
            dbc.Table.from_dataframe(crypto_data, bordered=True, dark=True, striped=True),
            dcc.Graph(figure=fig)
        ])
    elif active_tab == "commodities":
        fig = px.bar(commodities_data, x="Commodity", y="Price (USD)", color="Change (%)",
                     title="Commodities Overview")
        return html.Div([
            html.H3("Commodities Data", className="text-warning"),
            dbc.Table.from_dataframe(commodities_data, bordered=True, dark=True, striped=True),
            dcc.Graph(figure=fig)
        ])
    elif active_tab == "forex":
        forex_data = pd.DataFrame({
            "Currency Pair": ["USD/EUR", "USD/JPY", "USD/GBP", "USD/AUD"],
            "Rate": [0.85, 110, 0.72, 1.35],
            "Change (%)": [0.1, 0.05, -0.2, 0.5]
        })
        fig = px.line(forex_data, x="Currency Pair", y="Rate", title="Forex Rates")
        return html.Div([
            html.H3("Forex Data", className="text-warning"),
            dbc.Table.from_dataframe(forex_data, bordered=True, dark=True, striped=True),
            dcc.Graph(figure=fig)
        ])
    elif active_tab == "markets":
        markets_data = pd.DataFrame({
            "Index": ["S&P 500", "Nasdaq", "FTSE 100", "DAX", "Nikkei", "Hang Seng"],
            "Price": [4500, 15000, 7500, 16000, 29000, 20000],
            "Change (%)": [0.5, 1.2, -0.3, 0.4, 0.8, -0.1]
        })
        fig = px.bar(markets_data, x="Index", y="Price", color="Change (%)",
                     title="Global Market Indices")
        return html.Div([
            html.H3("Global Markets", className="text-warning"),
            dbc.Table.from_dataframe(markets_data, bordered=True, dark=True, striped=True),
            dcc.Graph(figure=fig)
        ])
    return html.Div("Select a tab to view data.", className="text-warning")

if __name__ == "__main__":
    app.run_server(debug=True)
