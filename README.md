<h1 align="center">FRED Timeseries Analysis Package</h1>

<p align="center">
  <a href="https://pypi.org/project/fred-timeseries-toolkit/">
    <img src="https://img.shields.io/pypi/v/fred-timeseries-toolkit?label=PyPI&logo=pypi&logoColor=white&color=blue" alt="PyPI version">
  </a>
</p>

<table align="center">
  <tr>
    <td colspan="2" align="center" style="background-color: white; color: black;"><strong>Table of Contents</strong></td>
  </tr>

  <tr>
    <td style="background-color: white; color: black; padding: 10px;">
      1. <a href="#fred-timeseries-analysis-package" style="color: black;">Overview</a><br>
    </td>
    <td style="background-color: gray; color: black; padding: 10px;">
      2. <a href="#fred-api-key-requirement" style="color: black;">FRED API Key Requirement</a><br>
    </td>
  </tr>

  <tr>
    <td style="background-color: gray; color: black; padding: 10px;">
      3. <a href="#installation" style="color: black;">Installation</a><br>
    </td>
    <td style="background-color: white; color: black; padding: 10px;">
      4. <a href="#package-structure" style="color: black;">Package Structure</a><br>
    </td>
  </tr>

  <tr>
    <td style="background-color: white; color: black; padding: 10px;">
      5. <a href="#techniques-and-defaults" style="color: black;">Techniques and Defaults</a><br>
    </td>
    <td style="background-color: gray; color: black; padding: 10px;">
      6. <a href="#function-descriptions" style="color: black;">Function Descriptions</a><br>
  </tr>

  <tr>
    <td style="background-color: gray; color: black; padding: 10px;">
      7. <a href="#summary" style="color: black;">Summary</a><br>
      &nbsp;&nbsp;&nbsp;- <a href="#functions-and-purposes" style="color: black;">Functions and Purposes</a><br>
      &nbsp;&nbsp;&nbsp;- <a href="#techniques-used" style="color: black;">Techniques Used</a><br>
    </td>
    <td style="background-color: white; color: black; padding: 10px;">
      8. <a href="#license" style="color: black;">License</a><br>
    </td>
  </tr>

  <tr>
    <td colspan="2" style="background-color: white; color: black; padding: 10px;">
 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
      9. <a href="#contributing" style="color: black;">Contributing</a>
    </td>
  </tr>
</table>





