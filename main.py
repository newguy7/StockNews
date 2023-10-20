import os
import requests
import datetime as dt

from dotenv import load_dotenv
from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient

load_dotenv()

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

API_KEY = os.environ.get('STOCK_API_KEY')
API_KEY_NEWS = os.environ.get('NEWS_API_KEY')

account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
my_number = os.environ.get('TWILIO_NUMBER')
to_number = os.environ.get('TO_NUMBER')

current_time = dt.datetime.now().strftime('%Y-%m-%d')


start_date = dt.datetime.now() - dt.timedelta(days=1)
data_start_date = start_date.strftime('%Y-%m-%d')

previous_date = dt.datetime.now() - dt.timedelta(days=2)
data_previous_date = previous_date.strftime('%Y-%m-%d')

print(data_start_date)
print(data_previous_date)


base_url = "https://www.alphavantage.co/query"
news_base_url = "https://newsapi.org/v2/everything?"

parameters = {
    'function' : 'TIME_SERIES_DAILY',
    'symbol' : STOCK,
    'apikey' : API_KEY
}


# Record the STOCK price increase/decreases by 5% between yesterday and the day before yesterday

response = requests.get(url=base_url, params=parameters)
response.raise_for_status()

daily_data = response.json()["Time Series (Daily)"]
#print(daily_data)

stock_price_today = float(daily_data[data_start_date]['4. close'])
stock_price_yesterday = float(daily_data[data_previous_date]['4. close'])

change_in_stock_price = (stock_price_today - stock_price_yesterday)/stock_price_today
percentage_change = round(change_in_stock_price * 100,2)


# get the first 3 news pieces for the COMPANY_NAME. 

news_parameters = {
    'qInTitle' : COMPANY_NAME,
    'apiKey' : API_KEY_NEWS
}

news_response = requests.get(url=news_base_url, params=news_parameters)
news_response.raise_for_status()

news_data = news_response.json()['articles']

# Send a seperate message with the percentage change and each article's title and description to your phone number. 
message = ""

for news in range(3):
    news_title = news_data[news]['title']
    news_content = news_data[news]['description']
    if percentage_change < 0:
        message = f"{STOCK}:🔻{percentage_change}%\nHeadline: {news_title}.\nBrief: {news_content}"
    elif percentage_change > 0:    
        message = f"{STOCK}:🔺{percentage_change}%\nHeadline: {news_title}.\nBrief: {news_content}"
    else:
        message = f"{STOCK}: {percentage_change}\nHeadline: {news_title}.\nBrief: {news_content}"
    # proxy_client = TwilioHttpClient()
    # proxy_client.session.proxies = {'https': os.environ['https_proxy']}
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_=my_number,
        to=to_number
    )
print(message.status)    
 

