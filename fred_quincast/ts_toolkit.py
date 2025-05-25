# --- Imports ---
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fredapi import Fred
from statsmodels.tsa.stattools import adfuller
import io
import base64
from IPython.display import display, HTML
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
import io
import base64
from statsmodels.tsa.arima.model import ARIMA
import itertools
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from fredapi import Fred

# ----------------------------------
# Helper Functions
# ----------------------------------

def in_notebook():
    try:
        from IPython import get_ipython
        if 'IPKernelApp' not in get_ipython().config:
            return False
    except Exception:
        return False
    return True

# ----------------------------------
# Data Fetching and Preprocessing
# ----------------------------------



def fetch_series(series_id, start_date=None, end_date=None, api_key=None):
    """
    Fetch a FRED series using its ID.

    Args:
        series_id (str): FRED series identifier.
        start_date (str or datetime, optional): Start date for series.
        end_date (str or datetime, optional): End date for series.
        api_key (str): FRED API key (required).

    Returns:
        pandas.Series: Time series data.
    """
    if api_key is None:
        raise ValueError("An API key must be provided to fetch data from FRED.")

    fred = Fred(api_key=api_key)
    series = fred.get_series(series_id)
    series.name = series_id

    if start_date or end_date:
        series = series.loc[start_date:end_date]

    return series

def resample_series(series, freq='Q', method='ffill'):
    """
    Resample a series to a new frequency.
    """
    resampled = series.resample(freq).mean()
    if method == 'ffill':
        resampled = resampled.ffill()
    elif method == 'bfill':
        resampled = resampled.bfill()
    return resampled

def log_diff(series, periods=1):
    """
    Apply log difference transformation to a series.
    """
    log_series = np.log(series)
    log_diffed = log_series.diff(periods=periods).dropna()
    return log_diffed

# ----------------------------------
# Stationarity Tests
# ----------------------------------

