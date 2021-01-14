# runner.py
import yfinance as yf
import plotly.graph_objects as go
import plotly.figure_factory as ff
import math
from datetime import datetime

# Define the ticker and time range
ticker = 'KO'
time_range = 6
ticker = ticker.upper()

# Get Yahoo Finance data
yahoo_data = yf.Ticker(ticker)

# Create a dataframe of Yahoo Finance data
# actions=True includes dividend data
stock_price_history_df = yahoo_data.history(
    actions=True,
    period=f"{time_range}y"
)

# Calculates years of returned data
years = round((
                      stock_price_history_df.index[-1] -
                      stock_price_history_df.index[-0]
              ).days / 365.25)

# Define price data
# Gets high price on first day of Yahoo data
start_price = stock_price_history_df['High'].iloc[0]

# Gets current Yahoo price
current_price = yahoo_data.info['regularMarketPrice']

# Gets max of all daily highs
max_price = max(stock_price_history_df['High'])

# Calculates compound Annual Growth Rate (CAGR)
stock_cagr = ((current_price / start_price) ** (1 / years)) - 1

# Filters stock history data on dividend payment dates
dividend_df = stock_price_history_df[(stock_price_history_df['Dividends'] > 0)]

# Extracts dividend data
try:
    start_dividend = dividend_df['Dividends'].iloc[0]
    end_dividend = dividend_df['Dividends'].iloc[-1]
    dividend_cagr = ((end_dividend / start_dividend) ** (1 / years)) - 1
    dividend_payments = [x for x in dividend_df.itertuples(index=True, name='Pandas')]
    dividend_frequency = round(len(dividend_payments) / years)
# Exception for stocks with dividend history like AMZN
except IndexError as error:
    start_dividend = 0
    end_dividend = 0
    dividend_cagr = 0
    dividend_payments = []
    dividend_frequency = 0

# Extracts table information
# Accounts for cases when yfinance doesn't include some info
try:
    payout_ratio = '<b>{0:.2%}</b>'.format(yahoo_data.info['payoutRatio'])
except:
    payout_ratio = '<b>Not in<br>yfinance</b>'

try:
    dividend_yield = '<b>{0:.2%}</b>'.format(yahoo_data.info['dividendYield'])
except:
    dividend_yield = '<b>Not in<br>yfinance</b>'

try:
    forward_pe = f"<b>{round(yahoo_data.info['forwardPE'], 2)}</b>"
except:
    forward_pe = '<b>Not in<br>yfinance</b>'

table_data = [
    [
        'Ticker',
        'Time<br>Range<br>(years)',
        'Current<br>Share<br>Price',
        f'{years}-Year<br>Dividend<br>CAGR',
        'Current<br>Yield',
        'Payout<br>Ratio<br>(Forward)',
        'PE<br>Ratio',
        f'{years}-Year<br>Stock<br>CAGR',
        'Consecutive<br>Dividend<br>Increases<br>(years)',
        'Dividends/<br>Year<br>(frequency)'
    ], [
        f'<b>{ticker}</b>',
        f'<b>{years}</b>',
        '<b>${:,.2f}</b>'.format(current_price),
        '<b>{0:.2%}</b>'.format(dividend_cagr),
        dividend_yield,
        payout_ratio,
        forward_pe,
        '<b>{0:.2%}</b>'.format(stock_cagr),
        '<b>TBD</b>',
        f'<b>{dividend_frequency}</b>'
    ]
]

# Set dashboard color palette variables
color_dividends = '#3d85c6'
color_yields = '#f4b400'
color_white = '#FFFFFF'
color_gray_shade_1 = '#D3D3D3'
color_gray_shade_2 = '#a8a8a8'
color_background = '#434343'
color_line_area = '#42576b'
color_black = 'black'
color_table_header = '#b7b7b7'
color_table_cells = "#6ea8dc"

# Builds colorscale (used by table)
colorscale = [
    [0, color_table_header],
    [.5, color_white],
    [1, color_table_cells]
]

# Build the table
fig = ff.create_table(
    table_data,
    colorscale=colorscale,
    font_colors=[color_black],
)

#### Generate x/y charting data
# Initialize the four y-axis data columns
dates = []
amounts = []
percent_increases = []
yields = []

# Add data to the y-axis data columns for each dividend payment
for row in dividend_payments:
    # Removes errant yfinance duplication (two dividends in under ten days)
    if dates and (row[0] - datetime.strptime(dates[-1], "%Y-%m-%d")).days < 10:
        dates.pop()

    # Adds date
    dates.append(str(row[0].to_pydatetime())[0:10])

    # Adds amount
    amounts.append(row[6])

    # Adds historic yield
    share_price = row[2]
    yields.append(row[6] * dividend_frequency / share_price)

    # Adds percent increase if there was an increase
    if len(amounts) > 1 and amounts[-2] != row[6]:
        increase = (row[6] - amounts[-2]) / amounts[-2]
        percent_increases.append('{0:.2%}'.format(increase))
    else:
        percent_increases.append(None)

# Set y gridlines
# https://github.com/VictorBezak/Plotly_Multi-Axes_Gridlines
gridlines = 4


# Function which takes in y-axis values and number of gridlines
# Outputs information used to optimize gridlines for multiple y-axes
def normalize_axis(y_values, gridlines):
    if y_values:
        y_max = max(y_values)
    else:  # Exception for when there are no dividend payments
        y_max = 5
    y_range = y_max * 1000  # because min is always 0 and to account for ranges < 1
    y_len = len(str(math.floor(y_range)))  # Gets number of digits
    y_pow10_divisor = math.pow(10, y_len - 1)
    y_firstdigit = math.floor(y_range / y_pow10_divisor)
    y_max_base = y_pow10_divisor * y_firstdigit / 1000
    y_dtick = y_max_base / gridlines
    y_dtick_ratio = y_range / y_dtick

    return {
        'max': y_max,
        'range': y_range,
        'dtick': y_dtick,
        'dtick_ratio': y_dtick_ratio
    }


