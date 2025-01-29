import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import math
from datetime import date

# ------------------ 1. TECHNICAL INDICATORS ------------------ #
def add_moving_average(df, window=50):
    """Adds a 50-day MA column."""
    if "Close" in df.columns:
        df["50-Day MA"] = df["Close"].rolling(window=window).mean()
    return df

def compute_rsi(series, period=14):
    """Compute the Relative Strength Index (RSI)."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def add_rsi(df, period=14):
    """Adds RSI column to the dataframe."""
    if "Close" in df.columns:
        df["RSI"] = compute_rsi(df["Close"], period=period)
    return df

def compute_bollinger_bands(series, window=20):
    """Returns (SMA, Upper Band, Lower Band)."""
    sma = series.rolling(window).mean()
    std = series.rolling(window).std()
    upper_band = sma + 2 * std
    lower_band = sma - 2 * std
    return sma, upper_band, lower_band

def add_bollinger_bands(df, window=20):
    """Adds Bollinger Band columns to the dataframe."""
    if "Close" in df.columns:
        sma, upper, lower = compute_bollinger_bands(df["Close"], window)
        df["BB_Mid"] = sma
        df["BB_Upper"] = upper
        df["BB_Lower"] = lower
    return df

def force_1d(df):
    """
    Ensures all numeric columns are flattened to 1D 
    to avoid ValueError: Data must be 1-dimensional.
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].ndim > 1:
            df[col] = df[col].values.ravel()
    return df

# ------------------ 2. STREAMLIT CONFIG ------------------ #
st.set_page_config(page_title="Financial Dashboard", layout="wide", page_icon="📈")

tabs = ["Home", "Forex", "Stocks", "Crypto", "Commodities", "Markets", "ETFs/Mutual Funds"]
selected_tab = st.sidebar.radio("Navigate", sorted(tabs, key=len))