def check_stationarity(series, alpha=0.05, regression='c', autolag='AIC', verbose=True, plot=True, resample_freq=None, resample_method='ffill'):
    """
    Perform Augmented Dickey-Fuller test to check stationarity of a time series,
    with optional resampling, formatted summary, and side-by-side plot if inside Jupyter.

    Args:
        series (pandas.Series): Time series data.
        alpha (float): Significance level for rejecting stationarity.
        regression (str): Regression type ('c', 'ct', 'ctt', 'n').
        autolag (str): Lag selection criterion ('AIC', 'BIC', etc.).
        verbose (bool): Whether to display summary.
        plot (bool): Whether to plot the series.
        resample_freq (str, optional): Resample frequency ('D', 'W', 'M', 'Q', 'A', etc.).
        resample_method (str, optional): Method to fill missing values after resampling ('ffill' or 'bfill').

    Returns:
        dict: Dictionary with ADF test results.
    """
    original_name = series.name if series.name else "Unnamed Series"
    series = series.dropna()

    # Optional resample
    if resample_freq:
        series = series.resample(resample_freq).mean()
        if resample_method == 'ffill':
            series = series.ffill()
        elif resample_method == 'bfill':
            series = series.bfill()
        series = series.dropna()
    
    # --- Generate title and y-axis label ---
    freq_mapping = {
        'D': 'Daily',
        'W': 'Weekly',
        'M': 'Monthly',
        'Q': 'Quarterly',
        'A': 'Annual',
        'Y': 'Annual'
    }
    freq_name = freq_mapping.get(resample_freq, '') if resample_freq else ''
    plot_title = f"{original_name} {freq_name}".strip()
    y_label = original_name

    # Perform ADF test
    result = adfuller(series, regression=regression, autolag=autolag)

    adf_stat = result[0]
    p_value = result[1]
    used_lag = result[2]
    n_obs = result[3]
    critical_values = result[4]
    ic_best = result[5]

    summary = {
        'adf_statistic': adf_stat,
        'p_value': p_value,
        'used_lag': used_lag,
        'n_obs': n_obs,
        'aic_bic_value': ic_best,
        'critical_values': critical_values
    }

    if in_notebook():
        from IPython.display import display, HTML

        html_summary = f"""
        <h3>Augmented Dickey-Fuller Test Results</h3>
        <ul>
            <li><strong>ADF Statistic:</strong> {adf_stat:.4f}</li>
            <li><strong>P-value:</strong> {p_value:.4f}</li>
            <li><strong>Used Lag:</strong> {used_lag}</li>
            <li><strong>Number of Observations:</strong> {n_obs}</li>
            <li><strong>{autolag} selected IC value:</strong> {ic_best:.4f}</li>
        </ul>
        <h4>Critical Values</h4>
        <ul>
        """
        for key, value in critical_values.items():
            html_summary += f"<li>{key}: {value:.4f}</li>"
        html_summary += "</ul>"

        if p_value < alpha:
            html_summary += f"<p style='color:green;'><strong> Stationary (reject H₀ at {alpha*100:.0f}% level)</strong></p>"
        else:
            html_summary += f"<p style='color:red;'><strong> Not Stationary (fail to reject H₀ at {alpha*100:.0f}% level)</strong></p>"

        html_output = "<div style='display: flex; flex-direction: row;'>"
        html_output += f"<div style='flex: 50%; padding-right: 20px;'>{html_summary}</div>"

        if plot:
            buf = io.BytesIO()
            fig, ax = plt.subplots(figsize=(6,4))
            series.plot(ax=ax, title=plot_title)
            ax.set_ylabel(y_label)
            plt.tight_layout()
            fig.savefig(buf, format='png')
            plt.close(fig)
            encoded = base64.b64encode(buf.getbuffer()).decode("ascii")
            img_html = f"<img src='data:image/png;base64,{encoded}'/>"
            html_output += f"<div style='flex: 50%;'>{img_html}</div>"

        html_output += "</div>"

        display(HTML(html_output))

    else:
        if verbose:
            print("Augmented Dickey-Fuller Test Results")
            print(f"ADF Statistic: {adf_stat:.4f}")
            print(f"P-value: {p_value:.4f}")
            print(f"Used Lag: {used_lag}")
            print(f"Number of Observations: {n_obs}")
            print(f"{autolag} selected IC value: {ic_best:.4f}")
            for key, value in critical_values.items():
                print(f"Critical Value ({key}): {value:.4f}")
            if p_value < alpha:
                print(f"\n The series IS stationary (reject H₀ at {alpha*100:.0f}% level).")
            else:
                print(f"\n The series IS NOT stationary (fail to reject H₀ at {alpha*100:.0f}% level).")
        
        if plot:
            series.plot(title=plot_title, figsize=(10,5))
            plt.ylabel(y_label)
            plt.show()

    return summary

#### First Diff Function


