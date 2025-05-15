# fred-timeseries-toolkit

```
timeseries_toolkit/
│
├── timeseries_toolkit/        <- the code folder (same name as project)
│   ├── __init__.py             <- makes it a package
│   ├── fetch.py                <- (fetch_series, resample_series, log_diff)
│   ├── stationarity.py         <- (check_stationarity, check_stationarity_diff)
│   ├── arima_models.py         <- (quick_arima_forecast, auto_arima_forecast)
│   ├── sarima_models.py        <- (sarima_forecast, auto_sarima_forecast)
│
├── examples/                  <- optional: Jupyter notebooks showing usage
│   └── basic_usage.ipynb
│
├── README.md                   <- describe project, functions
├── LICENSE                     <- (MIT recommended)
├── setup.py                    <- installable package config
├── pyproject.toml              <- (optional but modern, for packaging)
├── requirements.txt            <- dependencies (fredapi, pandas, statsmodels, matplotlib, etc.)
│
└── .gitignore                  <- ignore __pycache__/, .ipynb_checkpoints/, etc.
```