start_date = st.sidebar.date_input("Start Date", date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", date.today())

time_increments = ["Daily", "Weekly", "Monthly"]
selected_time_increment = st.sidebar.selectbox("Time Increment", time_increments)
time_increment_mapping = {"Daily": "1d", "Weekly": "1wk", "Monthly": "1mo"}
time_increment_for_yahoo = time_increment_mapping[selected_time_increment]

# Optional feature toggles
show_moving_average = st.sidebar.checkbox("Show 50-Day Moving Average", value=False)
compare_with_sp500 = st.sidebar.checkbox("Compare with S&P 500", value=False)
show_rsi = st.sidebar.checkbox("Show RSI", value=False)
show_bollinger = st.sidebar.checkbox("Show Bollinger Bands", value=False)

# Default tickers per category
tickers_map = {
    "Stocks": ["AAPL", "MSFT", "AMZN", "GOOGL", "NVDA", "TSLA", "META"],
    "Forex": ["EURUSD=X", "USDJPY=X", "GBPUSD=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "USDCHF=X"],
    "Crypto": ["BTC-USD", "ETH-USD", "USDT-USD", "BNB-USD", "XRP-USD", "ADA-USD", "DOGE-USD"],
    "Commodities": ["GLD", "SLV", "USO", "UNG", "PPLT", "COPX", "GDX"],
    "Markets": ["^GSPC", "^DJI", "^IXIC", "^FTSE", "^N225", "^HSI", "^GDAXI"],
    "ETFs/Mutual Funds": ["SPY", "VTI", "VOO", "QQQ", "ARKK", "IWM", "XLF"]
}

# ------------------ 3. DATA FETCHING ------------------ #
def fetch_data(tickers, start_date, end_date, interval):
    data = {}
    for ticker in tickers:
        try:
            df = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                interval=interval,
                group_by=False,
                progress=False
            )
            if not df.empty:
                df = df.reset_index(drop=False)

                # Flatten any tuple columns into strings, e.g. ('Close','SPY') -> "Close_SPY"
                flattened_cols = []
                for col in df.columns:
                    if isinstance(col, tuple):
                        flat_col = "_".join(str(x) for x in col if x)
                        flattened_cols.append(flat_col)
                    else:
                        flattened_cols.append(str(col))
                df.columns = flattened_cols

                # Rename "TICKER_Close" -> "Close", etc.
                prefix = f"{ticker}_"
                rename_map = {col: col.replace(prefix, "") for col in df.columns if col.startswith(prefix)}
                df.rename(columns=rename_map, inplace=True)

                df = force_1d(df)
                data[ticker] = df
            else:
                st.warning(f"No data available for {ticker}.")
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")
    return data

# ------------------ 4. PLOTTING ------------------ #
def plot_combined_data(data_dict, title, show_ma=False, show_rsi=False, show_boll=False):
    combined_df = pd.DataFrame()
    all_dates = pd.concat(
        [df["Date"] for df in data_dict.values() if not df.empty]
    ).drop_duplicates().sort_values()
    combined_df["Date"] = all_dates

    for ticker, df in data_dict.items():
        if not df.empty:
            df = df.set_index("Date").reindex(all_dates).reset_index()
            df = force_1d(df)
            if "Close" in df.columns:
                combined_df[ticker] = df["Close"]
            if show_ma and "50-Day MA" in df.columns:
                combined_df[f"{ticker} 50-Day MA"] = df["50-Day MA"]

    if combined_df.shape[1] > 1:  # 'Date' + something else
        melted_df = combined_df.melt(
            id_vars=["Date"],
            var_name="Symbol",
            value_name="Price"
        )
        fig = px.line(
            melted_df,
            x="Date",
            y="Price",
            color="Symbol",
            title=title
        )
        st.download_button(
            label="Download Combined Data as CSV",
            data=combined_df.to_csv(index=False).encode("utf-8"),
            file_name="combined_data.csv",
            mime="text/csv",
        )
        return fig
    else:
        st.warning("No data available for the selected symbols.")
        return None

def plot_correlation_heatmap(data_dict):
    """Create a correlation heatmap based on daily returns."""
    returns_series_list = []

    for ticker, df in data_dict.items():
        if not df.empty:
            df = force_1d(df)
            df = df.sort_values("Date")
            if "Close" in df.columns:
                df["Returns"] = df["Close"].pct_change()
                returns_series = df.set_index("Date")["Returns"].rename(ticker)
                returns_series_list.append(returns_series)

    if len(returns_series_list) < 2:
        return None

    returns_df = pd.concat(returns_series_list, axis=1).dropna()
    corr_matrix = returns_df.corr()

    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu",
        zmin=-1, zmax=1,
        title="Correlation Heatmap of Daily Returns"
    )
    st.download_button(
        label="Download Correlation Data as CSV",
        data=corr_matrix.to_csv().encode("utf-8"),
        file_name="correlation_heatmap.csv",
        mime="text/csv",
    )
    return fig

def plot_individual_data(df, ticker, show_ma=False, show_rsi=False, show_boll=False):
    df = force_1d(df)
    if df.empty:
        return None

    if "Close" not in df.columns:
        st.warning(f"No 'Close' column found for {ticker}. Columns: {list(df.columns)}")
        return None

    close_vals = df["Close"].values
    start_close = float(close_vals[0])
    end_close = float(close_vals[-1])
    if math.isnan(start_close) or math.isnan(end_close):
        st.warning(f"Cannot compute total return for {ticker} due to missing start/end price.")
    else:
        total_return_pct = ((end_close - start_close) / start_close) * 100
        st.metric(label=f"{ticker} Total Return (%)", value=f"{total_return_pct:.2f}%")

    with st.expander("Data Summary"):
        st.table(df.describe(include="all"))

    fig = px.line(df, x="Date", y="Close", title=f"{ticker} Prices", labels={"x": "Date", "y": "Price"})

    if show_ma and "50-Day MA" in df.columns:
        fig.add_scatter(x=df["Date"], y=df["50-Day MA"], mode="lines", name="50-Day MA")

    if show_boll and all(x in df.columns for x in ["BB_Upper", "BB_Lower", "BB_Mid"]):
        fig.add_scatter(x=df["Date"], y=df["BB_Upper"], mode="lines", line=dict(dash="dash", color="gray"), name="BB Upper")
        fig.add_scatter(x=df["Date"], y=df["BB_Mid"], mode="lines", line=dict(dash="dot", color="gray"), name="BB Mid")
        fig.add_scatter(x=df["Date"], y=df["BB_Lower"], mode="lines", line=dict(dash="dash", color="gray"), name="BB Lower")

    if show_rsi and "RSI" in df.columns:
        fig.add_scatter(
            x=df["Date"],
            y=df["RSI"],
            mode="lines",
            name="RSI",
            yaxis="y2"
        )
        fig.update_layout(
            yaxis2=dict(
                title="RSI",
                overlaying="y",
                side="right",
                range=[0, 100]
            )
        )

    return fig

