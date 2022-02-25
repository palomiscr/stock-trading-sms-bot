STOCK_NAME = "TSLA"
COMPANY_NAME = "TESLA"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"


import requests
import os
from twilio.rest import Client

# LIST OF ENVIRONMENT VARIABLES NEEDED TO RUN THIS CODE
# API_KEY_STOCK https://www.alphavantage.co/
# API_KEY_NEWS https://newsapi.org/
#
# TWILIO https://www.twilio.com/
# TWILIO_ACCOUNT_SID
# TWILIO_AUTH_TOKEN
# TWILIO_PHONE_NUMBER
# MY_PHONE_NUMBER
#
"""
makes an API request to know the daily stock value of a company and returns the difference in percentage
between today's and yesterday's values.

Returns:
Positive value if today's stock is greater than yesterday's. Negative if not.

"""
def get_stock_difference():
    stock_parameters = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK_NAME,
        "apikey": os.environ["API_KEY_STOCK"]

    }
    response_stock = requests.get(url=STOCK_ENDPOINT, params=stock_parameters)
    response_stock.raise_for_status()
    data_s = response_stock.json()["Time Series (Daily)"]

    date_info = [value['4. close'] for (key, value) in data_s.items()]
    yesterday = float(date_info[1])
    today = float(date_info[0])
    return round((today - yesterday) * 100 / today, 2)

"""
fetches several news making an API request

Arguments:
number_of_news -- int with the number of news you want to recieve. 
                  Be careful because these will be send to your phone
                  using your twilio credit. I recommend 3 max 

Returns:
news -- python dictionary with several news
"""
def get_news(number_of_news):
    params_news = {
        "q": COMPANY_NAME,
        "apiKey": os.environ["API_KEY_NEWS"],
    }
    response = requests.get(url=NEWS_ENDPOINT, params=params_news)
    response.raise_for_status()
    return response.json()["articles"][:number_of_news]

"""
if the stock price of the company you are tracking changes more than a 5%, it sends several sms to your phone number 
containing the name of the company, the stock price variation
and one article related.

Arguments:
news -- python dictionary with several news
percentage -- variation between today's and yesterday's stock value.

"""
def send_sms(news, percentage):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)
    if percentage>0:
        symbol="🟩"
    else:
        symbol="🟥"
    for new in news:
        message = client.messages \
            .create(
            body=f"{STOCK_NAME}{symbol}{percentage}%\n\n{new['title']} \n\n{new['description']}",
            from_='TWILIO_PHONE_NUMBER',
            to='MY_PHONE_NUMBER'
        )

    print(message.sid)

stock_difference=get_stock_difference()
news = get_news(3)

send_sms(news, stock_difference)