**FRED-Timeseries-Analysis-Package** is a Python package for fetching, analyzing, and forecasting economic time series data, built on top of [FRED](https://fred.stlouisfed.org/), `pandas`, and `statsmodels`.

It includes:
- Data fetching and resampling
- Stationarity testing (ADF)
- ARIMA and SARIMA modeling
- Automatic model selection
- Jupyter-optimized visualizations

An example notebook is included in the `examples/` folder.

## FRED API Key Requirement

In order to fetch data from the FRED database, you must obtain a free FRED API key.

**How to get a FRED API key:**
1. Visit the [FRED API Key Request page](https://fredaccount.stlouisfed.org/apikey).
2. Create a free account if you do not already have one.
3. Request an API key from your account dashboard.
4. You will receive a personal API key that you can use in all fetch operations.

**Where to use the API key:**
- The `fetch_series` function requires your FRED API key as an input.
- Provide it once when calling `fetch_series`, and your data will load automatically.

Example usage:

```python
fred_api_key = 'your-api-key-here'
gdp = fetch_series('GDP', start_date='2010-01-01', api_key=fred_api_key)
```
---

## Package Structure

```
FRED-Timeseries-Analysis-Package/
│
├── timeseries_toolkit/        <- the code folder (same name as PyPI project)
│   ├── __init__.py             <- makes it a package
│   ├── ts_toolkit.py         <- (check_stationarity, check_stationarity_diff)

│
├── examples/                  <- Jupyter notebooks showing usage
│   └── basic_usage.ipynb
│
├── README.md                   <- describe project, functions
├── pyproject.toml              <- (for packaging)
├── requirements.txt            <- dependencies (fredapi, pandas, statsmodels, matplotlib, etc.)
```

---
## Installation

You can install the package directly from PyPI:

```python
pip install fred-timeseries-toolkit
```
Or install it from the GitHub repository:

```bash
pip install git+https://github.com/RoryQo/FRED-Timeseries-Analysis-Package.git
```

**Requirements** (automatically handled with pip install):

- `fredapi`
- `pandas`
- `statsmodels`
- `matplotlib`
- `scikit-learn`
- `numpy`

Make sure you have Python 3.8 or later.


> **Important Note:**  
The `fredapi` package must be installed and imported separately when using this toolkit.  
While `fredapi` is included as a dependency, users must create and manage their own `Fred` object with their FRED API key when working with the toolkit’s functions.

```python
from fredapi import Fred
fred = Fred(api_key='your-api-key-here')
```


---

## Techniques and Defaults

- **Missing Data Handling:**  
  By default, series are cleaned using `.dropna()`. When resampling, missing periods are filled by **forward-fill (`ffill`)** unless otherwise specified.

- **Frequency Handling:**  
  Functions can **infer** time series frequency from the index or allow **manual override** (`freq` argument).

- **Model Stability Checks:**  
  Automatic model selection (ARIMA and SARIMA) rejects unstable fits (e.g., AR/MA terms near 1, singular covariance matrices).

- **Plotting:**  
  All forecasting functions plot observed + forecasted values unless `plot=False`.

---

#  Function Descriptions

### `Import`

```python
from fred_timeseries_toolkit.ts_toolkit import (
    fetch_series,
    resample_series,
    log_diff,
    check_stationarity,
    check_stationarity_diff,
    quick_arima_forecast,
    quick_arima_forecast_testing,
    auto_arima_forecast,
    sarima_forecast,
    auto_sarima_forecast)
from fredapi import Fred
```

### `fetch_series`

**Description:**  
Fetches a single time series from the FRED database.

**Inputs:**
- `series_id` (str): The FRED series ID.
- `start_date`, `end_date` (optional, str or datetime): Date range.
- `api_key` (str): User’s FRED API key.

**Outputs:**
- `pandas.Series` indexed by dates.

**Default behavior:**  
Entire available series is fetched if no date range is specified.

**Reminder:**  
This function requires that you manage your own `Fred` object separately.  
Ensure that `fredapi` is installed and imported before fetching data.  
See the **Installation** section for guidance on how to properly import `fredapi`.

---

### `resample_series`

**Description:**  
Resamples a series to a new frequency.

**Inputs:**
- `series` (pandas.Series): Input series.
- `freq` (str): Target frequency (`'Q'`, `'M'`, `'A'`, etc.).
- `method` (str): Fill method (`'ffill'` or `'bfill'`).

**Outputs:**
- `pandas.Series` resampled.

**Default behavior:**  
Forward-fill (`ffill`) is used for missing values.

---

### `log_diff`

**Description:**  
Applies log transformation and differencing to stabilize variance and mean.

**Inputs:**
- `series` (pandas.Series): Input series.
- `periods` (int): Number of periods to difference.

**Outputs:**
- `pandas.Series` after log and differencing.

**Default behavior:**  
1-period difference.

---


### `check_stationarity`

**Description:**  
Performs the Augmented Dickey-Fuller (ADF) test for stationarity.

**Inputs:**
- `series` (pandas.Series)
- `alpha` (float): Significance level (default 0.05).
- `regression` (str): Trend type ('c', 'ct', 'ctt', 'n').
- `autolag` (str): Criterion for lag selection ('AIC', 'BIC').
- `resample_freq`, `resample_method` (optional): If provided, resample before testing.

**Outputs:**
- Dictionary summarizing ADF test results.

**Default behavior:**  
Original series used without resampling. Displays formatted summary and plot.

---

### `check_stationarity_diff`

**Description:**  
Same as `check_stationarity` but first differences the series before applying the ADF test.

**Inputs:**  
Same as `check_stationarity`.

**Outputs:**
- Dictionary summarizing ADF test on differenced series.

**Default behavior:**  
First difference applied automatically.

---

### `quick_arima_forecast`

**Description:**  
Fits an ARIMA model and forecasts future periods.

**Inputs:**
- ARIMA orders (`p`, `d`, `q`).
- `forecast_steps` (int): Number of periods ahead to forecast.

**Outputs:**
- Dictionary with model fit, forecast, AIC, BIC.

**Default behavior:**  
Forecast 5 future periods, plot results.

---

### `quick_arima_forecast_testing`

**Description:**  
Splits data into train/test sets, fits ARIMA, forecasts, and evaluates RMSE.

**Inputs:**
- `train_ratio` (float): Fraction of data to train on (default 0.8).

**Outputs:**
- Dictionary with model, forecast, AIC, BIC, RMSE.

**Default behavior:**  
80% train / 20% test split, forecast matching test set size.

---

### `auto_arima_forecast`

**Description:**  
Automatically searches ARIMA(p,d,q) models using AIC or BIC.

**Inputs:**
- Search ranges for p, d, q.
- `ic` (str): 'aic' or 'bic'.

**Outputs:**
- Best model, best order, forecast, AIC, BIC.

**Default behavior:**  
Minimizes AIC, autoreject unstable models.

---


### `sarima_forecast`

**Description:**  
Manually fits SARIMA(p,d,q)x(P,D,Q,s) model.

**Inputs:**
- Non-seasonal (`p,d,q`) and seasonal (`P,D,Q,s`) orders.
- Forecast frequency (`freq`) optional.

**Outputs:**
- Model fit, forecast, AIC, BIC.

**Default behavior:**  
No seasonality unless specified. Forecast 5 periods ahead.

---

### `auto_sarima_forecast`

**Description:**  
Automatically selects best SARIMA(p,d,q)x(P,D,Q,s) model.

**Inputs:**
- Search ranges for p, d, q, P, D, Q, and seasonality s.
- `ic` (str): 'aic' or 'bic'.

**Outputs:**
- Best model fit, best order, forecast, AIC, BIC.

**Default behavior:**  
Default seasonality `s=4` (quarterly). Autoreject unstable models.

---

# Summary


## Functions and Purposes

| Function | Purpose |
|:---------|:--------|
| fetch_series | Fetch time series data from FRED |
| resample_series | Resample to new frequency |
| log_diff | Log-transform and difference a series |
| check_stationarity | ADF stationarity test |
| check_stationarity_diff | ADF test after differencing |
| quick_arima_forecast | Fit ARIMA and forecast |
| quick_arima_forecast_testing | ARIMA with train/test evaluation |
| auto_arima_forecast | Auto-select ARIMA model |
| sarima_forecast | Fit SARIMA manually |
| auto_sarima_forecast | Auto-select SARIMA model |



## Techniques Used

| Feature | Behavior |
|:--------|:---------|
| Missing Data | `.dropna()` at start; `resample()` uses `'ffill'` |
| Frequency | Infer from index if not provided, or manually set |
| Model Stability | Auto-reject AR/MA terms near unit root or singular covariance |
| Plotting | Enabled by default, can be turned off |
| Forecasting | Extends beyond last date, aligns future dates automatically |


---

## License

This project is licensed under the MIT License.  
See the `LICENSE` file for details.

---

## Contributing

Contributions are welcome!

If you would like to improve this package, feel free to open:
- An Issue (for bug reports, feature requests, or clarifications)
- A Pull Request (for proposed changes or additions)

When contributing, please:
- Keep code style clean and readable
- Follow the organization structure (group similar functions together)
- Include clear function descriptions (Inputs, Outputs, Purpose)
- Update the `examples/` notebook if you add major functionality

For large changes, it is recommended to open an issue first to discuss the proposed approach.


---



