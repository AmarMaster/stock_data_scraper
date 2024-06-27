# Stock Data Scraper

## Overview

The Stock Data Scraper is an advanced Python application designed to collect, analyze, and visualize stock market data. This project leverages powerful libraries such as BeautifulSoup for web scraping, Pandas for data manipulation, and Matplotlib for generating insightful visualizations. By automating the data collection and analysis process, this tool provides valuable real-time and historical insights into stock performance.

## Features

- **Comprehensive Web Scraping:** Efficiently retrieves real-time stock data from Investing.com using the BeautifulSoup library.
- **Technical Analysis Indicators:** Integrates sophisticated technical indicators including Moving Average, Relative Strength Index (RSI), Bollinger Bands, and Moving Average Convergence Divergence (MACD) to facilitate detailed market analysis.
- **Data Management and Integrity:** Automatically updates daily stock data, ensuring high data integrity and reliability through robust error handling mechanisms.
- **Dynamic Visualizations:** Utilizes Matplotlib to create interactive and informative charts and graphs, enhancing data comprehension.
- **Automated Scheduling:** Employs the Schedule library to automate daily data scraping and analysis tasks, ensuring timely updates and continuous monitoring.

## Usage

1. Customize the target stocks by modifying the "target_stocks" list in the script.
2. Run the scraper to extract historical data through the "scrape_historical_data" method in the script.
3. Run the svraper to schedule daily updates at the time of your choice.

## Project Structure

- **scraper.py** : Main script for scraping, analysing and visualising stock data.
- **requirements.txt** : List of required python packages
- **README.md** : Project Documentation

