import os
import requests
import schedule
import time
from bs4 import BeautifulSoup
import pandas as pd
import urllib.parse
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
current_dir = os.path.abspath(os.path.dirname(__file__))

#Insert target stocks here
target_stocks = ["Tesla", "Adani Enterprises", "Microsoft", "T Mobile", "NVIDIA", "LIC Housing", "Gamestop"] 

# Get most recent data from CSV file
def get_data(stock_name):
    file_name = f"{stock_name}_historical_data.csv"
    filepath = os.path.join(current_dir, file_name)
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        return df
    else:
        return pd.DataFrame()

# Get company URL 
def search_company(company_name):
    search_url = "https://www.investing.com/search/?q=" + urllib.parse.quote(company_name)
    page = requests.get(search_url)
    soup = BeautifulSoup(page.text, 'lxml')
    
    result = soup.find('a', {'href': True, 'class': 'js-inner-all-results-quote-item row'})
    if result:
        link = "https://www.investing.com" + result['href']
        return link
    else:
        print(f"Hyperlink not found for {company_name}.")
        return None

#Get today's data and make a new / append it to CSV file
def scrape_daily_data(stock_url, stock_name):
    if stock_url is None:
        return Exception("No main page URL")
    
    page = requests.get(stock_url)
    soup = BeautifulSoup(page.text, 'lxml')

    try:
        company = soup.find('h1', {'class': "mb-2.5 text-left text-xl font-bold leading-7 text-[#232526] md:mb-2 md:text-3xl md:leading-8 rtl:soft-ltr"}).text.strip() 
        table_data_today = soup.find_all('span', {'class' : 'key-info_dd-numeric__ZQFIs'})
        for i in range(4):
            table_data_today[i] = float(table_data_today[i].text.replace(",",""))
        closing_price = table_data_today[0]
        open_price = table_data_today[1]
        high_price = table_data_today[3]
        low_price = table_data_today[2]
        change_percent = ((soup.find("span", {"data-test" : "instrument-price-change-percent"}).text).replace(")","")).replace("(","")
    except Exception:
        print(f"Error scraping data for {stock_name}")
    date = datetime.now().strftime("%Y-%m-%d")

    new_data = {
        'Date': [date],
        'Price': [closing_price],
        'Open': [open_price],
        'High': [high_price],
        'Low': [low_price],
        'Change %': [change_percent]
    }

    df_new = pd.DataFrame(new_data)

    file_name = f"{stock_name}_historical_data.csv"
    filepath = os.path.join(current_dir, file_name)
    if os.path.exists(filepath):
        df_existing = pd.read_csv(filepath)
        if date in df_existing['Date'].values:
            df_existing.loc[df_existing['Date'] == date, ['Price', 'Open', 'High', 'Low','Change %']] = closing_price, open_price, high_price, low_price, change_percent
        else:
            df_existing = pd.concat([df_new, df_existing]).reset_index(drop=True)
    else:
        df_existing = df_new

    df_existing.to_csv(filepath, index=False)
    return df_existing


# Get previous 1 month data and make new CSV file
def scrape_historical_data(stock_url, stock_name):
    if stock_url is None:
        return Exception("No main page URL")
    
    file_name = f"{stock_name}_historical_data.csv"
    filepath = os.path.join(current_dir, file_name)

    historical_url = stock_url + "-historical-data"
    page = requests.get(historical_url)
    soup = BeautifulSoup(page.text, 'lxml')

    table = soup.find("table", {'class' : "freeze-column-w-1 w-full overflow-x-auto text-xs leading-4"})
    headers = [header.text for header in table.find("thead").find_all("th")]
    for i in range(len(headers)):
        headers[i] = headers[i].strip()
    rows = table.find("tbody").find_all("tr")
    data_table = []
    for row in rows:
        cols = row.find_all('td')
        for i in range(len(cols)):
            cols[i] = cols[i].text.strip()
        data_table.append(cols)
    
    df = pd.DataFrame(data_table, columns=headers)
    df['Date'] = pd.to_datetime(df['Date'])
    df.to_csv(filepath, index = False)
    df['Price'] = df['Price'].str.replace(',', '').astype(float)
    return df 

