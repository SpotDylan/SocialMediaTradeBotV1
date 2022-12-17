#This class will use the data scrapped from the websites that was exported into a csv
#in order to sort tickers and sent good trades to trade.py
import csv
import scrape
from stream import getDailyPercentageChange

#Declaring empty lists that we will use
RedditTwitterTrades = []
FinalList = []
StocktwitsList = []

class GetTickersToTrade:
    #Will read our csv files that have scraped data from various websites or APIs
    @staticmethod
    def searchSites():
        with open('StockTwits.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                x = 0
                StocktwitsList.insert(x, row["TICKER"])
                x += 1

        ApeWisdomList = list(())
        with open('Reddit.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                x = 0
                ApeWisdomList.insert(x, row["TICKER"])
                x += 1

        TradestieList = list(())
        with open('Twitter.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                x = 0
                TradestieList.insert(x, row["TICKER"])
                x += 1

        #Making a new list called CombinedTrades that will only take tickers that are both seen on Twitter and Reddit
        for element in ApeWisdomList:
            if element in TradestieList:
                RedditTwitterTrades.append(element)

        #Take out any values with "-" in them to take out any crypto tickers that aren't apart of our trading strategies
        for x in StocktwitsList:
            i = '-'
            if i in x:
                StocktwitsList.pop(StocktwitsList.index(x))
            i = '.'
            if i in x:
                StocktwitsList.pop(StocktwitsList.index(x))

        #Take out stocks that don't have above or below 5% market moves
        for x in StocktwitsList:
            print(type(x))
            print(x)
            if ((getDailyPercentageChange(x)) < (5) and (getDailyPercentageChange(x)) > (-5)):
                StocktwitsList.pop(StocktwitsList.index(x))

        #Reverse List to properly order rank 1 through 10 and remove any duplicate values
        StockTwitsReverse = StocktwitsList[::-1]
        FinalList = StockTwitsReverse + RedditTwitterTrades
        res = []
        [res.append(x) for x in FinalList if x not in res]
        file = open("StocksToTrade.csv", "w")
        writer = csv.writer(file)
        for x in range(len(res)):
            writer.writerow([res[x]])

