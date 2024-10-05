import json
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import pandas_market_calendars as mcal
import os

class SP500Data:
    def __init__(self):
        self.file_path = "spx.txt"
        self.stock_objects = {}
        self._import_stocks()

    def _import_stocks(self):
        try:
            with open(self.file_path, 'r') as file:
                tickers = [line.strip() for line in file]
                for ticker in tickers:
                    stock_data = StockData(ticker)
                    self.stock_objects[ticker] = stock_data
            self.save_data()

        except FileNotFoundError:
            print(f"Error: The file {self.file_path} was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def save_data(self):
        self.stock_objects = dict(
            sorted(self.stock_objects.items(), key=lambda item: item[1].market_cap, reverse=True))

        data = {ticker: stock.to_dict() for ticker, stock in self.stock_objects.items()}
        data_filename = StockData.get_last_trading_day().strftime('%Y-%m-%d') + ".json"
        directory = "DailyData"
        os.makedirs(directory, exist_ok=True)
        data_filepath = os.path.join(directory, data_filename)
        try:
            with open(data_filepath, 'w') as file:
                json.dump(data, file)
            print(f"Data saved to {data_filename}")
        except Exception as e:
            print(f"An error occurred while saving data: {e}")

    def extract_percents(self):
        percent_arrays = []
        for stock in self.stock_objects.values():
            if stock.percents is not None:
                percent_arrays.append(stock.percents)
        return percent_arrays

class StockData:
    def __init__(self, ticker):
        self.ticker = ticker
        self.percents = None
        self.minutes = None
        self.market_cap = None
        self.date = self.get_last_trading_day()
        self.last_close = self.get_last_trading_day(previous_day = True)
        self._load_data()

    def to_dict(self):
        return {
            'percents': self.percents,
            'minutes': self.minutes,
            'market_cap': self.market_cap
        }

    def _load_data(self):
        try:
            stock_object = yf.Ticker(self.ticker)
            daily_data = stock_object.history(start=self.date.strftime('%Y-%m-%d'), period="1d", interval='1m')
            previous_close = stock_object.history(start=self.last_close.strftime('%Y-%m-%d'), period="1d")['Close'].iloc[0]
            self.market_cap = stock_object.info['marketCap']
            self.percents = [(price - previous_close) / previous_close for price in daily_data['Close']]
            self.minutes = [timestamp.strftime('%H:%M') for timestamp in daily_data.index]

            if len(self.minutes) != 390:
                self.interpolate_missing_data()

            print(self.ticker, len(self.minutes))

        except Exception as e:
            print(f"An error occurred while loading data for {self.ticker}: {e}")

    def interpolate_missing_data(self):
        full_minutes = []
        start_time = datetime.strptime("09:30", "%H:%M")
        end_time = datetime.strptime("15:59", "%H:%M")
        current_time = start_time

        while current_time <= end_time:
            full_minutes.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=1)

        original_data = dict(zip(self.minutes, self.percents))
        interpolated_percents = []

        for minute in full_minutes:
            if minute in original_data:
                interpolated_percents.append(original_data[minute])
            else:
                earlier_minute = max([m for m in self.minutes if m < minute], default=None)
                later_minute = min([m for m in self.minutes if m > minute], default=None)

                if earlier_minute and later_minute:
                    time_diff = (datetime.strptime(later_minute, "%H:%M") - datetime.strptime(earlier_minute,
                                                                                                 "%H:%M")).total_seconds()
                    weight = (datetime.strptime(minute, "%H:%M") - datetime.strptime(earlier_minute,
                                                                                        "%H:%M")).total_seconds() / time_diff

                    interpolated_value = (1 - weight) * original_data[earlier_minute] + weight * original_data[
                        later_minute]
                    interpolated_percents.append(interpolated_value)
                elif earlier_minute:
                    interpolated_percents.append(original_data[earlier_minute])
                elif later_minute:
                    interpolated_percents.append(original_data[later_minute])
                else:
                    interpolated_percents.append(0)

        self.minutes = full_minutes
        self.percents = interpolated_percents

    @staticmethod
    def get_last_trading_day(previous_day=False):
        present = datetime.now(pytz.timezone('US/Eastern'))
        nyse = mcal.get_calendar('NYSE')
        schedule = nyse.schedule(start_date=present - timedelta(days=10), end_date=present)

        last_market_close = schedule['market_close'].iloc[-1]
        is_after_close = present.date() > last_market_close.date() or (
                present.date() == last_market_close.date() and present.hour >= 16)

        if previous_day is False:
            return schedule['market_close'].iloc[-1].date() if is_after_close else schedule['market_close'].iloc[
                -2].date()
        else:
            return schedule['market_close'].iloc[-2].date() if is_after_close else schedule['market_close'].iloc[
                -3].date()
