import pandas as pd
from joblib import load

# function to load the saved model and make predictions
def load_and_forecast(model_path, forecast_steps, manual_start_date=None):
    # load the sarima model
    model_fit = load(model_path)
    
    # generate the forecast
    forecasts = model_fit.forecast(steps=forecast_steps)
    
    # check if the model has a valid date index
    if model_fit.data.dates is not None:
        # use the last date from the training data
        last_date = model_fit.data.dates[-1]
    else:
        # if the model doesn't have date info, use the provided start date
        if manual_start_date is None:
            raise ValueError("model has no date info. please provide a manual start date.")
        last_date = pd.to_datetime(manual_start_date)
    
    # generate date range for the forecast period
    forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=forecast_steps, freq='M')
    
    # create a dataframe to hold the forecasted values and dates
    forecast_df = pd.DataFrame({
        'Date': forecast_dates,
        'Predicted Solar Production (GWh)': forecasts
    })
    
    return forecast_df

# example usage
model_path = 'Solar_Prediction_SARIMA.joblib'  # path to your saved model
forecast_steps = 12  # how many months you want to forecast

# if the model doesn't have date info, provide a manual start date for forecasting
manual_start_date = '2024-06-01'  # change this to an appropriate start date

forecast_df = load_and_forecast(model_path, forecast_steps, manual_start_date)

# print out the forecasted dates and values
print(forecast_df)
