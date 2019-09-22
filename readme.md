# Structjour - A Structured Daily Journal for Day Traders of Stock Equities
![Image of structjour](images/structjour.png)

 The features of the program include 

Import from DAS Trader Pro or Interactive Broker Statements. If requested I plan to include other brokers' statements.

Tickets are divided into trades and displayed showing entries, exits, PnL, and the diff between initial entry and exit and some other stuff.

A place to enter your initial target and stoploss can detect when the stop is violated and figures the lost PnL. The loss amount can be edited to reflect loss of real or potential PnL due to breaking your rules. 

For your trade review, there is a strategey dropdown to choose from, a location to describe your trade, a location to analyze your trade, and a location to summarize your trade (which will be included in your daily summary).

The strategy dropdown box on the main page can add new strategies to your list. Strategies are supported by the strategy browser where you can define your strategies and check whether to include them in the dropdown box on the front page. In the Strategy browser, you can define your strategy and provide a couple images. Additionally you can add web pages that describe each strategy


Charts can be 1) automatically generated 2) copied from the clipboard or 3) loaded from a file. Data for automatic chart generation has three possible sources. Alphavantage and Barchart (free APIs) and Interactive Brokers python API using IB Gateway or Trader Work Station. If you have all three APIS setup, structjour will choose one based on availability and your set preference. The setup for Alphavantage and Barchart requires you get an API key (very simple and available to everyone). The ibapi data (setup more complicated) has the advantage of providing after hours data and long historical availability. Automatic chart generation can include Moving averages and VWAP. All charts are stored in a directory for that day providing easy access.

Input files are limited to DAS Trader PRO exports and IB statements (Activity, Trade and Flex statements). At some point in the future, other formats will be added.

Navigation between days is done with a date widget. Just Change the date and click read or load to read a new file or load saved data. 

The daily summary has a place to store notes that refer to the whole day. A summary of Wins and losses is displayed that includes the summary made for each trade.

Everything is stored in a light-weight sqlite database

The entire day can be exported to an excel file which includes a trades table, the daily summaries, easy to read forms for each trade and the charts.

All of your trades can be exported to an excel file (a tweak of 'DisciplinedTrader.xlsx) which shows monthly and yearly statistics. 

![Image of daily summary](images/dailysummary.png)

Excel export
![Image of excel](images/excel.png) 

Strategy Browser
![Image of excel](images/strategybrowser.png) 


Strategy web browser
![Image of excel](images/strategybrowserweb.png) 

Export to an excel analysis tool

![Image of excel](images/disciplined.png) 


The state of the software is pre-alpha. I created it for my own use based on what I needed. I believe the scope has grown to be more generally useful for Day-Traders of Stock Equities. 

If you are interested in contributing, I would welcome your help and input in any and all areas of design, implementation and bug reports.





