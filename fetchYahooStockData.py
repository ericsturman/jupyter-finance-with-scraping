from bs4 import BeautifulSoup
import pandas as pd
import requests
import numpy as np
from urllib.request import Request, urlopen
import json

def basic_stats(ticker):
    statsData = requests.get(f"https://finance.yahoo.com/quote/{ticker}?p={ticker}&.tsrc=fin-srch")
    statsSoup = BeautifulSoup(statsData.content, 'html.parser')
    stats_elem = statsSoup.find('div',id="quote-summary")
    statsObj={}
    stats=[]
    if stats_elem != None:
        for t in stats_elem.find_all("tr"):
            if(len(stats)==2):
                head, *tail=np.array(stats)
                statsObj[head]=tail[0]
            elif(len(stats)>=2):
                head, *tail=np.array(stats)
                statsObj[head]=tail
            stats=[]
            for td in t.find_all("td"):
                stats.append(td.text)
    return statsObj
#https://query1.finance.yahoo.com/v8/finance/chart/TTWO?symbol=TTWO&period1=1553835600&period2=1584507600&useYfid=true&interval=1d&includePrePost=true&events=div%7Csplit%7Cearn&lang=en-US&region=US&crumb=y%2FiyJMFZV99&corsDomain=finance.yahoo.com
#https://query1.finance.yahoo.com/v8/finance/chart/MMM?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance
def metadata_price_action(ticker, interval, timeRange):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?symbol={ticker}&region=US&lang=en-US&includePrePost=false&interval={interval}&useYfid=true&range={timeRange}&corsDomain=finance.yahoo.com&.tsrc=finance"
#     headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'}
    stockJson = getJsonData(url)
    stockResult = stockJson["chart"]["result"][0]
    stockMetadata = stockResult["meta"]
    stockPriceData = pd.DataFrame({"timestamp": stockResult["timestamp"]})
    stockIndicators = pd.DataFrame(stockResult["indicators"]["quote"][0])
    stockDataMerge = pd.concat([stockPriceData, stockIndicators], axis=1)
    return {"metadata": stockMetadata, "price":stockDataMerge}


def extended_stock_stats(ticker):
    stockData = requests.get(f"https://finance.yahoo.com/quote/{ticker}/key-statistics?p={ticker}")
    soup = BeautifulSoup(stockData.content, 'html.parser')
    job_elems = soup.find_all('section',  {"data-test":"qsp-statistics"})
    datObj={}
    dat=[]
    for job_elem in job_elems:
        for t in job_elem.find_all("tr"):
            if(len(dat)==2):
                head, *tail=np.array(dat)
                datObj[head]=tail[0]
            elif(len(dat)>=2):
                head, *tail=np.array(dat)
                datObj[head]=tail
            dat=[]
            for td in t.find_all("td"):
                dat.append(td.text)
    return datObj


def financials_balance_sheet(ticker):
    stockData = requests.get(f"https://finance.yahoo.com/quote/{ticker}/balance-sheet?p={ticker}")
    soup = BeautifulSoup(stockData.content, 'html.parser')
    job_elems = soup.find_all('section',  {"data-test":"qsp-financial"})
    datObj={}
    dat=[]
    for job_elem in job_elems:
        for t in job_elem.find_all("div"):
            if(len(dat)==2):
                head, *tail=np.array(dat)
                datObj[head]=tail[0]
            elif(len(dat)>=2):
                head, *tail=np.array(dat)
                datObj[head]=tail
            dat=[]
            for td in t.find_all("td"):
                dat.append(td.text)
    return datObj


def current_sp500_symbols():
    sp500 = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    soup = BeautifulSoup(sp500.content, 'html.parser')
    symbols=[]
    symbol_table = soup.find_all('table', id="constituents")
    for sym in symbol_table:
        for tr in sym.find_all("tr"):
            td = tr.find("td")
            if(td != None):
                symbols.append(td.text.strip())
    return symbols

def current_dow30_symbols():
    sp500 = requests.get("https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average")
    soup = BeautifulSoup(sp500.content, 'html.parser')
    symbols=[]
    symbol_table = soup.find_all('table', id="constituents")
    for sym in symbol_table:
        for tr in sym.find_all("tr"):
            td = tr.find_all("td")
            if(td != None and len(td) > 0):
                symbols.append(td[1].text.strip())
    return symbols

def current_nasdaq100_symbols():
    sp500 = requests.get("https://en.wikipedia.org/wiki/Nasdaq-100")
    soup = BeautifulSoup(sp500.content, 'html.parser')
    symbols=[]
    symbol_table = soup.find_all('table', id="constituents")
    for sym in symbol_table:
        for tr in sym.find_all("tr"):
            td = tr.find_all("td")
            if(td != None and len(td) > 0):
                symbols.append(td[1].text.strip())
    return symbols


def parse_value(val):
    lastChar = val[-1]
    number = val[0:-1]
    number = number.replace(",","")
    if(lastChar == "A"):
        return None
    elif (lastChar == "M"):
        return float(number) * 1000000
    elif (lastChar == "B"):
        return float(number) * 1000000000
    elif (lastChar == "T"):
        return float(number) * 1000000000000
    elif (lastChar == "%"):
        return float(number) / 100
    else:
        return float(number)
    
def getJsonData(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'}):
    stockData = requests.get(url, headers=headers)
    stockJson = stockData.json()
    print("first attempt status code:  ", stockData.status_code)
    if(stockData.status_code != 200):
        req = Request(url, headers)
        stockData = urlopen(req).read()
        stockJson = json.loads(stockData)
        print("second attempt status code:  ", stockData.status_code)
    return stockJson



    