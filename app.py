import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Static placeholder data for each section
stocks_data = pd.DataFrame({
    "Symbol": ["AAPL", "MSFT", "AMZN", "GOOGL", "NVDA"],
    "Close Price": [230, 250, 3300, 2800, 700],
    "Change (%)": [1.5, 1.5, -0.5, 2.0, 3.0]
})

crypto_data = pd.DataFrame({
    "Crypto": ["Bitcoin", "Ethereum", "Tether", "BNB", "XRP"],
    "Price (USD)": [50000, 3500, 1, 400, 0.5],
    "Change (%)": [1.2, -0.3, 0.0, 2.1, 3.5]
})

forex_data = pd.DataFrame({
    "Currency Pair": ["USD/EUR", "USD/JPY", "USD/GBP", "USD/AUD"],
    "Rate": [0.85, 110, 0.72, 1.35],
    "Change (%)": [0.1, 0.05, -0.2, 0.5]
})

commodities_data = pd.DataFrame({
    "Commodity": ["Gold", "Silver", "Crude Oil", "Natural Gas", "Platinum"],
    "Price (USD)": [1800, 23, 70, 4, 900],
    "Change (%)": [0.5, -0.3, 1.2, 0.8, -0.4]
})

market_data = pd.DataFrame({
    "Index": ["S&P 500", "NASDAQ", "Dow Jones", "FTSE 100", "DAX", "Nikkei 225", "Hang Seng", "CAC 40"],
    "Price (USD)": [4700, 15500, 34700, 7400, 16100, 32000, 18000, 7200],
    "Change (%)": [0.75, 1.2, 0.5, -0.3, 0.8, 1.1, -0.4, 0.6]
})

# App layout
app.layout = html.Div([
    html.H1("Financial Dashboard", style={"textAlign": "center", "color": "white"}),

    # Navigation Tabs
    dcc.Tabs(id="tabs", value="stocks", children=[
        dcc.Tab(label="Stocks", value="stocks"),
        dcc.Tab(label="Markets", value="markets"),
        dcc.Tab(label="Crypto", value="crypto"),
        dcc.Tab(label="Forex", value="forex"),
        dcc.Tab(label="Commodities", value="commodities"),
    ], colors={
        "border": "black",
        "primary": "orange",
        "background": "gray"
    }),

    # Content Area
    html.Div(id="tab-content", style={"padding": "20px"})
])

# Callback to update content based on the selected tab
@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "value")]
)
def render_content(tab_name):
    if tab_name == "stocks":
        return html.Div([
            html.H2("Top Stocks", style={"color": "orange"}),
            dbc.Table.from_dataframe(stocks_data, striped=True, bordered=True, hover=True, className="table-dark"),
            dcc.Graph(
                id="stocks-graph",
                figure=px.line(
                    stocks_data, x="Symbol", y="Close Price", title="Stock Prices",
                    labels={"Close Price": "Price (USD)", "Symbol": "Stock Symbol"}
                )
            )
        ])
    elif tab_name == "markets":
        return html.Div([
            html.H2("Global Market Indices", style={"color": "orange"}),
            dbc.Table.from_dataframe(market_data, striped=True, bordered=True, hover=True, className="table-dark"),
            dcc.Graph(
                id="markets-graph",
                figure=px.bar(
                    market_data, x="Index", y="Price (USD)", color="Change (%)",
                    title="Global Market Indices",
                    labels={"Price (USD)": "Price (USD)", "Change (%)": "Change (%)"}
                )
            )
        ])
    elif tab_name == "crypto":
        return html.Div([
            html.H2("Top Cryptocurrencies", style={"color": "orange"}),
            dbc.Table.from_dataframe(crypto_data, striped=True, bordered=True, hover=True, className="table-dark"),
            dcc.Graph(
                id="crypto-graph",
                figure=px.bar(
                    crypto_data, x="Crypto", y="Price (USD)", color="Change (%)",
                    title="Top Cryptocurrencies",
                    labels={"Price (USD)": "Price (USD)", "Change (%)": "Change (%)"}
                )
            )
        ])
    elif tab_name == "forex":
        return html.Div([
            html.H2("Forex Data", style={"color": "orange"}),
            dbc.Table.from_dataframe(forex_data, striped=True, bordered=True, hover=True, className="table-dark"),
            dcc.Graph(
                id="forex-graph",
                figure=px.line(
                    forex_data, x="Currency Pair", y="Rate", title="Forex Exchange Rates",
                    labels={"Rate": "Rate (USD)", "Currency Pair": "Currency Pair"}
                )
            )
        ])
    elif tab_name == "commodities":
        return html.Div([
            html.H2("Commodities Data", style={"color": "orange"}),
            dbc.Table.from_dataframe(commodities_data, striped=True, bordered=True, hover=True, className="table-dark"),
            dcc.Graph(
                id="commodities-graph",
                figure=px.bar(
                    commodities_data, x="Commodity", y="Price (USD)", color="Change (%)",
                    title="Top Commodities",
                    labels={"Price (USD)": "Price (USD)", "Change (%)": "Change (%)"}
                )
            )
        ])

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
