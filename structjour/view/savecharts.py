# Structjour -- a daily trade review helper
# Copyright (C) 2019 Zero Substance Trading
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
'''
Created on Apr 1, 2019

@author: Mike Petersen
'''
import os
from structjour.stock.graphstuff import FinPlot

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

