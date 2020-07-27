import pandas as pd
import yfinance as yf
from datetime import datetime
from time_series_transform.stock_transform.base import *

class Stock_Extractor(object):
    def __init__(self,symbol,engine):
        self.client = self._get_extractor(engine)(symbol)
        self.symbol = symbol
        self.stock = None

    def _get_extractor(self,engine):
        engineDict = {
            'yahoo':yahoo_stock
        }
        return engineDict[engine]

    def get_stock_period(self,period):
        data = self.client.getHistoricalByPeriod(period)
        data = pd.DataFrame(data.to_records())
        data['Date'] = data.Date.astype(str)
        additionalInfo = self.client.getAdditionalInfo()
        self.stock = Stock(self.symbol,data,additionalInfo,'Date')
        return self.stock

    def get_stock_date(self,start_date,end_date):
        data = self.client.getHistoricalByRange(start_date,end_date)
        data = pd.DataFrame(data.to_records())
        data['Date'] = data.Date.astype(str)
        additionalInfo = self.client.getAdditionalInfo()
        self.stock = Stock(self.symbol,data,additionalInfo,'Date')
        return self.stock

    # I/O
    @classmethod
    def get_stock_from_csv(cls, symbol, path, *args, **kwargs):
        data = pd.read_csv(path)
        stock_data = Stock(symbol, data, *args, **kwargs)
        return stock_data


    @classmethod
    def get_stock_from_parquet(cls, symbol, path, *args, **kwargs):
        data = pd.read_parquet(path, engin = 'pyarrow')
        stock_data = Stock(symbol, data, *args, **kwargs)
        return stock_data

class Portfolio_Extractor(object):
    def __init__(self,symbolList,engine):
        self.engine = engine
        self.symbolList = symbolList
        self.portfolio = None

    def get_portfolio_period(self,period):
        stockList = []
        for symbol in self.symbolList:
            stock_data = Stock_Extractor(symbol, self.engine).get_stock_period(period)
            stockList.append(stock_data)

        self.portfolio = Portfolio(stockList)
        return self.portfolio

    def get_portfolio_date(self,start_date, end_date):
        stockList = []
        for symbol in self.symbolList:
            stock_data = Stock_Extractor(symbol, self.engine).get_stock_date(start_date, end_date)
            stockList.append(stock_data)

        self.portfolio = Portfolio(stockList)
        return self.portfolio




class yahoo_stock(object):

    """
    Fetching stock data from yahoo finance
    
    API Document: 
    - https://github.com/ranaroussi/yfinance
    - https://pypi.org/project/fix-yahoo-finance/0.1.0/
    ---
    Require:
    - yfinance

    """
    def __init__(self,symbol):
        """
        Historical Data
        ---
        Input:
        symbol: string
        period: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        (default is '1mo')
        start_date, end_date: String, "%Y-%m-%d", eg "2020-02-20"
        ---
        Return:
        date, open, high, low, close, volume, dividends, stock splits
        """
        self._symbol = symbol
        self._ticker = self._getStock(symbol)
    

    # getter and setter
    @property
    def ticker(self):
        return self._ticker

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, symbol):
        self._symbol = symbol
        self._ticker = yf.Ticker(symbol)
    
    def _getStock(self, symbol):
        ticker = yf.Ticker(symbol)
        return ticker

    def getCompanyInfo(self):
        try:
            return self.ticker.info
        except:
            return None


    def getHistoricalByPeriod(self, period = '1mo'):
        return self.ticker.history(period)

    def getHistoricalByRange(self, start_date, end_date):
        return self.ticker.history(start = start_date, end = end_date)

    def getActions(self):
        try:
            return self.ticker.actions
        except:
            return None

    def getDividends(self):
        try:
            return self.ticker.dividends
        except:
            return None

    def getSplits(self):
        try:
            return self.ticker.splits
        except:
            return None

    def getSustainability(self):
        try:
            return self.ticker.sustainability
        except:
            return None

    def getRecommendations(self):
        try:
            return self.ticker.recommendations
        except:
            return None

    def getNextEvent(self):
        try:
            return self.ticker.calendar
        except:
            return None

    def getAdditionalInfo(self):
        info_dict = {
            'company_info':self.getCompanyInfo(),
            'sustainability': self.getSustainability()
        }

        schedule_dict = {
            'actions': self.getActions(),
            'recommendations': self.getRecommendations(),
            'next_event': self.getNextEvent()
        }
       
        data = {
            'info': info_dict,
            'schedule': schedule_dict
            
        }
        return data