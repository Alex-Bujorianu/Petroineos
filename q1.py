import pandas as pd

def add_missing_day(series: pd.Series) -> pd.Series:
    "Adds missing hourly data on the last day using the value of the previous day"
    series_list = series.to_list()
    last_value = series_list[-1]
    for i in range(len(series_list), len(series_list)+5, 1):
        series_list.append(last_value)
    return pd.Series(series_list)

def fill_na_from_column(df: pd.DataFrame) -> pd.DataFrame:
    "Fills missing bi-hourly data from the column with daily averages"
    index = df.index
    print("Length of index ", len(index))
    daily_values = df['dailyPrice'].to_list()
    two_h_values = df['averagePrice'].to_list()
    new_2h_values = [two_h_values[i] if not pd.isna(two_h_values[i]) else daily_values[i] for i in range(len(two_h_values))]
    to_return = pd.DataFrame({'Price': new_2h_values})
    to_return.set_index(index, inplace=True)
    return to_return

merge_df = pd.read_csv("Merge.csv")
ten_minutes = merge_df[merge_df['Resolution'] == '10MIN']
daily = merge_df[merge_df['Resolution'] == 'D']
hourly = merge_df[merge_df['Resolution'] == '1H']
hourly.pop('Resolution')
# print(ten_minutes.head())
ten_minutes['Datetime'] = pd.DatetimeIndex(ten_minutes['Datetime'].values)
ten_minutes.pop('Resolution')
ten_minutes = ten_minutes.resample('2H', origin='start', on='Datetime').mean()
# print(ten_minutes.head())
ten_minutes = ten_minutes[(ten_minutes.index.hour < 17) &
                          (ten_minutes.index.hour >= 7)]

hourly.set_index(pd.DatetimeIndex(hourly['Datetime'].values), inplace=True)
hourly.pop('Datetime')
hourly = hourly.resample('2H', origin='start').mean()
hourly = hourly[(hourly.index.hour < 17) &
                          (hourly.index.hour >= 7)]
print("Hourly \n ", hourly)
datetime_index = pd.DatetimeIndex(daily['Datetime'].values)
daily.set_index(datetime_index, inplace=True)
daily = daily.resample('2H', origin='start_day', offset='1H').ffill()
# Upsample gives us 23:00 on the 31st Oct because it's dumb
# print("Daily \n", daily)
daily.dropna(inplace=True, how='all')

# Ffill from the resampler object is in fact practically unrelated to ffill from the dataframe object
daily.ffill(inplace=True)
print("Missing values in daily data? ", daily.isnull().values.any())
daily = daily[(daily.index.hour < 17) & (daily.index.hour >= 7)]
# print("Ten minutes \n", ten_minutes)
# print("Length of daily: ", daily['Price'].size)
# print("Length of ten minutes: ", ten_minutes['Price'].size)
daily_prices = add_missing_day(daily['Price'])
daily = pd.DataFrame({'Daily Price': daily_prices})
# print("Length of daily prices ", len(daily_prices))

# You need to set the index as well, it's not smart enough to do it automatically
daily.set_index(ten_minutes.index, inplace=True)
ten_minutes['hourlyPrice'] = hourly['Price']
ten_minutes['averagePrice'] = ten_minutes[['Price', 'hourlyPrice']].mean(axis=1)
ten_minutes['dailyPrice'] = daily['Daily Price']
ten_minutes = fill_na_from_column(ten_minutes)
ten_minutes.to_csv("New_merge.csv")