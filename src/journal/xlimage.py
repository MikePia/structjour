'''
Created on Oct 16, 2018

@author: Mike Petersen
'''
import os
import unittest

from PIL import Image as PILImage
from PIL import ImageGrab
from openpyxl.drawing.image import Image
# pylint: disable=C0103

def askUser(question):
    '''
    Ask the user a question. Placed in a function to facilitate automating it.
    :return: The response
    '''
    response = input(question)
    return response

class XLImage(object):
    '''Handle image stuff'''

#     20.238095238095237
    def __init__(self, default='data/defaultImage.png', heightInCells=20, pixPerCell=19.3):
        '''
        Create the XLImage, set the name and the size image here.
        :params default: Location of a default image to use
        :params heightInCells: Determine the height based on how many excel rows for the height.
        :params pixPerCell: The aproximate number of pixels per excel row.  Because this is
                            determined by issues beyond our control, it will (eventually) be
                            configurable in user settings. The number of pixels is unscientifically
                            determined (by me) to be about 19.3.

        '''
        self.defaultImage = default
        self.numCells = heightInCells
        self.pixPerCell = pixPerCell


    def adjustSizeByHeight(self, sz):
        ''' 
        Adjust size to keep the aspect ratio the same as determined by self.numCells and 
        self.pixPerCell
        '''
        #TODO Make some contraption to adjust the size by the user. 
        w, h = sz

        newHeight = self.numCells * self.pixPerCell
        newWidth = newHeight * w/h
        nw = int(newWidth)
        nh = int(newHeight)
        return(nw, nh)    

    def getDefaultPILImage(self):
        '''Return a default image'''
        im = PILImage.open(self.defaultImage)
        return im

    def getPilImageFromClipboard(self, msg):
        '''
        Retrieve the image from the clipboard. Ask the user if the image is ready and collect the response
        Use the PIL library to get an image from the clipboard. The ImageGrab.grabclibboard() works on
        Windows and MAC only. On failure to get an image, give the user 4 more tries or the user can opt out by
        entering 'q'.
        :param:msg: This is communication to the user of what to copy into the clipboard. It should be something
                    'Copy the chart for MU long at 9:35 for 2 minutes.
        :return:     The image in as a PIL object or None
        '''

        for i in range(5):
            msg_go = "{0} {1}".format(msg, "Are you ready? (n to skip image) \n\t\t\t\t")
            response = askUser(msg_go)
            im = None
            if response.lower().startswith('y') or response == '':
                im = ImageGrab.grabclipboard()
            elif response.lower().startswith('q') or response.lower().startswith('n'):
                # return self.getDefaultPILImage()
                return None
            elif response.lower().startswith('d'):
                return self.getDefaultPILImage()

            if im is None:
                print("Failed to get an image. Please select and copy an image (or press 'q')")
            else:
                return im
        print("Moving on")
        return self.getDefaultPILImage()

    def getAndResizeImage (self, name, outdir) :
        '''
        Tell the user to copy an image to the clipboard then call getPilImageFromClipboard. A
        script to run the image manipulation in structjour. Save it with a new name. Return the
        name. 
        :params name: The name to save the image.
        :param outdir: The location to save the images.
        :return: The pathname of the image we save.
        '''

        try:
            if not os.path.exists(outdir):
                os.mkdir(outdir)
            msg = '''
            Copy an image to the clipboard using snip for {0}
            '''.format(name)

            pilImage = self.getPilImageFromClipboard(msg)
            if not pilImage:
                return None
            newSize = self.adjustSizeByHeight(pilImage.size)
            pilImage = pilImage.resize(newSize, PILImage.ANTIALIAS)

            resizeName, ext = self.getResizeName(name, outdir)
            # TODO handle permission denied error (if the file is open)
            pilImage.save(resizeName, ext)
            img = Image(resizeName)

        except IOError as e :
            print("An exception occured '%s'" % e)
            if img :
                return img
            return None

        return img    

    def getResizeName(self, orig, outdir) :
        '''
        Do minimal checking that it has some extension. Using openpyxl and PIL, they may have more
        stringent requirements. PIL, for example, fails if you try to save with the extension .jpg.
        But its perfectly happy with .jpeg
        :param orig: The original pathfile name.
        :outdir outdir: The location to save to.
        :return: A tuple (newFileName, extension)
        '''

        orig = orig.replace(":", "-")
        x = os.path.splitext(orig)
        if len(x[1]) < 4:
            print("please provide an image name with an image extension in its name. e.g 'png'")
        newName = x[0]
        if 'jpg' in x[1].lower():
            newName += '.jpeg'
        else :
            newName += x[1]
        newName = os.path.join(os.path.normpath(outdir), newName)
        return (newName, os.path.splitext(newName)[1][1:])
