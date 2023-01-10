import plotly.graph_objects as go
import pandas as pd
from datetime import date

def freq_string_to_hours(freq: str) -> float:
    conversion_dict = {'D': 24, 'H': 1, 'MIN': 1/60, 'min': 1/60, 'S': 1/3600, 'M': 30*24}
    return int(freq[0]) * conversion_dict[freq[1]]

def add_ohlc(df: pd.DataFrame, begin=date(2022, 4, 18), end=date(2022, 4, 22), freq='1D') -> pd.DataFrame:
    "Returns a pandas dataframe with the OHLC + total volume columns"
    if df is None:
        return None
    df.set_index(pd.DatetimeIndex(df['TradeDateTime'].values), inplace=True)
    df.pop('TradeDateTime')
    #print("df: ", df)
    df['High'] = df.groupby(pd.Grouper(freq=freq)).Price.transform('max')
    df['Low'] = df.groupby(pd.Grouper(freq=freq)).Price.transform('min')
    df['Open'] = df.groupby(pd.Grouper(freq=freq)).Price.transform('first')
    df['Close'] = df.groupby(pd.Grouper(freq=freq)).Price.transform('last')
    df['Total Volume'] = df.groupby(pd.Grouper(freq=freq)).Quantity.transform('sum')
    #df.to_csv('df_before_resampling.csv')
    df = df.resample(freq).mean()
    df = df[(df.index.date >= begin) & (df.index.date <= end)]
    # Be sensible about this, the following WILL fail if you give it something weird
    hours = freq_string_to_hours(freq)
    if hours < 24:
        df = df[(df['TradeDateTime'].dt.hour >= 7) & (df['TradeDateTime'].dt.hour < 17)]
    return df

def create_dataframe(freq='1D', begin=date(2022, 4, 18), end=date(2022, 4, 22), products=['Emission', 'Energy']) -> tuple:
    #@return: a tuple of dataframes in the order emissions_DA, emissions_M01, and energy_Q01 (if applicable)
    df = pd.read_csv('Trades.csv')
    #print(df['Product'].unique())
    # Split based on product type
    # On top of that, split by contract as well
    all_contracts = []
    if 'Emission' in products:
        df_emission = df[(df['Product'] == 'Emission - Venue A') | (df['Product'] == 'Emission - Venue B')]
        #print("Contracts in df_emission ", df_emission['Contract'].unique())
        df_emission['TradeDateTime'] = pd.DatetimeIndex(df_emission['TradeDateTime'].values)
        df_emission_DA = df_emission[df_emission['Contract'] == 'DA']
        df_emission_M01 = df_emission[df_emission['Contract'] == 'M01']
        all_contracts.extend([df_emission_DA, df_emission_M01])
    if 'Energy' in products:
        df_energy = df[df['Product'] == 'Energy']
        #print("Contracts in df_energy ", df_energy['Contract'].unique())
        df_energy['TradeDateTime'] = pd.DatetimeIndex(df_energy['TradeDateTime'].values)
        df_energy_Q01 = df_energy[df_energy['Contract'] == 'Q01']
        all_contracts.append(df_energy_Q01)
    for i in range(len(all_contracts)):
        all_contracts[i] = add_ohlc(all_contracts[i], begin=begin, end=end, freq=freq)
    return tuple(all_contracts)

df_emission_DA = create_dataframe()[0]
df_emission_DA.to_csv("emissions_DA.csv")
fig = go.Figure(data=[go.Candlestick(x=df_emission_DA.index,
                    open=df_emission_DA['Open'],
                    high=df_emission_DA['High'],
                    low=df_emission_DA['Low'],
                    close=df_emission_DA['Close'])])

fig.show()