def check_stationarity_diff(series, alpha=0.05, autolag='AIC', regression='c',
                             verbose=True, plot=True, resample_freq=None, resample_method='ffill'):
    """
    Perform Augmented Dickey-Fuller test to check stationarity of the **first-differenced** series,
    with optional resampling, formatted summary, and side-by-side plot if inside Jupyter.

    Args:
        series (pandas.Series): Time series data.
        alpha (float): Significance level for rejecting stationarity.
        autolag (str): Lag selection method ('AIC', 'BIC', 't-stat', or None).
        regression (str): Regression type ('c', 'ct', 'ctt', 'n').
        verbose (bool): Whether to display summary.
        plot (bool): Whether to plot the series.
        resample_freq (str, optional): Resample frequency ('D', 'W', 'M', 'Q', 'A', etc.).
        resample_method (str, optional): Method to fill missing values after resampling ('ffill' or 'bfill').

    Returns:
        dict: Dictionary with ADF test results (only if assigned).
    """
    original_name = series.name if series.name else "Unnamed Series"
    units_label = series.attrs.get('units', '')
    series = series.dropna()

    # Optional resample
    if resample_freq:
        series = series.resample(resample_freq).mean()
        if resample_method == 'ffill':
            series = series.ffill()
        elif resample_method == 'bfill':
            series = series.bfill()
        series = series.dropna()
    
    # First difference
    series = series.diff().dropna()

    # --- Generate plot title and y-axis label ---
    freq_mapping = {
        'D': 'Daily',
        'W': 'Weekly',
        'M': 'Monthly',
        'Q': 'Quarterly',
        'A': 'Annual',
        'Y': 'Annual'
    }
    freq_name = freq_mapping.get(resample_freq, '') if resample_freq else ''
    plot_title = f"{original_name} (First Difference {freq_name})".strip()
    y_label = f"Δ {original_name} ({units_label})" if units_label else f"Δ {original_name}"

    # Perform ADF test
    result = adfuller(series, regression=regression, autolag=autolag)

    adf_stat = result[0]
    p_value = result[1]
    used_lag = result[2]
    n_obs = result[3]
    critical_values = result[4]
    ic_best = result[5]

    summary = {
        'adf_statistic': adf_stat,
        'p_value': p_value,
        'used_lag': used_lag,
        'n_obs': n_obs,
        'aic_bic_value': ic_best,
        'critical_values': critical_values
    }

    if in_notebook():
        from IPython.display import display, HTML

        html_summary = f"""
        <h3>Augmented Dickey-Fuller Test Results (First Difference)</h3>
        <ul>
            <li><strong>ADF Statistic:</strong> {adf_stat:.4f}</li>
            <li><strong>P-value:</strong> {p_value:.4f}</li>
            <li><strong>Used Lag:</strong> {used_lag}</li>
            <li><strong>Number of Observations:</strong> {n_obs}</li>
            <li><strong>{autolag} selected IC value:</strong> {ic_best:.4f}</li>
        </ul>
        <h4>Critical Values</h4>
        <ul>
        """
        for key, value in critical_values.items():
            html_summary += f"<li>{key}: {value:.4f}</li>"
        html_summary += "</ul>"

        if p_value < alpha:
            html_summary += f"<p style='color:green;'><strong> Stationary (reject H₀ at {alpha*100:.0f}% level)</strong></p>"
        else:
            html_summary += f"<p style='color:red;'><strong> Not Stationary (fail to reject H₀ at {alpha*100:.0f}% level)</strong></p>"

        html_output = "<div style='display: flex; flex-direction: row;'>"
        html_output += f"<div style='flex: 50%; padding-right: 20px;'>{html_summary}</div>"

        if plot:
            buf = io.BytesIO()
            fig, ax = plt.subplots(figsize=(6,4))
            series.plot(ax=ax, title=plot_title)
            ax.set_ylabel(y_label)
            plt.tight_layout()
            fig.savefig(buf, format='png')
            plt.close(fig)
            encoded = base64.b64encode(buf.getbuffer()).decode("ascii")
            img_html = f"<img src='data:image/png;base64,{encoded}'/>"
            html_output += f"<div style='flex: 50%;'>{img_html}</div>"

        html_output += "</div>"

        display(HTML(html_output))

    else:
        if verbose:
            print("Augmented Dickey-Fuller Test Results (First Difference)")
            print(f"ADF Statistic: {adf_stat:.4f}")
            print(f"P-value: {p_value:.4f}")
            print(f"Used Lag: {used_lag}")
            print(f"Number of Observations: {n_obs}")
            print(f"{autolag} selected IC value: {ic_best:.4f}")
            for key, value in critical_values.items():
                print(f"Critical Value ({key}): {value:.4f}")
            if p_value < alpha:
                print(f"\n The differenced series IS stationary (reject H₀ at {alpha*100:.0f}% level).")
            else:
                print(f"\n The differenced series IS NOT stationary (fail to reject H₀ at {alpha*100:.0f}% level).")
        
        if plot:
            series.plot(title=plot_title, figsize=(10,5))
            plt.ylabel(y_label)
            plt.show()


    return summary
