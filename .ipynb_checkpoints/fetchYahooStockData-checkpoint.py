from bs4 import BeautifulSoup
import pandas as pd
import requests
import numpy as np

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
def metadata_price_action(ticker, interval, timeRange):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?symbol={ticker}&region=US&lang=en-US&includePrePost=false&interval={interval}&useYfid=true&range={timeRange}&corsDomain=finance.yahoo.com&.tsrc=finance"
    print(url)
    stockData = requests.get(url)
    print(stockData.text)
    stockJson = stockData.json()
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