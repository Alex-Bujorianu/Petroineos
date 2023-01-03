import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

def split_years(dt: pd.DataFrame):
    "Adds the year of the Date as a separate column in-place"
    dt['year'] = dt['Date'].dt.year


def clean_dates(df: pd.DataFrame) -> pd.DataFrame:
    "Remove faulty dates from the dataframe"
    bad_dates = []
    i = 0
    for date in df['Date']:
        try:
            date_object = datetime.strptime(date, '%d/%m/%Y')
        except:
            bad_dates.append(i)
        i += 1
    return df.drop(df.index[bad_dates], inplace=False)

consumption = pd.read_csv("Consumption.csv")
print(consumption.iloc[1461])
# Some of the dates appear to be corrupt
consumption = clean_dates(consumption)
consumption['Date'] = pd.to_datetime(consumption['Date'].values, dayfirst=True)
split_years(consumption)
consumption.set_index(pd.DatetimeIndex(consumption['Date'].values, dayfirst=True), inplace=True)
consumption.index = consumption.index.strftime('%m-%d')
consumption.drop(columns='Date', inplace=True)
print(consumption)

# Plots
cons_2016_2020 = consumption[consumption['year'] <= 2020]
print(cons_2016_2020.groupby('year').mean())
ax = cons_2016_2020.groupby('year').mean().plot(style='b--')
ax.locator_params(integer=True)
plt.title("Consumption from 2016–2020")
plt.show()
consumption[consumption['year'] == 2021].plot(y='Consumption', use_index=True, kind='line')
plt.title("Consumption during the year 2021")
plt.show()
consumption[consumption['year'] == 2022].plot(y='Consumption', use_index=True, kind='line')
plt.title("Consumption during the year 2022")
plt.show()