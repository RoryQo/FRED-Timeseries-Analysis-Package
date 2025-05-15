# fred_timeseries_toolkit/__init__.py

import warnings
from statsmodels.tools.sm_exceptions import ValueWarning

# Suppress harmless statsmodels warnings about missing frequency
warnings.simplefilter("ignore", ValueWarning)

from .ts_toolkit import (
    in_notebook,
    fetch_series,
    resample_series,
    log_diff,
    check_stationarity,
    check_stationarity_diff,
    quick_arima_forecast,
    quick_arima_forecast_testing,
    auto_arima_forecast,
    sarima_forecast,
    auto_sarima_forecast
)