# ------------------ 5. MAIN LOGIC ------------------ #
if selected_tab == "Home":
    st.title("Financial Dashboard")
    st.markdown(
        """
        Welcome to the Financial Dashboard! This is a demonstration project showcasing financial data analysis capabilities.

        ### Features:
        - Analyze data for Stocks, Forex, Cryptocurrencies, Commodities, Markets, and ETFs/Mutual Funds.
        - Combined and individual visualizations for easy comparison and detailed insights.
        - Interactive and user-friendly interface.
        - Compare tickers against the S&P 500.
        - Optional technical indicators (50-day MA, RSI, Bollinger Bands).
        - Correlation heatmap for multiple tickers.
        - Download combined data and correlation heatmap as CSV.

         ### Usage:
        - Use the sidebar to navigate between different financial data categories.
        - Adjust the date range and time increments.
        - Check the boxes for 50-day MA, S&P 500 comparison, RSI, or Bollinger Bands if desired.
        - The 'Correlation Heatmap' tab appears if multiple tickers are selected.
        - In the 'Combined' tab, you can download the data as a CSV.
        """
    )

else:
    st.title(f"{selected_tab}")

    default_list = tickers_map[selected_tab]
    user_input = st.sidebar.text_input(
        f"Enter {selected_tab} symbols (comma-separated):",
        ",".join(default_list)
    )
    user_tickers = [t.strip() for t in user_input.split(",") if t.strip()]

    if compare_with_sp500 and "^GSPC" not in user_tickers:
        user_tickers.append("^GSPC")

    data = fetch_data(user_tickers, start_date, end_date, time_increment_for_yahoo)

    for tkr, df_tkr in data.items():
        if not df_tkr.empty:
            if show_moving_average:
                df_tkr = add_moving_average(df_tkr)
            if show_rsi:
                df_tkr = add_rsi(df_tkr)
            if show_bollinger:
                df_tkr = add_bollinger_bands(df_tkr)
            data[tkr] = force_1d(df_tkr)

    if data and any(not df_.empty for df_ in data.values()):
        tab_names = ["Combined"]
        if len(data) > 1:
            tab_names.append("Correlation Heatmap")
        tab_names.extend(user_tickers)

        st_tabs = st.tabs(tab_names)

        with st_tabs[0]:
            fig = plot_combined_data(
                data,
                f"{selected_tab} Combined Prices",
                show_moving_average,
                show_rsi,
                show_bollinger
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        if len(data) > 1:
            with st_tabs[1]:
                corr_fig = plot_correlation_heatmap(data)
                if corr_fig:
                    st.plotly_chart(corr_fig, use_container_width=True)
                else:
                    st.warning("Not enough valid data to compute correlation.")

        for i, ticker in enumerate(user_tickers):
            with st_tabs[2 + i]:
                df_ticker = data.get(ticker)
                if df_ticker is not None and not df_ticker.empty:
                    fig_ind = plot_individual_data(
                        df_ticker,
                        ticker,
                        show_moving_average,
                        show_rsi,
                        show_bollinger
                    )
                    if fig_ind:
                        st.plotly_chart(fig_ind, use_container_width=True)
                else:
                    st.warning(f"No data available for {ticker}.")
    else:
        st.warning("No data retrieved for the selected tickers.")
