import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import date

# Streamlit configuration
st.set_page_config(page_title="Financial Dashboard", layout="wide", page_icon="📈")

# Sidebar for navigation
tabs = ["Home", "Forex", "Stocks", "Crypto", "Commodities", "Markets", "ETFs/Mutual Funds"]
selected_tab = st.sidebar.radio("Navigate", sorted(tabs, key=len))

# Date range selection
start_date = st.sidebar.date_input("Start Date", date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", date.today())

# Time increment selection
time_increments = ["Daily", "Weekly", "Monthly"]
selected_time_increment = st.sidebar.selectbox("Time Increment", time_increments)
time_increment_mapping = {"Daily": "1d", "Weekly": "1wk", "Monthly": "1mo"}
time_increment_for_yahoo = time_increment_mapping[selected_time_increment]

# NEW FEATURE CHECKBOXES
show_moving_average = st.sidebar.checkbox("Show 50-Day Moving Average", value=False)
compare_with_sp500 = st.sidebar.checkbox("Compare with S&P 500", value=False)

# Default tickers per category
tickers_map = {
    "Stocks": ["AAPL", "MSFT", "AMZN", "GOOGL", "NVDA", "TSLA", "META"],
    "Forex": ["EURUSD=X", "USDJPY=X", "GBPUSD=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "USDCHF=X"],
    "Crypto": ["BTC-USD", "ETH-USD", "USDT-USD", "BNB-USD", "XRP-USD", "ADA-USD", "DOGE-USD"],
    "Commodities": ["GLD", "SLV", "USO", "UNG", "PPLT", "COPX", "GDX"],
    "Markets": ["^GSPC", "^DJI", "^IXIC", "^FTSE", "^N225", "^HSI", "^GDAXI"],
    "ETFs/Mutual Funds": ["SPY", "VTI", "VOO", "QQQ", "ARKK", "IWM", "XLF"]
}

# ----------------------------- FETCH DATA -----------------------------
def fetch_data(tickers, start_date, end_date, time_increment):
    data = {}
    for ticker in tickers:
        try:
            df = yf.download(ticker, start=start_date, end=end_date, interval=time_increment, progress=False)
            if not df.empty:
                df = df.reset_index()
                # Ensure columns are 1D
                for col in ["Open", "High", "Low", "Close", "Volume"]:
                    if col in df.columns:
                        df[col] = df[col].squeeze()  # Flatten to 1D if necessary

                data[ticker] = df
            else:
                st.warning(f"No data available for {ticker}.")
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")
    return data

# ----------------------------- CALCULATIONS -----------------------------
def add_moving_average(df, window=50):
    """Add a 50-day moving average to a DataFrame if 'Close' exists."""
    if "Close" in df.columns:
        df["50-Day MA"] = df["Close"].rolling(window=window).mean()
    return df

# ----------------------------- PLOTTING -----------------------------
def plot_combined_data(data, title, show_ma=False):
    """Plot a single figure with all tickers' Close prices (and 50-Day MA if requested)."""
    combined_df = pd.DataFrame()
    all_dates = pd.concat([df["Date"] for df in data.values() if not df.empty]).drop_duplicates().sort_values()
    combined_df["Date"] = all_dates
    
    # Gather each ticker's Close and optional 50-Day MA
    for ticker, df in data.items():
        if not df.empty:
            df = df.set_index("Date").reindex(all_dates).reset_index()
            combined_df[ticker] = df["Close"].values

            # If 50-day MA is requested and exists
            if show_ma and "50-Day MA" in df.columns:
                combined_df[f"{ticker} 50-Day MA"] = df["50-Day MA"].values

    if not combined_df.empty:
        # Melt to long form
        combined_df = combined_df.melt(id_vars=["Date"], var_name="Symbol", value_name="Price")
        fig = px.line(combined_df, x="Date", y="Price", color="Symbol", title=title)
        return fig
    else:
        st.warning("No data available for the selected symbols.")
        return None

def plot_individual_data(data, ticker, show_ma=False):
    """Plot each ticker individually with optional 50-day MA overlay."""
    df = data.get(ticker)
    if df is not None and not df.empty:
        # Flatten if needed
        close_prices = df["Close"].values.flatten()
        fig = px.line(df, x="Date", y=close_prices, title=f"{ticker} Prices", labels={"y": "Price", "x": "Date"})
        
        # If user wants to see 50-day MA and it's present
        if show_ma and "50-Day MA" in df.columns:
            # Flatten the MA series just in case
            ma_values = df["50-Day MA"].values.flatten()
            fig.add_scatter(x=df["Date"], y=ma_values, mode="lines", name="50-Day MA")
        
        return fig
    else:
        st.warning(f"No data available for {ticker}.")
        return None

# ----------------------------- MAIN LOGIC -----------------------------
if selected_tab == "Home":
    st.title("Financial Dashboard")
    st.markdown(
        """
        Welcome to the Financial Dashboard! This is a demonstration project showcasing financial data analysis capabilities.

        ### Features:
        - Analyze data for Stocks, Forex, Cryptocurrencies, Commodities, Markets, and ETFs/Mutual Funds.
        - Combined and individual visualizations for easy comparison and detailed insights.
        - Interactive and user-friendly interface.

        ### Skills Demonstrated:
        - Python Programming
        - Data Analysis with Pandas
        - Financial Data Retrieval using Yahoo Finance API
        - Interactive Visualizations with Plotly
        - Web App Development with Streamlit

        ### Usage:
        - Use the sidebar to navigate between different financial data categories.
        - View combined plots for all default symbols.
        - Select individual symbols for detailed analysis using the subtabs above the chart.
        - Double click to select and deselect tickers for detailed comparisons.
        """
    )

elif selected_tab:
    st.title(f"{selected_tab}")

    # Gather user tickers
    default_symbols = tickers_map[selected_tab]
    user_input = st.sidebar.text_input(
        f"Enter {selected_tab} symbols (comma-separated):", ",".join(default_symbols)
    )
    user_tickers = [ticker.strip() for ticker in user_input.split(",") if ticker.strip()]

    # Compare with S&P 500 if checked
    if compare_with_sp500 and "^GSPC" not in user_tickers:
        user_tickers.append("^GSPC")

    # Fetch data
    data = fetch_data(user_tickers, start_date, end_date, time_increment_for_yahoo)

    # Add 50-day moving average if requested
    if show_moving_average:
        for tkr, df_tkr in data.items():
            if not df_tkr.empty:
                data[tkr] = add_moving_average(df_tkr)

    if data:
        # Create tabs for combined and individual
        tab_names = ["Combined"] + user_tickers
        tabs = st.tabs(tab_names)

        # Combined data tab
        with tabs[0]:
            fig = plot_combined_data(data, f"{selected_tab} Combined Prices", show_ma=show_moving_average)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        # Individual data tabs
        for i, ticker in enumerate(user_tickers):
            with tabs[i + 1]:
                fig = plot_individual_data(data, ticker, show_ma=show_moving_average)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data retrieved for the selected tickers.")
