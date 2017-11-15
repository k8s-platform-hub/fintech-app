# Fintech Application with Hasura

This is a simple chartjs based application made using nodeJS and deployed on Hasura. This app generates charts of economic profit calculated based on data scraped from [www.moneycontrol.com](www.moneycontrol.com)

This quickstart repo comes with three things:
* A sample database of scraped data
* A nodejs app that pulls data from the database and displays charts
* A python scraper script to scrape data and insert into the database

The economic profit ratio is the ratio of economic profit of the company to the total income of the company. This gives a better idea of the performance of the company relative to the market average.
The economic profit is calculated on metrics fetched from a financial statistics site. The exact calculation can be found in scraper/scraper.py.

The app then displays economic performance charts based on the scraped data separated by sector:
![Charts for a particular sector](https://github.com/hasura/fintech-app/raw/master/charts.png)

The quickstart repo comes with sample data that can be used to quickly check out the running application. To get it set up quickly, follow the steps shown below:

1.  Get the project from the hub using

```
    hasura quickstart rishi/fintech-app
```

2. Modify your cluster name in the ``microservices/fintech/src/views/index.html``

```
  hasura.setProject('controllable78'); //Set your own cluster name in place of controllable78
```

3. Run these commands from the project directory to push this service to your cluster::

```
  $ git add .
  $ git commit -m "First commit"
  $ git push hasura master
```
4. Your app will be running at https://fintech.cluster-name.hasura-app.io

