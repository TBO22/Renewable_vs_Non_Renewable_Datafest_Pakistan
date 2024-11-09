import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error
from joblib import dump, load

# load and prep the data
def load_and_preprocess_data(file_path):
    df = pd.read_csv(file_path)

    # convert 'observation date' to datetime
    df['Observation Date'] = pd.to_datetime(df['Observation Date'], format='%d-%b-%Y')

    # filter the data to only keep solar power generation
    solar_df = df[df['Series name'].str.contains('Solar', case=False, na=False)]

    # sort the data by date and fill any missing values
    solar_df = solar_df[['Observation Date', 'Observation Value']].sort_values(by='Observation Date')

    # handle missing values
    solar_df['Observation Value'] = solar_df['Observation Value'].ffill().bfill()

    # set the 'observation date' as index for the time series
    solar_df.set_index('Observation Date', inplace=True)

    return solar_df

# check if the data is stationary using adf test
def test_stationarity(timeseries):
    adf_result = adfuller(timeseries)
    print(f'adf statistic: {adf_result[0]}')
    print(f'p-value: {adf_result[1]}')
    if adf_result[1] > 0.05:
        print("data is non-stationary")
    else:
        print("data is stationary")

# train sarima model and save it
def train_sarima_model(solar_df, p=1, d=1, q=1, P=1, D=1, Q=1, s=12):
    model = SARIMAX(solar_df['Observation Value'], order=(p, d, q),
                    seasonal_order=(P, D, Q, s))
    model_fit = model.fit()
    print(model_fit.summary())
    dump(model_fit, 'Solar_Prediction_SARIMA.joblib')
    return model_fit

# generate forecasts for the next few months
def generate_forecasts(model_fit, solar_df, forecast_steps):
    forecasts = model_fit.forecast(steps=forecast_steps)

    # set up a date range for the forecast
    forecast_dates = pd.date_range(start=solar_df.index[-1] + pd.DateOffset(months=1),
                                   periods=forecast_steps, freq='M')

    # combine the forecasts with the dates
    forecast_df = pd.DataFrame({
        'Date': forecast_dates,
        'Predicted Solar Production (GWh)': forecasts.values
    })

    return forecast_df

# plot the historical and predicted data
def plot_forecasts(solar_df, forecast_df):
    plt.figure(figsize=(10, 6))

    # plot historical data as bars
    plt.bar(solar_df.index, solar_df['Observation Value'], width=20, label='historical data', color='cyan')

    # plot forecasted data as bars
    plt.bar(forecast_df['Date'], forecast_df['Predicted Solar Production (GWh)'], width=20, label='predicted data', color='green')

    # add labels and title
    plt.title('solar power generation: historical and forecasted data', fontsize=14)
    plt.xlabel('date', fontsize=12)
    plt.ylabel('solar power generation (MWh)', fontsize=12)

    # add a legend
    plt.legend()

    # show the plot
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# create forecasts for different time frames and save them to csv
def create_forecast_df(solar_df, model_fit):
    # define how long to predict (in months)
    time_ranges = {
        "6 months": 6,
        "1 year": 12,
        "2 years": 24,
        "5 years": 60,
        "10 years": 120,
        "15 years": 180
    }

    # loop through each time range and generate forecasts
    for label, steps in time_ranges.items():
        forecast_df = generate_forecasts(model_fit, solar_df, steps)

        # plot the historical vs predicted data
        plot_forecasts(solar_df, forecast_df)

        # save the forecast data to a csv file
        forecast_df.to_csv(f'forecast_{label.replace(" ", "_").lower()}.csv', index=False)

        # print forecast data for debugging
        print(f'\nforecast for {label}:\n', forecast_df)

# check how well the model did
def evaluate_model(model_fit, solar_df):
    # predict the last 12 months of data
    predictions = model_fit.predict(start=len(solar_df)-12, end=len(solar_df)-1, dynamic=False)

    # calculate the mean squared error to see how far off we were
    error = mean_squared_error(solar_df['Observation Value'][-12:], predictions)
    print(f'mean squared error: {error}')

# main function to load data, train the model, and make predictions
def main(file_path):
    # step 1: load and prep the data
    solar_df = load_and_preprocess_data(file_path)

    # step 2: check if the data is stationary
    print("checking stationarity of the data:")
    test_stationarity(solar_df['Observation Value'])

    # step 3: train the sarima model
    print("\ntraining sarima model:")
    model_fit = train_sarima_model(solar_df, p=1, d=1, q=1, P=1, D=1, Q=1, s=12)

    # step 4: make forecasts and save them to csv
    print("\ngenerating forecasts and saving to csv:")
    create_forecast_df(solar_df, model_fit)

    # step 5: evaluate how well the model performed
    print("\nevaluating the model:")
    evaluate_model(model_fit, solar_df)

# replace with your dataset's file path
file_path = '/content/dataset.csv'
main(file_path)
