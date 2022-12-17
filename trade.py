#This is our main file that will send orders
#Importing data from other local Python files
import config
import sort
from sort import GetTickersToTrade
from stream import getAskPrice
from stream import getDailyPercentageChange

#Alpaca Related Packages
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
import alpaca_trade_api as tradeapi

#Miscellaneous Packages
import time
import datetime
import threading
import csv

BASE_URL = "https://paper-api.alpaca.markets"

#account variables
trading_client = TradingClient(config.APCA_API_KEY_ID, config.APCA_API_SECRET_KEY, paper=True)
account = trading_client.get_account()
positions = trading_client.get_all_positions()

def startPosLong(symbol, sharesAmount):
    trading_client.submit_order(
        symbol=symbol,
        qty=sharesAmount,
        side=OrderSide.BUY,
        type="market",
        time_in_force=TimeInForce.GTC
    )

def startPosShort(symbol, sharesAmount):
    trading_client.submit_order(
        symbol=symbol,
        qty=sharesAmount,
        side=OrderSide.SELL,
        type="market",
        time_in_force=TimeInForce.GTC
    )

class Trade:
    api = tradeapi.REST(config.APCA_API_KEY_ID, config.APCA_API_SECRET_KEY, BASE_URL, 'v2')
    def run(self):
        # We will first clean our account and get rid of all open orders
        trading_client.cancel_orders()
        # Setting up internal clock
        # Wait for market to open.
        print("Waiting for market to open...")
        tAMO = threading.Thread(target=self.awaitMarketOpen)
        tAMO.start()
        tAMO.join()
        print("Market opened.")
        # While True allows our program to continously loop, with time.sleep() intervals to give it breaks
        while True:
            # Configures a clock so the program knows when is market open and when is market close
            clock = self.api.get_clock()
            closingTime = clock.next_close.replace(tzinfo=datetime.timezone.utc).timestamp()
            currTime = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
            self.timeToClose = closingTime - currTime

            if (self.timeToClose < (60 * 15)):
                # Close all positions when 15 minutes til market close.
                print("Market closing soon.  Closing All Open Orders")
                trading_client.cancel_orders()
                # Run script again after market close for next trading day.
                print("Sleeping until market close (15 minutes).")
                time.sleep(60 * 15)
            else:
                #Search for an exit opportunity, either take profit or take
                for position in positions:
                    positionTicker = position.symbol
                    price = getAskPrice(positionTicker)
                    profit_loss = (float(price) - float(position.avg_entry_price)) / float(position.avg_entry_price)
                        # Check if the profit or loss is greater than 4%
                    if profit_loss >= 0.04:
                        # Submit an order to sell the stock at market price
                        trading_client.close_position(positionTicker)
                        print(f'Took profit on {position.qty} shares of {positionTicker} at {price}')
                        # Check if the profit or loss is less than -2%
                    elif profit_loss <= -0.02:
                        # Submit an order to sell the stock at market price
                        trading_client.close_position(positionTicker)
                        print(f'Stopped out on {position.qty} shares of {positionTicker} at {price}')
                # Search for new trade opportunity
                x = GetTickersToTrade()
                x.searchSites()
                with open('StocksToTrade.csv', 'r') as csvfile:
                    reader = csv.DictReader(csvfile)
                    FiveMinStocks =[]
                    for row in reader:
                        FiveMinStocks.append(row)
                for FiveMinStock in FiveMinStocks:
                    #Using getAskPrice method from the stream.py file
                    if float(account.buying_power) > 0:
                        fracShare = 2000.0/float(getAskPrice(FiveMinStock))
                        if getDailyPercentageChange(FiveMinStock) > 0:
                            startPosLong(self, FiveMinStock, fracShare)
                            print(f'Started long position of {fracShare} shares, qty of {FiveMinStock} at {getAskPrice(FiveMinStock)}')
                        elif getDailyPercentageChange(FiveMinStock) < 0:
                            startPosShort(self, FiveMinStock, fracShare)
                            print(f'Started short position of {fracShare} shares, qty of {FiveMinStock} at {getAskPrice(FiveMinStock)}')
                    else:
                        break
                time.sleep(60 * 5)

    #Function to see if the market is open
    def awaitMarketOpen(self):
        isOpen = self.api.get_clock().is_open
        while (not isOpen):
            clock = self.api.get_clock()
            openingTime = clock.next_open.replace(tzinfo=datetime.timezone.utc).timestamp()
            currTime = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
            timeToOpen = int((openingTime - currTime) / 60)
            print(str(timeToOpen) + " minutes til market open.")
            time.sleep(60)
            isOpen = self.api.get_clock().is_open

#Create an instantiation of our Trade Object, use .run() to actually run our program
ls = Trade()
ls.run()