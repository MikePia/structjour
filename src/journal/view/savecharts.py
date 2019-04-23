import os
from journal.stock.graphstuff import FinPlot

class SaveChart:
    def __init__(self, tname, outdir):
        self.outdir = outdir
        self.tradeName = tname
        self.chartNames = []
        self.dynamic = False
        self.start = None
        self.end = None
        self.old = []

    def saveChart(self, newName):
        if self.getChart():
            self.old.append(self.name)
        self.name = newName
        
    
    def getChart(self):
        if not self.dynamic:
            pname = os.path.join(self.outdir, self.name)
            if os.path.exists(pname):
                return pname
            else:
                return None
        else:
            return None
    
    def update(self, start, end, interval):
        self.start = start
        self.end = end

