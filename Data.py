import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.patches as patches



class StockMinutePrices:
    def __init__(self, ticker):
        self.ticker = ticker
        self.percents = None
        self.minutes = None
        self.colors = None

    def get_minutes(self):
        stock = yf.Ticker(self.ticker)
        data = stock.history(start="2024-07-17", end="2024-07-18", interval='1m')
        closing_price = stock.history(start="2024-07-16", period="1d")['Close'].iloc[0]

        if data is not None:
            prices = data['Close'].tolist()
            percents = [(float(price) - closing_price) / closing_price for price in prices]
            timestamps = data.index.tolist()
            minutes = [timestamp.strftime('%Y-%m-%d %H:%M:%S') for timestamp in timestamps]
            self.percents = percents
            self.minutes = minutes
        else:
            return "Data not fetched yet. Use fetch_yesterday_prices() first."

    def get_colors(self):
        colors = []
        for percent in self.percents:
            percent = float(percent)
            if percent < 0.50:
                red = 1.0
                green = 1.0 - percent * 2
                blue = 1.0 - percent * 2
            else:
                red = 1.0 - (percent - 0.50) * 2
                green = 1.0
                blue = 1.0 - (percent - 0.50) * 2
            colors.append((red, green, blue))
        return colors

stock = StockMinutePrices('AAPL')
stock.get_minutes()

def value_to_color(value, min_val, max_val):
    normalized_value = (value - min_val) / (max_val - min_val)  # Normalize to range [0, 1]
    if value >= 0:
        return (0, 1 - normalized_value, 0)  # Green shades
    else:
        return (1 - normalized_value, 0, 0)  # Red shades

values = stock.percents
print(values)
min_val, max_val = min(values), max(values)

fig, ax = plt.subplots()
width, height = 0.2, 0.2
x_start, y_start = 0.1, 0.5

for i, value in enumerate(values):
    color = value_to_color(value, min_val, max_val)
    rect = patches.Rectangle((x_start + i * width, y_start), width, height, linewidth=1, edgecolor=color, facecolor=color)
    ax.add_patch(rect)

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_aspect('equal')
ax.axis('off')

plt.show()