# ----------------------------------
# ARIMA Models
# ----------------------------------

#### Quick test

def quick_arima_forecast_testing(series, ar_order=1, diff_order=0, ma_order=0,
                          train_ratio=0.8, forecast_steps=None, plot=True, verbose=True,
                          manual_lags=None):
    """
    Quick fit and assess an ARIMA model on a univariate time series.

    Args:
        series (pandas.Series): The time series to model.
        ar_order (int): AR (autoregressive) order (p).
        diff_order (int): Differencing order (d).
        ma_order (int): MA (moving average) order (q).
        train_ratio (float): Ratio of data to use for training.
        forecast_steps (int, optional): How many periods ahead to forecast. If None, forecast length of test set.
        plot (bool): Whether to plot actual vs forecasted.
        verbose (bool): Whether to print model fit summary.
        manual_lags (tuple, optional): If given, manually specify (p,d,q) lags instead of using ar_order, diff_order, ma_order.

    Returns:
        dict: Results including model, forecast, AIC, BIC, and RMSE.
    """
    series = series.dropna()

    n_train = int(len(series) * train_ratio)
    train = series.iloc[:n_train]
    test = series.iloc[n_train:]

    # Determine how many steps to forecast
    steps = forecast_steps if forecast_steps is not None else len(test)

    # Use manual lags if specified
    if manual_lags is not None:
        p, d, q = manual_lags
    else:
        p, d, q = ar_order, diff_order, ma_order

    # Fit ARIMA model
    model = ARIMA(train, order=(p, d, q))
    model_fit = model.fit()

    # Forecast
    forecast = model_fit.forecast(steps=steps)

    # Adjust residuals comparison depending on forecast horizon
    if steps <= len(test):
        test_to_compare = test.iloc[:steps]
    else:
        test_to_compare = test

    residuals = test_to_compare - forecast.iloc[:len(test_to_compare)]
    rmse = (residuals**2).mean()**0.5 if len(test_to_compare) > 0 else None

    results = {
        'model_fit': model_fit,
        'forecast': forecast,
        'aic': model_fit.aic,
        'bic': model_fit.bic,
        'rmse': rmse
    }

    if verbose:
        print(f"ARIMA({p},{d},{q}) Fit Summary:")
        print(model_fit.summary())
        if rmse is not None:
            print(f"\nForecast RMSE (over {len(test_to_compare)} periods): {rmse:.4f}")
        else:
            print("\nForecast RMSE: Not computable (no test data available).")

    if plot:
        fig, ax = plt.subplots(figsize=(10,6))
        train.plot(ax=ax, label='Train')
        test.plot(ax=ax, label='Test', color='gray')
        forecast.plot(ax=ax, label='Forecast', color='red', linestyle='--')
        ax.set_title(f"ARIMA({p},{d},{q}) Forecast vs Actual")
        ax.set_ylabel(series.name if series.name else "Value")
        ax.legend()
        plt.tight_layout()
        plt.show()

    return results



