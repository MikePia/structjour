"""
Import this file before running anything. It tests that setting has the db and directory locations.
If not, it will fire up the file settings dialog.
"""
import os
import datetime as dt
from PyQt5.QtCore import QSettings
settings = QSettings('zero_substance', 'structjour')

from structjour.utilities.util import autoGenCreateDirs


def setDefaultChartSettings():
    chartSet = QSettings('zero_substance/chart', 'structjour')
    keys = {
        'chart3vwapcolor': 'violet',
        'chart3vwap': 'true',
        'chart3ma4color': 'green',
        'chart3ma4spin': 200,
        'chart3ma4': 'true',
        'chart3ma3color': 'black',
        'chart3ma3spin': 50,
        'chart3ma3': 'true',
        'chart3ma2color': 'blue',
        'chart3ma2spin': 20,
        'chart3ma2': 'true',
        'chart3ma1color': 'red',
        'chart3ma1spin': 9,
        'chart3ma1': 'true',
        'chart2vwapcolor': 'violet',
        'chart2vwap': 'true',
        'chart2ma4color': 'green',
        'chart2ma4spin': 200,
        'chart2ma4': 'spin',
        'chart2ma3color': 'black',
        'chart2ma3spin': 50,
        'chart2ma3': 'true',
        'chart2ma2color': 'blue',
        'chart2ma2spin': 20,
        'chart2ma2': 'true',
        'chart2ma1color': 'red',
        'chart2ma1spin': 9,
        'chart2ma1': 'true',
        'chart1vwapcolor': 'violet',
        'chart1vwap': 'true',
        'chart1ma4color': 'green',
        'chart1ma4spin': 200,
        'chart1ma4': 'true',
        'chart1ma3color': 'black',
        'chart1ma3spin': 50,
        'chart1ma3': 'true',
        'chart1ma2color': 'blue',
        'chart1ma2spin': 20,
        'chart1ma2': 'true',
        'chart1ma1color': 'red',
        'chart1ma1spin': 9,
        'chart1ma1': 'true',
        'showlegend': 'false',
        'afterhours': 'true',
        'interactive': 'false',
        'colordown': 'red',
        'colorup': 'green',
        'markersize': 3,
        'markeralpha': .7,
        'markeredgecolor': 'black',
        'markercolorup': 'green',
        'markercolordown': 'red',
        'gridv': 'false',
        'gridh': 'false',
        # 'chart': '',
    }
    for key in keys:
        chartSet.setValue(key, keys[key])


if not settings.value('journal') or not settings.value('tradeDb'):
    from structjour.view.filesetcontrol import FileSetCtrl
    from PyQt5 import QtWebEngineWidgets
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QCoreApplication
    import sys

    app = QApplication(sys.argv)
    w = FileSetCtrl(settings, initialize=True)
    QCoreApplication.exit(0)

    # Set outdir to todays date outdir. Generate the directories if they don't exist
    n = dt.datetime.now()
    outdir = settings.value('journal')
    outdir += n.strftime('/_%Y%m_%B/_%m%d_%A/')
    if not os.path.exists(outdir):
        autoGenCreateDirs(settings)
    
    # If the user has pre-made directories, this will only match the default directory scheme
    settings.setValue('outdir', outdir)
    setDefaultChartSettings()
    settings.setValue('scheme', '_{Year}{month}_{MONTH}/_{month}{day}_{DAY}/')