# Create variables for amounts and yields
y1 = normalize_axis(amounts, gridlines)
y2 = normalize_axis(yields, gridlines)

# Optimizes matching y-axis ticks for amounts and yields
global_dtick_ratio = max(y1['dtick_ratio'], y2['dtick_ratio'])
y1_positive_ratio = abs(y1['max'] / y1['range']) * global_dtick_ratio
y2_positive_ratio = abs(y2['max'] / y2['range']) * global_dtick_ratio
global_positive_ratio = max(y1_positive_ratio, y2_positive_ratio) + 0.1

# Outputs y-axes ranges for use when building the chart
y1_range_max = (global_positive_ratio) * y1['dtick']
y2_range_max = (global_positive_ratio) * y2['dtick']

########################
# Make traces for graph
trace1 = go.Bar(
    x=dates,
    y=amounts,
    xaxis='x2',
    yaxis='y2',
    text=amounts,
    textposition='inside',
    texttemplate='$%{y:.2f}',
    marker=dict(color=color_dividends),
    name='Dividend Amount ($)',
    hoverinfo='x+y'
)
trace2 = go.Scatter(
    x=dates,
    y=yields,
    xaxis='x2',
    yaxis='y3',
    name='Historic Yield (%)',
    line=dict(color=color_yields, width=3),
    hoverinfo='x+y'
)
trace3 = go.Scatter(
    x=dates,
    y=percent_increases,
    xaxis='x2',
    yaxis='y4',
    marker=dict(color=color_white),
    mode='markers+text',
    text=percent_increases,
    textposition='top center',
    textfont=dict(color=color_white),
    name='Percent Increase (%)',
    hoverinfo='x+text'
)
trace4 = go.Scatter(
    x=stock_price_history_df.index,
    y=stock_price_history_df['High'],
    xaxis='x2',
    yaxis='y5',
    name='Share Price ($)',
    fill='tozeroy',
    fillcolor=color_line_area,
    line=dict(color=color_dividends, width=3),
    hoverinfo='x+y'
)

# Add trace data to figure
fig.add_traces([trace1, trace2, trace3, trace4])

# initialize xaxis2 and yaxis2
fig['layout']['xaxis2'] = {}
fig['layout']['yaxis2'] = {}
fig['layout']['yaxis3'] = {}
fig['layout']['yaxis4'] = {}
fig['layout']['yaxis5'] = {}

# Edit screen layout for subplots
fig.layout.yaxis.update({
    'domain': [.7, .95]
})
fig.layout.xaxis2.update({
    'tickfont': dict(color=color_gray_shade_2),
    'hoverformat': '%B %d, %Y',
    'anchor': 'y2',
})
fig.layout.yaxis2.update({
    'domain': [.1, .45],
    'title': 'Dividend Amount',
    'range': [0, y1_range_max],
    'dtick': y1['dtick'],
    'gridcolor': color_gray_shade_2,
    'title_font': dict(color=color_gray_shade_1),
    'tickfont': dict(color=color_gray_shade_2),
    'anchor': 'x2',
    'tickprefix': '$',
    'tickformat': ',.2f',
})
fig.layout.yaxis3.update({
    'domain': [.1, .45],
    'title': 'Historic Yield and Dividend Increase (%)',
    'side': 'right',
    'overlaying': 'y2',
    'anchor': 'x2',
    'range': [0, y2_range_max * 2],
    'dtick': y2['dtick'] * 2,
    'showgrid': False,
    'title_font': dict(color=color_gray_shade_1),
    'tickfont': dict(color=color_gray_shade_2),
    'hoverformat': ',.2%',
    'tickformat': ',.1%',
    'zeroline': True,
    'zerolinewidth': 2,
    'zerolinecolor': color_gray_shade_2,
})
fig.layout.yaxis4.update({
    'domain': [.1, .45],
    'overlaying': 'y2',
    'anchor': 'x2',
    'rangemode': 'tozero',
    'showgrid': False,
    'showticklabels': False,
    'tickformat': ',.1%',
    'zeroline': False
})
fig.layout.yaxis5.update({
    'domain': [.5, .65],
    'anchor': 'x2',
    'tickfont': dict(color=color_gray_shade_2),
    'showgrid': False,
    'title': 'Share Price ($)',
    'title_font': dict(color=color_gray_shade_1),
    'range': [0, max_price],
    'tickprefix': '$',
    'tickformat': ',.0f',
    'hoverformat': ',.2f',
    'zeroline': True,
    'zerolinewidth': 2,
    'zerolinecolor': color_gray_shade_2,
})

# Update the margins to add a title and see graph x-labels.
fig.layout.margin.update({'t': 75, 'l': 50})

title = (
        f"{years}-Year Dividend Summary for {ticker}: {yahoo_data.info['longName']}" +
        f"<br><span style='font-size: 12px;'>As of {datetime.now().strftime('%B %d, %Y')}</span>" +
        "<br><span style='font-size: 12px;'>Information accuracy and completeness not guaranteed. Not all yfinance dividends are adjusted for splits</span>"
)

fig.layout.update({
    'title': title,
    'plot_bgcolor': color_background,
    'paper_bgcolor': color_background,
    'legend': dict(
        x=.14,
        y=0.69,
        traceorder="normal",
        font=dict(color=color_gray_shade_1),
    ),
    'legend_orientation': 'h',
    'font': dict(color=color_white),
    'height': 800,
    'hovermode': 'x'
})

fig.show()