# Forecast 
def quick_arima_forecast(series, ar_order=1, diff_order=0, ma_order=0,
                          forecast_steps=5, plot=True, verbose=True,
                          manual_lags=None):
    """
    Quick fit and assess an ARIMA model on a univariate time series,
    optionally forecasting into the future beyond observed data.

    Args:
        series (pandas.Series): The time series to model.
        ar_order (int): AR (autoregressive) order (p).
        diff_order (int): Differencing order (d).
        ma_order (int): MA (moving average) order (q).
        forecast_steps (int): How many periods ahead to forecast.
        plot (bool): Whether to plot actual + forecasted data.
        verbose (bool): Whether to print model fit summary.
        manual_lags (tuple, optional): If given, manually specify (p,d,q) lags instead of ar_order/diff_order/ma_order.

    Returns:
        dict: Results including model, forecast, AIC, BIC.
    """
    series = series.dropna()

    # Use manual lags if specified
    if manual_lags is not None:
        p, d, q = manual_lags
    else:
        p, d, q = ar_order, diff_order, ma_order

    # Fit ARIMA on entire series
    model = ARIMA(series, order=(p, d, q))
    model_fit = model.fit()

    # Forecast future periods
    forecast = model_fit.forecast(steps=forecast_steps)

    results = {
        'model_fit': model_fit,
        'forecast': forecast,
        'aic': model_fit.aic,
        'bic': model_fit.bic
    }

    if verbose:
        print(f"ARIMA({p},{d},{q}) Fit Summary:")
        print(model_fit.summary())
        print(f"\nForecasted {forecast_steps} periods beyond last date.")

    if plot:
        fig, ax = plt.subplots(figsize=(10,6))
        series.plot(ax=ax, label='Observed', color='blue')
        forecast_index = pd.date_range(start=series.index[-1], periods=forecast_steps+1, freq=pd.infer_freq(series.index))[1:]
        forecast.index = forecast_index
        forecast.plot(ax=ax, label='Forecast', color='red', linestyle='--')
        ax.set_title(f"ARIMA({p},{d},{q}) Forecast")
        ax.set_ylabel(series.name if series.name else "Value")
        ax.legend()
        plt.tight_layout()
        plt.show()

    return results


####
###auto arima

def auto_arima_forecast(series, p_range=(0, 3), d_range=(0, 2), q_range=(0, 3),
                         forecast_steps=5, ic='aic', plot=True, verbose=True,
                         autoreject=True):
    """
    Automatically select the best ARIMA model based on AIC or BIC,
    with optional autoreject of unstable models, and forecast future periods.

    Args:
        series (pandas.Series): The time series to model.
        p_range (tuple): Range of p values to try (min, max inclusive).
        d_range (tuple): Range of d values to try (min, max inclusive).
        q_range (tuple): Range of q values to try (min, max inclusive).
        forecast_steps (int): How many periods ahead to forecast.
        ic (str): Information criterion to minimize ('aic' or 'bic').
        plot (bool): Whether to plot actual + forecasted data.
        verbose (bool): Whether to print model fit summary.
        autoreject (bool): Whether to reject unstable models automatically.

    Returns:
        dict: Results including best model, best order, forecast, AIC, BIC.
    """
    series = series.dropna()

    best_score = float('inf')
    best_order = None
    best_model_fit = None

    # Grid search over p,d,q
    for p, d, q in itertools.product(range(p_range[0], p_range[1]+1),
                                      range(d_range[0], d_range[1]+1),
                                      range(q_range[0], q_range[1]+1)):
        try:
            model = ARIMA(series, order=(p, d, q))
            model_fit = model.fit()

            score = model_fit.aic if ic == 'aic' else model_fit.bic

            # --- Stability checks ---
            unstable = False
            if autoreject:
                params = model_fit.params

                # Check AR coefficients
                ar_params = [v for k, v in params.items() if 'ar.' in k]
                ma_params = [v for k, v in params.items() if 'ma.' in k]

                if any(abs(coeff) >= 0.99 for coeff in ar_params):
                    unstable = True
                if any(abs(coeff) >= 0.99 for coeff in ma_params):
                    unstable = True

                # Check if covariance matrix is singular
                try:
                    cond_number = np.linalg.cond(model_fit.cov_params())
                    if cond_number > 1e12:  # Very large condition number = singular matrix
                        unstable = True
                except Exception:
                    unstable = True  # If can't compute covariance, treat as unstable

            if unstable:
                if verbose:
                    print(f" Rejected ARIMA({p},{d},{q}) due to instability.")
                continue

            # --- Accept model ---
            if score < best_score:
                best_score = score
                best_order = (p, d, q)
                best_model_fit = model_fit

            if verbose:
                print(f" Accepted ARIMA({p},{d},{q}) - {ic.upper()}: {score:.2f}")

        except Exception as e:
            if verbose:
                print(f"ARIMA({p},{d},{q}) failed: {e}")
            continue

    # Forecast future periods
    forecast = best_model_fit.forecast(steps=forecast_steps)

    results = {
        'best_model_fit': best_model_fit,
        'best_order': best_order,
        'forecast': forecast,
        'aic': best_model_fit.aic,
        'bic': best_model_fit.bic
    }

    if verbose:
        print(f"\n Best ARIMA{best_order} selected based on {ic.upper()}.")
        print(best_model_fit.summary())

    if plot:
        fig, ax = plt.subplots(figsize=(10,6))
        series.plot(ax=ax, label='Observed', color='blue')

        forecast_index = pd.date_range(start=series.index[-1], periods=forecast_steps+1, freq=pd.infer_freq(series.index))[1:]
        forecast.index = forecast_index

        forecast.plot(ax=ax, label='Forecast', color='red', linestyle='--')

        ax.set_title(f"Auto-ARIMA{best_order} Forecast")
        ax.set_ylabel(series.name if series.name else "Value")
        ax.legend()
        plt.tight_layout()
        plt.show()

    return results

