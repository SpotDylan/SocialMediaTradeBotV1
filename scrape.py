#This file will scrape data from three websites
#Format each ticker:
# Rank,Ticker,Price,PriceChange
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import csv
import time
import requests
import re

class startScrape:
    def scrape(self):
        chrome_options = Options()
        driver = webdriver.Chrome(options=chrome_options)

        # StockTwits Scrape ======================================================
        #  Use Selenium to navigate to the website
        driver.get('https://stocktwits.com/rankings/trending')
        # Use Selenium to find the 'div' tags that contain the stock symbols
        div_tags = driver.find_elements(By.XPATH,
                                        '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div/div[1]/div[3]/div/div[1]/div')
        string = div_tags[0].text
        StockTwitsRanking = string.split('\n')
        file = open("StockTwits.csv", "w")
        writer = csv.writer(file)
        writer.writerow(["RANK", "TICKER", "NAME", "PRICE", "PRICECHANGE", "PRICE%CHANGE"])
        y = 0
        for x in range(1, 10):
            writer.writerow(
                [StockTwitsRanking[(5 * x) + y], StockTwitsRanking[(5 * x) + 1 + y],
                 StockTwitsRanking[(5 * x) + 2 + y],
                 StockTwitsRanking[(5 * x) + 3 + y], StockTwitsRanking[(5 * x) + 4 + y],
                 StockTwitsRanking[(5 * x) + 5 + y]])
            y += 1
        # End of StockTwits Scrape

        # ApeWisdom Scrape ======================================================
        #Unlike the other two, this will use an API to get data rather than scraping directly

        response = requests.get("https://apewisdom.io/api/v1.0/filter/all-stocks/")
        df = pd.read_json(response.text)
        tickerData = df.results.apply(pd.Series)
        file = open("Reddit.csv", "w")
        writer = csv.writer(file)
        writer.writerow(["RANK", "TICKER"])
        for y in range(0, 10):
            writer.writerow([y+1, tickerData['ticker'][y]])
        # End of ApeWisdom Scrape

        # Tradestie Scrape ======================================================
        driver.get("https://tradestie.com/apps/twitter/most-active-stocks/")

        # Forcing Selenium to wait for elements to appear, so program runs more efficiently
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "th"))
            )
        except:
            driver.quit()
        # End of forced pause of Selenium

        TradestieCommentBar = driver.find_elements(By.TAG_NAME, "th")
        TradestieCommentBar[5].click()
        TradestieCommentBar[5].click()
        TradestieHypeRanking = driver.find_elements(By.TAG_NAME, "tr")
        file = open("Twitter.csv", "w")
        writer = csv.writer(file)
        writer.writerow(["RANK", "TICKER", "SENTIMENT", "SENTIMENT SCORE", "NUMBER OF COMMENTS"])
        for z in range(1, 11):
            temp = TradestieHypeRanking[z + 7].text
            tempList = temp.split()
            writer.writerow([z, tempList[0], tempList[1], tempList[2], tempList[3]])
        # End of Tradestie Scrape

ls = startScrape()
ls.scrape()


