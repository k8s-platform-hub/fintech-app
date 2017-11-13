#!/usr/local/bin/python
from bs4 import BeautifulSoup
import requests
import lxml
import json
import math

print("Starting script")
stock_data = {}
financial_data = {}
project_url = "https://data.<YOUR-HASURA-PROJECT-NAME>.hasura-app.io/"

# Keep your token secret
headers = {"Content-Type":"application/json", "Authorization":"Bearer <YOUR-ADMIN-TOKEN-HERE>"}

# First get the Balance sheet and profit/loss urls for each company
def fetch_urls():

    url = "http://www.moneycontrol.com/stocks/marketinfo/marketcap/nse/index.html"
    page = requests.get(url).text

    soup = BeautifulSoup(page, 'lxml')

    table = soup.find('table', class_="tbldata14")
    urls = []

    for tr in table.findAll('tr')[1:]:
        companyUrl = tr.find('a', class_='bl_12', href=True)['href']
        # Link for company main page found
        urls.append(companyUrl)

    # Moving this out so that it can be done after compiling all the urls
    for url in urls:

        # Now get balance sheet and profit/loss data for company
        extract_bl_pl_data(url)

# Get bl pl urls and extract data

def extract_bl_pl_data(companyUrl):

    url = "http://www.moneycontrol.com" + companyUrl

    page = requests.get(url).text
    soup = BeautifulSoup(page, 'lxml')

    blsUrl = soup.find('a', text='Balance Sheet', href=True)['href']
    plUrl = soup.find('a', text='Profit & Loss', href=True)['href']

    # Ensure stock_data and financial_data are null
    global stock_data
    global financial_data
    stock_data = {}
    financial_data = {}

    # First we get stock name etc
    base_div = soup.find('div', {"id":"nChrtPrc"})

    stock_name = base_div.find('h1').text
    print("================================")
    stock_data['stock_name'] = stock_name
    print("Company: " + stock_data['stock_name'])
    sector_name = soup.findAll('a', class_='gD_10')[3].text
    stock_data['sector_name'] = sector_name
    print("Sector: " + stock_data['sector_name'])
    # print("Stock data: " + str(stock_data))

    # Now we get actual data from the balance sheet
    extract_bl_data(blsUrl)

    # Extract Profit & Loss data
    extract_pl_data(plUrl)

    # Now calculate economic profit and insert the data into the db
    # print("Stock data: " + str(stock_data))
    insert_data()

# Get balance sheet data

def extract_bl_data(blsUrl):

    url = "http://www.moneycontrol.com" + blsUrl

    print("Extracting Balance Sheet from " + url)

    page = requests.get(url).text
    soup = BeautifulSoup(page, 'lxml')

    base_div = soup.find('div', class_='boxBg1')
    table = base_div.findAll('table')[2]

    years = []
    trs = table.findAll('tr')[0]
    for td in trs.findAll('td')[1:]:
        years.append(int(td.text[-2:]) + 2000)
        # These are all the years for which data is available

    # Better split this up into a separate function.
    try:
        get_td_value('Total Current Assets','total_net_current_assets', years, table)
        get_td_value('Total Non-Current Assets','net_block', years, table)
    except Exception as e:
        try:
            get_td_value('Total Assets','invested_capital', years, table)
        except Exception as e:
            print("Error: " + str(e))
            pass

        print("Error: " + str(e))
        pass



    print("--- Finished extracting balance sheet data")


# Get value from table
def get_td_value(name,column, years, table):
    try:
        all_data = table.find('td', text=name).find_next_siblings()

        index = 0

        for year in years:
            current_data = all_data[index]

            if year in financial_data:
                financial_data[year][column] = float((current_data.text).replace(',',''))
            else:
                financial_data[year] = {"year": year}
                financial_data[year][column] = float((current_data.text).replace(',',''))

            index = index + 1
    except Exception as e:
        print("Error: " + str(e))


# Get profit/loss data