# ----------------------------------
# SARIMA Models
# ----------------------------------
def sarima_forecast(series, order=(1,1,1), seasonal_order=(0,0,0,0),
                    forecast_steps=5, freq=None, plot=True, verbose=True):
    """
    Fit a SARIMA model and forecast future periods.

    Args:
        series (pandas.Series): Time series data.
        order (tuple): (p,d,q) for ARIMA part.
        seasonal_order (tuple): (P,D,Q,s) for seasonal part.
        forecast_steps (int): How many periods ahead to forecast.
        freq (str, optional): Frequency string ('M', 'Q', 'W', 'D', etc.). If None, tries to infer from series.
        plot (bool): Whether to plot actual + forecasted data.
        verbose (bool): Whether to print model fit summary.

    Returns:
        dict: Results including model fit, forecast, AIC, BIC.
    """
    series = series.dropna()

    # Fit SARIMA
    model = SARIMAX(series, order=order, seasonal_order=seasonal_order,
                    enforce_stationarity=False, enforce_invertibility=False)
    model_fit = model.fit()

    # Forecast future
    forecast = model_fit.forecast(steps=forecast_steps)

    results = {
        'model_fit': model_fit,
        'forecast': forecast,
        'aic': model_fit.aic,
        'bic': model_fit.bic
    }

    if verbose:
        print(f"\n SARIMA{order}x{seasonal_order} Fit Summary:")
        print(model_fit.summary())

    if plot:
        fig, ax = plt.subplots(figsize=(10,6))
        series.plot(ax=ax, label='Observed', color='blue')

        # Determine correct forecast index
        if freq is None:
            freq_used = pd.infer_freq(series.index)
        else:
            freq_used = freq

        forecast_index = pd.date_range(start=series.index[-1], periods=forecast_steps+1, freq=freq_used)[1:]
        forecast.index = forecast_index

        forecast.plot(ax=ax, label='Forecast', color='red', linestyle='--')

        ax.set_title(f"SARIMA{order}x{seasonal_order} Forecast")
        ax.set_ylabel(series.name if series.name else "Value")
        ax.legend()
        plt.tight_layout()
        plt.show()

    return results


##### SARIMA Auto

