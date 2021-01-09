import sys
import pandas as pd
import re
import yfinance as yf
import datetime
# import numpy as np


class TSF:
    """
    Trade Station transaction fields
    """
    symbol = "Symbol"
    principal = "Principal"
    quantity = "Qty"
    commission = "Comm"
    purchase_price = "Price"
    dropped = ["Date", "Cusip", "Order Id", "Other Fees", "Net Amt", purchase_price]
    summation = [quantity, principal, commission]


class PF(TSF):
    """
    Portfolio fields
    """
    tranches = "Tranches"
    current_price = "Closing Price"
    position_cache_flow = "Position Cache Flow"
    position_cache_flow_percent = "Position Cache Flow %"
    position_market_value = "Position Market Value"
    position_market_value_percent = "Position Market Value %"
    position_yoc = "Position YOC"
    forward_div_rate = "Forward Div Rate"
    summary = [TSF.quantity, TSF.principal, position_cache_flow, TSF.commission, position_market_value]


yahoo_field_map = {
        "Sector": "sector",
        "Name": "shortName",
        PF.current_price: "previousClose",   # regularMarketPreviousClose
        PF.forward_div_rate: "dividendRate",
        "Forward Div Yield": "dividendYield",
        "Forward PE": "forwardPE",
        "Forward EPS": "forwardEps",
        "Price To Book": "priceToBook",
        "Payout Ratio": "payoutRatio",
        "Ex-Div Date": "exDividendDate",
        "Market Cap": "marketCap",
    }


def convert_str_to_float_df_columns(df: pd.DataFrame, numeric_columns: list):
    for column in numeric_columns:
        if str(df[column].dtype) not in ("int", "int64"):
            df[column] = df[column].map(lambda value: float(re.sub("[^0-9.]", "", value)))


def fetch_positions_current_info(position_df: list, field_map: dict):
    data = dict()
    for symbol in position_df:
        ticker = yf.Ticker(symbol)
        ticker_data = ticker.info
        for field in field_map.keys():
            if field not in data:
                data[field] = []
            if "date" in field.lower():
                # Convert epoch time stamp to date-time format
                ticker_data[field_map[field]] = datetime.datetime.fromtimestamp(ticker_data[field_map[field]])
            data[field].append(ticker_data[field_map[field]])

    data["Symbol"] = position_df
    return pd.DataFrame.from_dict(data)


def calculate_positions_yoc():
    pass


def create_portfolio_from_transactions(transactions_df: pd.DataFrame):
    trans_cleaned = transactions_df.drop(PF.dropped, axis="columns")
    symbol_group = trans_cleaned.groupby([PF.symbol])
    portfolio_df = symbol_group[PF.summation].sum()    # TODO - Subtract Sell transactions
    portfolio_df[PF.tranches] = trans_cleaned[PF.symbol].value_counts()
    portfolio_df.reset_index(inplace=True)
    position_info_df = fetch_positions_current_info(portfolio_df[PF.symbol].to_list(), yahoo_field_map)
    position_df = pd.merge(portfolio_df, position_info_df, on=PF.symbol, how='inner')
    # Cache Flow
    position_cache_flow = position_df[PF.quantity]*position_df[PF.forward_div_rate]
    position_df[PF.position_cache_flow] = position_cache_flow
    position_df[PF.position_cache_flow_percent] = position_cache_flow / position_cache_flow.sum()
    # YOC
    position_df[PF.position_yoc] = position_cache_flow / position_df[PF.principal]
    # Market Value
    position_market_value = position_df[PF.quantity] * position_df[PF.current_price]
    position_df[PF.position_market_value] = position_market_value
    position_df[PF.position_market_value_percent] = position_market_value / position_market_value.sum()
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
    convert_str_to_float_df_columns(transactions, TSF.summation)

    portfolio = create_portfolio_from_transactions(transactions)
    portfolio.to_excel(portfolio_xlsx, sheet_name="portfolio")

    summary_df = portfolio[PF.summary]
    print(f"\nSummary:\n{summary_df.sum(numeric_only=True)}")
