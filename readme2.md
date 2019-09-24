# Structjour -- Day Trade Review Journal

I am very interested in all issues. Please inform me [here. (issues on github)](https://github.com/MikePia/structjour/issues). First concerns are install and run errors, but I have used and designed this my self, there is a lack of input for everything including Usability and Design.

Structjour currently reads DAS Trader Pro export files and Interactive Broker Statements
Its pre Alpha. 

Install it in the usual python way (not on pypi yet). It will require python 3.6 or greater:
   * Download and unpack
   * Go to the directory where its unpacked and run the command:
       * 'python setup.py install'
   * ('pip install structjour' should also work from the root directory)


   

### How to run Structjour:

After installing, the program will be in your python Scripts directory. In my case it looks like the following
 
   `C:\\gs\\python\\python.exe`

   `C:\\gs\\python\\Scripts\\structjour.exe`

Start the program by typing the program name. There are several things required to initialize everything. (Alpha software)

## Initialize file settings
Go to file->file settings

![filesettings.png](images/filesettings.png)


  * Click Journal Directory and select the location to place your journal directory
  * Click on each of the next four buttons to set up defaults
  * Disciplined Trader log (Disciplined.xlsx) is located in your install directory. I recommend placing it in your Journal Directory. Then click on Discipline and navigate to the file
   * The structjour database and trades databse will be sqlite databases. They will be filenames in your system. They can be the same file if you like. Make up a name and place it in the boxes. Place them in your journal directory
   * Create Dirs will create subdirectories in your Journal Directory. 
       * Make sure you have a valid directory in the Journal Directory edit box.
       * Make sure you have a setting the the Directory Naming Scheme (press Set Default)
       * Then select the year and month and click 'Create Dirs'

## Optional setup of automatic chart generation using free data from barchart and alphavantage
   * Go to file->stock api 

![filesettings.png](images/stockapi.png)

   * Get the barchart apikey [from barchart here](https://www.barchart.com/ondemand/free-market-data-api )
      * Do the registration and copy the apikey into the box
   * Get the Alphavantage apikey [from alphavantage here.](https://www.alphavantage.co/support/#api-key) 
      * Do the registration and copy the apikey into the box
   * Select Barchart and Alphavantage boxes and place the tokens 'bc' and 'av' in the box underneath, seperated by a comma
   * Note that IEX recently outsourced their api and is currently disabled in the dialog

## Setup for Interactive Brokers TWSAPI (ibapi)
If you have an Interactive Brokers account and can receive data from them, this is the best data. It includes afterhours data, does not have a practical limit on the dates for which you can receive data, and has no limits to usage. Both Barchart and Alphavantage (free apis) have limits with only market hours, available dates and request limits.
Briefly, to us ibapi you must:
   * Download and install [TWSAPI](https://interactivebrokers.github.io/) 
      * Additionally, you may have to run 'python setup.py install' in the appropriate directory
   * While using ibapi, you must have either IB Gateway or Trader Work Staion running. IB Gateway has much less overhead. 
      * [IB Gateway install link](https://www.interactivebrokers.com/en/index.php?f=16457)
      * Configure Ib Gateway. Go to Configure->settings->api->settings
      * fill in (or just note the values) the the Socket port and client id
      * Place port and Client ID in the Structjour stockapi dialog -- one setting for live, one for paper
      * Click on Interactive Brokers (live) or IBPaper account

## How to open your trades in Structjour from DAS Trader Pro
   * Export your trades window from DAS Trader Pro into the folder for the correct date underneath your Journal Dir. 
      * Name the file trades.csv (the default name you selected earlier)
      * Be sure to include the following columns [time, symb, side, price, qty, account, cloid, P / L] 
   * Export your positions window that includes open shares. 
      * Name the file positions.csv
   * In Structjour, select 'DAS import' and the date. The file name should appear in green font indicating it exists.
   * Click Read File,   
      * Add your reviews and charts for each trade. Navigate trades using the combo box.
          * Click update to generate a chart. Right click to copy or browse for a chart.
          * Export to excel if you like. The file will be dated subdirectory/out
          * Export to Disciplined.xlsx if you like. file->Export TradeLog (Open the file and initialize the account number and balance first)

      * Click Save User Data to store your reviews etc in the database (You may have to click it twice.)