def auto_sarima_forecast(series, 
                         p_range=(0, 2), d_range=(0, 1), q_range=(0, 2),
                         P_range=(0, 1), D_range=(0, 1), Q_range=(0, 1), s=4,
                         forecast_steps=5, freq=None,
                         ic='aic', plot=True, verbose=True,
                         autoreject=True):
    """
    Automatically select best SARIMA model based on AIC or BIC,
    and forecast future periods.

    Args:
        series (pandas.Series): Time series data.
        p_range (tuple): Range for p (AR) terms.
        d_range (tuple): Range for d (differencing).
        q_range (tuple): Range for q (MA) terms.
        P_range (tuple): Range for seasonal P (SAR) terms.
        D_range (tuple): Range for seasonal D (seasonal differencing).
        Q_range (tuple): Range for seasonal Q (SMA) terms.
        s (int): Season length (e.g., 4 for quarterly, 12 for monthly).
        forecast_steps (int): Periods to forecast into future.
        freq (str, optional): Frequency string for forecast ('M', 'Q', etc.). If None, infer from series.
        ic (str): Information criterion ('aic' or 'bic') to minimize.
        plot (bool): Whether to plot actual and forecast.
        verbose (bool): Print progress.
        autoreject (bool): Reject unstable models automatically.

    Returns:
        dict: Results including best model, best order, forecast, AIC, BIC.
    """
    series = series.dropna()

    best_score = float('inf')
    best_order = None
    best_seasonal_order = None
    best_model_fit = None

    # Grid search over p,d,q and P,D,Q
    for p, d, q, P, D, Q in itertools.product(
            range(p_range[0], p_range[1]+1),
            range(d_range[0], d_range[1]+1),
            range(q_range[0], q_range[1]+1),
            range(P_range[0], P_range[1]+1),
            range(D_range[0], D_range[1]+1),
            range(Q_range[0], Q_range[1]+1)):

        try:
            model = SARIMAX(series,
                            order=(p,d,q),
                            seasonal_order=(P,D,Q,s),
                            enforce_stationarity=False,
                            enforce_invertibility=False)
            model_fit = model.fit(disp=False)

            score = model_fit.aic if ic == 'aic' else model_fit.bic

            # Stability checks
            unstable = False
            if autoreject:
                params = model_fit.params
                ar_params = [v for k, v in params.items() if 'ar.' in k]
                ma_params = [v for k, v in params.items() if 'ma.' in k]
                sar_params = [v for k, v in params.items() if 'seasonal_ar.' in k]
                sma_params = [v for k, v in params.items() if 'seasonal_ma.' in k]

                if any(abs(coeff) >= 0.99 for coeff in ar_params + ma_params + sar_params + sma_params):
                    unstable = True

                try:
                    cond_number = np.linalg.cond(model_fit.cov_params())
                    if cond_number > 1e12:
                        unstable = True
                except Exception:
                    unstable = True

            if unstable:
                if verbose:
                    print(f" Rejected SARIMA({p},{d},{q})x({P},{D},{Q},{s}) due to instability.")
                continue

            if score < best_score:
                best_score = score
                best_order = (p,d,q)
                best_seasonal_order = (P,D,Q,s)
                best_model_fit = model_fit

            if verbose:
                print(f" Accepted SARIMA({p},{d},{q})x({P},{D},{Q},{s}) - {ic.upper()}: {score:.2f}")

        except Exception as e:
            if verbose:
                print(f"SARIMA({p},{d},{q})x({P},{D},{Q},{s}) failed: {e}")
            continue

    # Forecast future
    forecast = best_model_fit.forecast(steps=forecast_steps)

    results = {
        'best_model_fit': best_model_fit,
        'best_order': best_order,
        'best_seasonal_order': best_seasonal_order,
        'forecast': forecast,
        'aic': best_model_fit.aic,
        'bic': best_model_fit.bic
    }

    if verbose:
        print(f"\n Best SARIMA{best_order}x{best_seasonal_order} selected based on {ic.upper()}.")
        print(best_model_fit.summary())

    if plot:
        fig, ax = plt.subplots(figsize=(10,6))
        series.plot(ax=ax, label='Observed', color='blue')

        # Determine correct forecast index
        if freq is None:
            freq_used = pd.infer_freq(series.index)
        else:
            freq_used = freq

        forecast_index = pd.date_range(start=series.index[-1], periods=forecast_steps+1, freq=freq_used)[1:]
        forecast.index = forecast_index

        forecast.plot(ax=ax, label='Forecast', color='red', linestyle='--')

        ax.set_title(f"Auto-SARIMA{best_order}x{best_seasonal_order} Forecast")
        ax.set_ylabel(series.name if series.name else "Value")
        ax.legend()
        plt.tight_layout()
        plt.show()

    return results