def extract_pl_data(plUrl):
    url = "http://www.moneycontrol.com" + plUrl

    print("Extracting Profit & Loss data from " + url)

    page = requests.get(url).text
    soup = BeautifulSoup(page, 'lxml')

    base_div = soup.find('div', class_='boxBg1')
    table = base_div.findAll('table')[2]

    years = []
    trs = table.findAll('tr')[0]
    for td in trs.findAll('td')[1:]:
        years.append(int(td.text[-2:]) + 2000)
        # These are all the years for which data is available

    # Better split this up into a separate function.
    get_td_value('Total Revenue','total_revenue', years, table)
    get_td_value('Profit/Loss Before Tax','profit_before_tax', years, table)
    get_td_value('Other Income','other_income', years, table)
    get_td_value('Total Tax Expenses','total_tax', years, table)

    print("--- Finished extracting Profit & Loss data")
# Calculate economic profit

def insert_data():
    # print("Stock data: " + str(stock_data))
    # Calcluate economic profit

    for year in financial_data:

        try:
            yearly_data = financial_data[year]

            pbt = yearly_data['profit_before_tax']
            other_income = yearly_data['other_income']
            adj_ebit = pbt - other_income

            total_tax = yearly_data['total_tax']
            tax_rate = total_tax/pbt
            tax_on_other_income = tax_rate * other_income

            tax_on_adj_ebit = total_tax - tax_on_other_income

            noplat = adj_ebit - tax_on_adj_ebit
            # Cost of equity assumed as 12%
            coe = 0.12

            net_block = yearly_data['net_block']
            if net_block == None:
                invested_capital = yearly_data['invested_capital']
            else:
                total_net_current_assets = yearly_data['total_net_current_assets']
                invested_capital = net_block + total_net_current_assets

            economic_profit = noplat - (coe*invested_capital)
            economic_profit = float("{0:.5f}".format(economic_profit))
            total_revenue = yearly_data['total_revenue']
            ep_ratio = economic_profit/total_revenue;
            ep_ratio = float("{0:.5f}".format(ep_ratio))

            financial_data[year]['economic_profit'] = economic_profit
            financial_data[year]['ep_ratio'] = ep_ratio
        except Exception as e:
            print("Error: " + str(e))

    # Now insert data into the database
    data_url = project_url + "/v1/query"

    stock_query = {"type":"insert",
            "args":{
                "table":"stocks",
                "objects":[stock_data],
                "returning":["id"]
                }
            }

    # Try inserting stock info
    try:
        # print("Stock data: " + str(stock_data))
        resp = requests.post(data_url, headers=headers, data=json.dumps(stock_query), timeout=30)
        print("Response: " + str(resp.content))
        id = json.loads(resp.text)['returning'][0]['id']
    except Exception as e:
        print("Error %s" % str(e))

    # Try inserting financial data

    for obj in financial_data:
        try:
            current_data = financial_data[obj]
            current_data['stock_id'] = id
            # print("Current data " + str(current_data))
            financials_query = {"type":"insert",
                    "args":{
                        "table":"stock_financial_data",
                        "objects":[current_data]
                        }
                    }

            try:
                # print("-----  Financial Query " + str(financials_query))
                resp = requests.post(data_url, headers=headers, data=json.dumps(financials_query), timeout=30)
                print("Response: " + str(resp.content))
            except Exception as e:
                print("Error: %s" % str(e))
        except Exception as e:
            print("Error: %s" % str(e))

    print("Successfully inserted data")

def delete_all():
    data_url = project_url + "/v1/query"

    query = {"args":{
        "table": "stocks",
        "where": {}
    },
    "type": "delete"
}
    try:
        resp = requests.post(data_url, headers=headers, data=json.dumps(query))
        print("Response: " + str(resp.content))
    except Exception as e:
        print("Error: %s" % str(e))

    query_financial = {"args":{
        "table": "stock_financial_data",
        "where": {}
    },
    "type": "delete"
}

    try:
        resp = requests.post(data_url, headers=headers, data=json.dumps(query_financial))
        print("Response: " + str(resp.content))
    except Exception as e:
        print("Error: %s" % str(e))
# Now call the main fetch_urls function
delete_all()
fetch_urls()

