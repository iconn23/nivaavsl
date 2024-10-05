# Wash St vs SJS 54 - 52. insane game
import Data
import View
import os

#data_file = "2024-09-20.json"
data_file = Data.StockData.get_last_trading_day().strftime('%Y-%m-%d') + ".json"
directory = 'DailyData'
data_filepath = os.path.join(directory, data_file)
print(data_file)

if not os.path.exists(data_filepath):
    Data.SP500Data()

canvas = View.Canvas(data_filepath=data_filepath)
canvas.run()