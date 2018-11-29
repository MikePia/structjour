'''
Created on Oct 16, 2018

@author: Mike Petersen
'''
import os
from PIL import Image as PILImage
from PIL import ImageGrab
from openpyxl.drawing.image import Image
# pylint: disable=C0103

class XLImage(object):

#     20.238095238095237

    def adjustSizeByHeight(self, sz, newHeight=425, numCells=0, pixPerCell = 19.3) :
        ''' 
        Adjust size to keep the aspect ratio the same as determined by newHeight
        :param:sz: A tuple of ints in the form (width, height).
        :param:newHeight: The height in pixels of the image as place in the excel doc. The default number is
                            based on 21 unaltered excel cells on my machine.
        :param:numCells: An alternate way to determine the height based on how many excel rows for the height.
                            This value will override newHeight. The number of pixels is unscientifically determined 
                            (by me) to be about 20.24.
        :param:pixPerCell: The aproximate number of pixels per excel row.  Because this is determined by issues
                            beyond our control, it will have to be configurable in user settings     
        '''
        #TODO Make some contraption to adjust the size by the user. 
        w,h = sz
        if numCells > 0:
            newHeight = numCells * pixPerCell
        newWidth = newHeight * w/h
        nw=int(newWidth)
        nh=int(newHeight)
        return(nw, nh)    

    def getDefaultPILImage(self):
        im = PILImage.open("data/defaultImage.png")
        return im

    def getPilImageFromClipboard(self, msg):
        '''
        Ask the user if the image is ready and collect the response
        Use the PIL library to get an image from the clipboard. The ImageGrab.grabclibboard() works on
        Windows and MAC only. On failure to get an image, give the user 4 more tries or the user can opt out by
        entering 'q'.
        :param:msg: This is communication to the user of what to copy into the clipboard. It should be something
                    'Copy the chart for MU long at 9:35 for 2 minutes.
        :return:     The image in as a PIL object or None
        '''

        for i in range (5):
            msg_go = "{0} {1}".format(msg, "Are you ready? (q to skip image) \n\t\t\t\t")
            response = input(msg_go)
            im = None
            if response.lower().startswith('y') or response == '': 
                im = ImageGrab.grabclipboard()
            elif response.lower().startswith('q') :
                return self.getDefaultPILImage()
            if im is None :
                print("Failed to get an image. Please select and copy an image (or press 'q')")
            else :
                return im
        print("Moving on")
        return self.getDefaultPILImage()
    
    
    
    
    def getAndResizeImage (self, name, outdir) :
        '''
        A script to run the image manipulation in structjour. Request a clipboard copy of an image. 
        Resze it to newSize height. Save it with a new name. Return the name. Hackiness lives until 
        I figure how to create a proper openpyxl Image object from a PIL Image object that doesn't 
        make the Workbook puke. (Saving the image is kind of a nice touch as long as the name has
        enough information to make the file useful ... like (Trade1_TWTR-Short_930-3min.jpeg)
        :param:name: An original name. We mark it up with _resize, save it, and return the new name.
        :param:outdir: The location to save the images.
        :return: The pathname of the image we save.
        '''

        try:
            if not os.path.exists(outdir):
                os.mkdir(outdir)
            msg = '''
            Copy an image to the clipboard using snip for {0}
            '''.format(name)
            pilImage = self.getPilImageFromClipboard(msg)
            newSize = self.adjustSizeByHeight(pilImage.size, numCells=20)
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
        Munge up a pathfile name by inserting _resize onto the name. Do minimal checking that it has some extension.
        Using openpyxl and PIL, they may have more stringent requirements. PIL, for example, fails if you try to save with 
        the extension .jpg. But its perfectly happy with .jpeg
        :param:orig: The original pathfile name.
        :outdir:outdir: The location to save to.
        :return: A tuple(newFileName, extension)
        '''

        orig = orig.replace(":", "-")
        x = os.path.splitext(orig)
        if (len(x[1]) < 4 ):
            print("please provide an image name with an image extension in its name. e.g 'png', jpg', etc")
        newName = x[0] + '_resize'
        if 'jpg' in x[1].lower() :
            newName += '.jpeg'
        else :
            newName += x[1]
        newName = os.path.join(os.path.normpath(outdir), newName)
        return (newName, os.path.splitext(newName)[1][1:])
