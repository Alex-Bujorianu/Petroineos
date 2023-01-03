import pandas as pd
import pandas_market_calendars as mcal
from datetime import time, datetime

def upsample_daily_data(to_upsample: pd.Series, intended_frequency=2):
    ratio = 24/intended_frequency
    new_data = []
    for number in to_upsample:
        for i in range(ratio):
            new_data.append(number)
    return pd.Series(new_data)

def resample_index(index, freq):
    """Resamples each day in the daily `index` to the specified `freq`.

    Parameters
    ----------
    index : pd.DatetimeIndex
        The frequency index to resample
    freq : str
        A pandas frequency string

    Returns
    -------
    pd.DatetimeIndex
        The resampled index

    """
    assert isinstance(index, pd.DatetimeIndex)
    start_date = index.min()
    end_date = index.max() + pd.DateOffset(days=1)
    resampled_index = pd.date_range(start_date, end_date, freq=freq)[:-1]
    return resampled_index


my_cal = mcal.get_calendar('NYSE', open_time=time(5, 0), close_time=time(15, 00))
early = my_cal.schedule(start_date='2021-11-01', end_date='2021-11-30', tz='America/New_York')
print(my_cal.tz.zone)
print(early)
range_2h = mcal.date_range(early, frequency='2H')
print(range_2h)
# Note: 6 and 7 November are missing because they are weekends
# Likely not the only ones
merge_df = pd.read_csv("Merge.csv")
merge_df.dropna(inplace=True, how="all")
merge_df.groupby(['Resolution'])
print(merge_df.head())
daily = merge_df[merge_df['Resolution'] == 'D']
datetime_index = pd.DatetimeIndex(daily['Datetime'].values)
daily.set_index(datetime_index, inplace=True)
daily.pop('Datetime')
# Fill in missing values (weekends) with valid value from previous row (Friday)
#daily.ffill(inplace=True)
print("Missing values in daily data? ", daily.isnull().values.any())
ten_minutes = merge_df[merge_df['Resolution'] == '10MIN']
print(daily.head())
datetime_index = resample_index(pd.DatetimeIndex(ten_minutes['Datetime'].values), freq='2H')
new_df = pd.DataFrame(index=datetime_index)
print(new_df)
ten_minutes.set_index(datetime_index, inplace=True)
# Columns no longer needed now that it is indexed
ten_minutes.pop('Datetime')
ten_minutes.pop('Resolution')
t_index = pd.DatetimeIndex(pd.date_range(start='2021-11-01 7:00:00', end='2021-11-30 15:00:00', freq="2h"))
ten_minutes = ten_minutes.resample('2H', origin='start').mean()
ten_minutes.to_csv("10_minutes.csv")
print(ten_minutes.head())
#ten_minutes.reindex(range_2h, copy=False)
daily_copy = daily.resample('2H', origin='start_day').ffill()#.reindex(range_2h)
#daily_copy.reindex(range_2h, copy=False)
print("Daily copy after resampling \n", daily_copy)
print("Ten minutes after resampling to 2h \n", ten_minutes)
#daily_copy.reindex(range_2h, copy=False)
print(ten_minutes['Price'].size)
print(daily_copy['Price'].size)
assert ten_minutes['Price'].size == daily_copy['Price'].size
print(daily_copy.head())
ten_minutes['Daily_mean'] = daily_copy['Price']
ten_minutes.to_csv("New_merge.csv")


