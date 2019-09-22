import setuptools

with open('readme.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='structjour',
    version='0.9.6-Alpha+000',
    author='Mike Petersen',
    author_email='pentsok@zerosubstance.org',
    description='A structured daily journal for day traders.',
    license='GPL',
    long_description=long_description,
    url='https://github.com/MikePia/structjour',
    packages=setuptools.find_packages(exclude=['tests']),
    keywords='DayTrading journal',
    classifiers=[
        'Development Status :: - Alpha',
        'Intended Audience :: Day Traders'
        'Programming Language :: Python :: 3',
        'License :: GNU GPL Version 3',
        'Operating System :: Windows',
    ],
    install_requires=[
        'numpy>=1.16.0',
        'pandas>=0.24.0',
        'seaborn>=0.9.0',
        'PyQt5>=5.13.0',
        'PyQtWebEngine>=5.12.1',
        'openpyxl==2.5.14',
        'beautifulsoup4>=4.7.1',
        'mpl-finance==0.10.0'
    ],
    data_files=[('images', [
        'images/ZeroSubstanceCreation_220.png',
        'images/ZeroSubstanceCreation_500x334.png',
        'images/ZeroSubstanceCreation.png',
        'images/ZSLogo.png'
    ]), ('data', [
        'data/ActivityStatement.20190313_PL.html',
        'data/ActivityStatement.20190404.html',
        'data/Disciplined.xlsx',
        'data/FLIPPED.xlsx',
        'data/licBlib.txt',
        'data/MarketHolidays.xlsx',
        'data/positions.csv',
        'data/testdata.xlsx',
        'data/trades.1116_messedUpTradeSummary10.csv',
        'data/trades.1116_messedUpTradeSummary10_messin.csv',
        'data/trades.8.csv',
        'data/trades.8.ExcelEdited.csv',
        'data/trades.8.WithBothHolds.csv',
        'data/trades.8.WithBothHolds_messin.xlsx',
        'data/trades.8.WithHolds.csv',
        'data/trades.8.WithHolds_messin.csv',
        'data/trades.8_messin.csv',
        'data/trades.8_messin.xlsx',
        'data/trades.907.WithChangingHolds.csv',
        'data/trades.910.tickets.csv',
        'data/trades.911.noPL.csv',
        'data/trades.csv',
        'data/trades1105HoldShortEnd.csv',
        'data/trades190221.BHoldPreExit.csv',
        'data/tradesByTicket.csv',
        'data/tradeStyle.xlsx',
        'data/tradeStyleTrades_Friday_1005.xlsx',
        'data/trades_190117_HoldError.csv',
        'data/trades_190130.csv',
        'data/trades_20190313_PL.csv',
        'data/Trades_Monday_1119.xlsx',
        'data/Trades_Tuesday_1106.PL_SUMMARY_FORM.xlsx',
        'data/trades_tuesday_1121_DivBy0_bug.csv',
        'data/U2429974_20190313_20190313_PL.csv'
        ]
        
        
        )],
    entry_points={'console_scripts': 'structjour=structjour.view.runtrade:main'},
    python_requires='>=3.6'
)


# figure out:
# entry_points
# package_data
# data_files
# extras_require
# and how to include IBAPI  optional