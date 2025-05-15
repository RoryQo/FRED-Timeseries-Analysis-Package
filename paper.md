---
title: 'FRED Timeseries Toolkit: Automating Economic Time Series Analysis and Forecasting in Python'
tags:
  - Python 
  - Time Series
  - Market Research
  - Economics
  - Forecasting
  - FRED
authors:
  - name: Rory G. Quinlan
    orcid: 0009-0006-7483-6769
    equal-contrib: true
    affiliation: "1"
affiliations:
  - name: University of Pittsburgh
    index: 1
    ror: 00hx57361
date: 03 May 2025
bibliography: paper.bib
nocite: |
  @*
---

# Summary

Economic time series analysis is fundamental for macroeconomic modeling, forecasting, and policy evaluation. Publicly accessible sources like the Federal Reserve Economic Data (FRED) provide a wealth of economic indicators; however, efficiently downloading, preparing, and modeling this data often requires extensive setup. The FRED Timeseries Analysis Package offers a Python-based toolkit that streamlines these tasks by automating data fetching from the FRED API, testing stationarity, and fitting ARIMA and SARIMA forecasting models with minimal code overhead. The package emphasizes model stability, automatic selection procedures, and Jupyter-optimized outputs, making it especially suited for rapid exploration and production-quality time series modeling.

# Statement of need

There are currently few lightweight packages that tightly integrate economic time series acquisition with modern Python modeling workflows. Existing general libraries such as statsmodels provide time series modeling utilities, but users must separately source, clean, and align economic datasets before beginning analysis. The FRED Timeseries Analysis Package addresses this gap by providing an integrated framework that connects directly to FRED, simplifies stationarity testing via Augmented Dickey-Fuller methods, and offers fast ARIMA and SARIMA modeling with sensible defaults. This combination enables reproducible, end-to-end forecasting pipelines without requiring custom setup scripts for every new project. The package is intended for economists, financial analysts, data scientists, and policy researchers who need fast and reproducible economic forecasts.

# Acknowledgments

This project was completed during master's degree studies at the University of Pittsburgh. We thank Editage (https://editage.com) for English language editing support and acknowledge the university faculty for their support and instruction throughout the program.

\clearpage

# References
::: {#refs}
:::

