import yfinance as yf
import pandas_market_calendars as mcal
from datetime import datetime, timedelta
import pytz
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class SP500Data:
    def __init__(self, file_path="spx.txt"):
        self.file_path = file_path
        self.stock_objects = {}
        self._import_stocks()
    def _import_stocks(self):
        try:
            with open(self.file_path, 'r') as file:
                tickers = [line.strip() for line in file]
                for ticker in tickers:
                    print(ticker)
                    self.stock_objects[ticker] = StockData(ticker)
        except FileNotFoundError:
            print(f"Error: The file {self.file_path} was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

class StockData:
    def __init__(self, ticker):
        self.ticker = ticker
        self.percents = None
        self.minutes = None
        self.market_cap = None
        self._load_data()

    def _load_data(self):
        last_trading_day = self.get_last_trading_day()
        previous_trading_close = last_trading_day - timedelta(days=1)

        try:
            stock_object = yf.Ticker(self.ticker)
            daily_data = stock_object.history(start=last_trading_day.strftime('%Y-%m-%d'), period="1d", interval='1m')
            previous_close = stock_object.history(start=previous_trading_close.strftime('%Y-%m-%d'), period="1d")['Close'].iloc[0]

            self.market_cap = stock_object.info['marketCap']
            self.percents = [(price - previous_close) / previous_close for price in daily_data['Close']]
            self.minutes = [timestamp.strftime('%Y-%m-%d %H:%M:%S') for timestamp in daily_data.index]

        except Exception as e:
            print(f"An error occurred while loading data for {self.ticker}: {e}")

    @staticmethod
    def get_last_trading_day():
        present = datetime.now(pytz.timezone('US/Eastern'))
        nyse = mcal.get_calendar('NYSE')
        schedule = nyse.schedule(start_date=present - timedelta(days=10), end_date=present)

        if present.hour > 16:
            return schedule['market_close'].iloc[-1].date()
        else:
            return schedule['market_close'].iloc[-2].date()

stock = StockData('AAPL')

#data = SP500Data()


