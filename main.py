import sys
import pandas as pd
import re
# import numpy as np


def convert_str_to_float_df_columns(df: pd.DataFrame, numeric_columns: list):
    for column in numeric_columns:
        if str(df[column].dtype) not in ("int", "int64"):
            df[column] = df[column].map(lambda value: float(re.sub("[^0-9.]", "", value)))


def create_portfolio_from_transactions(transactions_df: pd.DataFrame):
    portfolio_df = transactions_df.drop(["Date", "Cusip", "Order Id", "Other Fees", "Net Amt"], axis="columns")
    symbol_group = portfolio_df.groupby(["Symbol"])
    temp_df = symbol_group[["Qty", "Principal", "Comm"]].sum()    # TODO - Subtract sell transactions
    temp_df["Tranches"] = portfolio_df["Symbol"].value_counts()
    return temp_df


if __name__ == "__main__":
    if len(sys.argv) > 1:
        transactions_xlsx = sys.argv[1]
    else:
        transactions_xlsx = r"C:\Users\tnisa\Google Drive\Investing\dgi-transactions.xlsx"

    # Import the Sample worksheet with acquisition dates and initial cost basis:
    transactions = pd.read_excel(transactions_xlsx, sheet_name='Sheet1')
    convert_str_to_float_df_columns(transactions, ["Qty", "Price", "Principal", "Comm", "Other Fees", "Net Amt"])

    portfolio = create_portfolio_from_transactions(transactions)
    print(portfolio)
    # portfolio_positions = set(transactions["Symbol"])
    # print(f"Portfolio Positions: {portfolio_positions}")
    print(f"\nSummary:\n{portfolio.sum()}")