# INDICATORS
# 1. Moving Average Calculation and Plotting
def calculate_moving_average(df, stock_name, window):
    if df is None:
        print("No dataframe to calculate moving average")
        return df
    
    df['Moving Average'] = df['Price'].rolling(window=window).mean()
    return df

def plot_moving_average(df, stock_name, window):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['Price'], label='Closing Price')
    plt.plot(df['Date'], df['Moving Average'], label=f'{window}-Day Moving Average', color='orange')
    plt.title(f'{window}-Day Moving Average for {stock_name}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.show()

# 2. Relative Strength Index Calculation and Plotting
def calculate_rsi(df, window): # Calculate RSI 
    delta = df["Price"].diff()
    gains = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    losses = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    df["RSI"] = 100*(1 - ((1+(gains/losses))**(-1)))
    return df

def plot_rsi(df, stock_name):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['RSI'], color='purple', label='RSI')
    plt.axhline(70, color='red', linestyle='--')
    plt.axhline(30, color='green', linestyle='--')
    plt.title(f'RSI for {stock_name}')
    plt.xlabel('Date')
    plt.ylabel('RSI')
    plt.legend()
    plt.grid(True)
    plt.show()

# 3. Bollinger Bands Calculation and Plotting
def calculate_bollinger(df,  window): # Calculate Bollinger Bands and Middle Band
    df['Middle Band']= df['Price'].rolling(window=window).mean()
    df['Lower Band'] = df["Middle Band"] - (2 * df["Price"].rolling(window=window).std())
    df["Upper Band"] = df["Middle Band"] + (2 * df["Price"].rolling(window=window).std())
    return df

def plot_bollinger(df, stock_name):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['Price'], color='blue', label='Closing Price')
    plt.plot(df['Date'], df['Middle Band'], color='black', label='Middle Band')
    plt.plot(df['Date'], df['Upper Band'], color='red', label='Upper Band')
    plt.plot(df['Date'], df['Lower Band'], color='green', label='Lower Band')
    plt.title(f'Bollinger Bands for {stock_name}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.show()

# 4. MACD Calculation and Plotting
def calculate_macd(df, short_window=12, long_window=26, signal_window=9):
    df['Short EMA'] = df['Price'].ewm(span=short_window, adjust=False).mean()
    df['Long EMA'] = df['Price'].ewm(span=long_window, adjust=False).mean()
    df['MACD'] = df['Short EMA'] - df['Long EMA']
    df['Signal Line'] = df['MACD'].ewm(span=signal_window, adjust=False).mean()
    df['MACD Histogram'] = df['MACD'] - df['Signal Line']
    return df

def plot_macd(df, stock_name):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['MACD'], label='MACD', color='blue')
    plt.plot(df['Date'], df['Signal Line'], label='Signal Line', color='orange')
    plt.bar(df['Date'], df['MACD Histogram'], label='MACD Histogram', color='gray')
    plt.title(f'MACD for {stock_name}')
    plt.xlabel('Date')
    plt.ylabel('MACD Value')
    plt.legend()
    plt.grid(True)
    plt.show()


# Preview and Running settings
def update_and_analyze_stock(stock_name):
    stock_url = search_company(stock_name)
    df_updated = scrape_daily_data(stock_url, stock_name)
    if historical_data is not None:
        df_updated = calculate_moving_average(df_updated, stock_name)
        df_updated = calculate_rsi(df_updated)
        df_updated = calculate_bollinger(df_updated)
        df_updated = calculate_macd(df_updated)
        plot_moving_average(df_updated, stock_name)
        plot_rsi(df_updated, stock_name)
        plot_bollinger(df_updated, stock_name)
        plot_macd(df_updated)

def run_scraper(target_stocks):
    for stock in target_stocks:
        stock_url = search_company(stock)
        scrape_historical_data(stock_url, stock)

    schedule.every().day.at("17:00").do(lambda: [update_and_analyze_stock(stock) for stock in target_stocks])

if __name__ == "__main__":
    run_scraper(target_stocks=target_stocks)
