import Data
import View
import os

data_file = Data.StockData.get_last_trading_day().strftime('%Y-%m-%d') + ".json"
print(data_file)

if not os.path.exists(data_file):
    Data.SP500Data()

canvas = View.Canvas(data_file=data_file)
canvas.run()

