import sys
import pandas as pd
import re
import yfinance as yf
# import numpy as np

yahoo_field_map = {
        "Sector": "sector",
        "Name": "shortName",
        "Price": "previousClose",   # regularMarketPreviousClose
        "Forward Dividend": "dividendRate",
        "Forward Yield": "dividendYield",
        "Forward PE": "forwardPE",
        "Market Cap": "marketCap",
    }


def convert_str_to_float_df_columns(df: pd.DataFrame, numeric_columns: list):
    for column in numeric_columns:
        if str(df[column].dtype) not in ("int", "int64"):
            df[column] = df[column].map(lambda value: float(re.sub("[^0-9.]", "", value)))


def fetch_positions_current_info(position_df: pd.DataFrame, field_map: dict):
    data = dict()

    for symbol in position_df["Symbol"].to_list():
        ticker = yf.Ticker(symbol)
        ticker_data = ticker.info
        for field in field_map.keys():
            if field not in data:
                data[field] = []
            data[field].append(ticker_data[field_map[field]])

    # data = yf.download(tickers=" ".join(position_df["Symbol"].to_list()), period="1d", group_by="ticker")
    data["Symbol"] = position_df["Symbol"].to_list()
    return pd.DataFrame.from_dict(data)


def calculate_positions_yoc():
    pass


def create_portfolio_from_transactions(transactions_df: pd.DataFrame):
    trans_cleaned = transactions_df.drop(["Date", "Cusip", "Order Id", "Other Fees", "Net Amt"], axis="columns")
    symbol_group = trans_cleaned.groupby(["Symbol"])
    portfolio_df = symbol_group[["Qty", "Principal", "Comm"]].sum()    # TODO - Subtract Sell transactions
    portfolio_df["Tranches"] = trans_cleaned["Symbol"].value_counts()
    portfolio_df.reset_index(inplace=True)
    position_info_df = fetch_positions_current_info(portfolio_df[["Symbol"]], yahoo_field_map)
    position_df = pd.merge(portfolio_df, position_info_df, on="Symbol", how='inner')
    position_df["Cache Flow"] = position_df["Qty"]*position_df["Forward Dividend"]
    position_df["Market Value"] = position_df["Qty"] * position_df["Price"]
    return position_df


if __name__ == "__main__":
    if len(sys.argv) > 1:
        transactions_xlsx = sys.argv[1]
    else:
        transactions_xlsx = r"C:\Users\tnisa\Google Drive\Investing\dgi-transactions.xlsx"

    if len(sys.argv) > 2:
        portfolio_xlsx = sys.argv[2]
    else:
        portfolio_xlsx = r"C:\Users\tnisa\Google Drive\Investing\dgi-portfolio.xlsx"

    # Import the Sample worksheet with acquisition dates and initial cost basis:
    transactions = pd.read_excel(transactions_xlsx, sheet_name='Sheet1')
    convert_str_to_float_df_columns(transactions, ["Qty", "Price", "Principal", "Comm", "Other Fees", "Net Amt"])

    portfolio = create_portfolio_from_transactions(transactions)
    portfolio.to_excel(portfolio_xlsx, sheet_name="portfolio")

    summary_df = portfolio[["Qty", "Principal", "Cache Flow", "Comm", "Market Value"]]
    print(f"\nSummary:\n{summary_df.sum(numeric_only=True)}")
