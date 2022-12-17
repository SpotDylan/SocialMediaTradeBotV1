#This will connect our program to stream data with alpaca and calculate average move and average volume
import config
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.data.requests import StockSnapshotRequest

#keys required for stock historical data client
client = StockHistoricalDataClient(config.APCA_API_KEY_ID, config.APCA_API_SECRET_KEY)

#Gets Ask Price of Ticker (needs to be passed through as parameter)
def getAskPrice(ticker):
    multisymbol_request_params = StockLatestQuoteRequest(symbol_or_symbols=[ticker])
    latest_multisymbol_quotes = client.get_stock_latest_quote(multisymbol_request_params)
    latest_ask_price = latest_multisymbol_quotes[ticker].ask_price
    return(latest_ask_price)

# #daily open price
@staticmethod
def getDailyPercentageChange(ticker):
    request_params = StockSnapshotRequest(symbol_or_symbols = [ticker])
    classObj = client.get_stock_snapshot(request_params)
    dailyBar = classObj[ticker].daily_bar
    return ((float(dailyBar.close) - float(dailyBar.open))/((float(dailyBar.open))*100))

