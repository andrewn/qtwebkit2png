#!/usr/bin/env python

# webkit2png - makes screenshots of webpages
# http://www.paranoidfish.org/projects/webkit2png
__version__ = "0.4"

# $Id: webkit2png-0.4 398 2004-09-24 18:40:49Z paul $

# Copyright (C) 2008 Andrew Nicolaou
# Based on webkit2png: Copyright (C) 2004 Paul Hammond
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

import sys

try:
  from PyQt4 import QtGui, QtCore, QtWebKit
except ImportError:
  print "Couldn't import PyQt4 -- do you have Qt4 and PyQt installed?"
  sys.exit()

from optparse import OptionParser

# Provides helper method for 
class WebSnapshotProcessor:
  def __init__(self, urls, options):
    self.urls   = urls
    self.options = options
    
    print "Start web view wrapper"
    self.view = WebSnapshotView()

    #print "Processing urls"
    self.processAllURLs()
    #self.processSingleURL(self.urls[0])
    
    self.view.suspendQuit()
  
  def whenLoaded(self, url, bitmapData):
    print "Loaded"
    filename = self.makeFilename(url, self.options)
    self.saveImages(bitmapData, filename, self.options)
    
    print " ... done"
    self.processAllURLs()
  
  def processSingleURL(self, url):
    self.view.getURL(url, self.whenLoaded)
  
  def processAllURLs(self):
     if self.urls:
         if self.urls[0] == '-':
             url = sys.stdin.readline().rstrip()
             if not url: self.view.quit() #AppKit.NSApplication.sharedApplication().terminate_(None)
         else: 
             url = self.urls.pop(0)
             print "Popped URL from array ", url 
     else:
         #self.view.quit()
         self.quit() 
         #AppKit.NSApplication.sharedApplication().terminate_(None)

     print "Fetching", url, "..."
     #self.view.resetWebView()
     self.view.getURL(url, self.whenLoaded)
     #TODO: self.resetWebview(webview)
     
     # TODO: ??
     #if not webview.mainFrame().provisionalDataSource():
     if not self.view.isSourceLoaded():
         print " ... not a proper url?"
         self.processAllURLs()
     
  def makeFilename(self,URL,options):
     # make the filename
     if options.filename:
       filename = options.filename
     elif options.md5:
       try:
              import md5
       except ImportError:
              print "--md5 requires python md5 library"
              self.quit()
              #AppKit.NSApplication.sharedApplication().terminate_(None)
       filename = md5.new(URL).hexdigest()
     else:
       import re
       filename = re.sub('\W','',URL);
       filename = re.sub('^http','',filename);
     if options.datestamp:
       import time
       now = time.strftime("%Y%m%d")
       filename = now + "-" + filename
     import os
     dir = os.path.abspath(os.path.expanduser(options.dir))
     return os.path.join(dir,filename)
  
  def saveImages(self,bitmapData,filename,options):
    # Save fullsize PNG
    if options.fullsize:
      bitmapData.save(filename + "-full.png", None, 100)

    if options.thumb or options.clipped:
      # work out how big the thumbnail is
      #width = bitmapData.pixelsWide()
      #height = bitmapData.pixelsHigh()
      #thumbWidth = (width * options.scale)
      #thumbHeight = (height * options.scale)

      #
      # Do clipping/scaling here
      #
      thumbOutput = bitmapData
      clipOutput = bitmapData
      
      if options.thumb:
        # Save thumbnail
        thumbOutput.save(filename + "-thumb.png", None, 100)
      if options.clipped:
        clipOutput.save(filename + "-clipped.png", None, 100)
     
  def quit(self):
   sys.exit()

# Wrapper for the QtWebkit view of 
# a web page. Provides methods for 
# capturing and loading.
class WebSnapshotView(QtGui.QWidget):
 def __init__(self, parent = None):
   print "Initialise web view"
   self.app     = QtGui.QApplication(sys.argv)
   self.widget  = QtGui.QWidget.__init__(self)
   self.web     = QtWebKit.QWebView()
   #self.web.show()
   
   # Capture signal indicating page loaded
   self.connect(self.web, QtCore.SIGNAL("loadFinished(bool)"), self.loadFinished)
 
 def suspendQuit(self):
   # Stop programming quitting
    # until QtApp quits
    #sys.exit(self.app.exec_())
    return

 def getURL(self, url, callback):
   self.loadedCallback = callback
   print "Getting url: " + url
   self.currentURL = url
   qtURL = QtCore.QUrl(url)
   self.web.setUrl( qtURL )
          
 def loadFinished(self, success):
   print "Finished loading: ", self.currentURL, " with bool ", success   
   self.resizeWebView()
   #url = self.getAbsoluteURL()
   bitmapData = QtGui.QPixmap.grabWidget(self.web)
   self.loadedCallback(self.currentURL, bitmapData)
 
 def resizeWebView(self):
   size = self.web.page().mainFrame().contentsSize()
   self.web.setFixedSize(size)
 
 def quit(self):
   print "Quit message received. Need to tidy up."
   #sys.exit(self.app.exec_())
   #sys.exit()
   #print "Done"
   
 def resetWebView(self):
   print "Reset web view..."
   
 def isSourceLoaded(self):
   print "Check is url loaded"
   return True
   
def main():

    # parse the command line
    usage = """%prog [options] [http://example.net/ ...]

examples:
%prog http://google.com/            # screengrab google
%prog -W 1000 -H 1000 http://google.com/ # bigger screengrab of google
%prog -T http://google.com/         # just the thumbnail screengrab
%prog -TF http://google.com/        # just thumbnail and fullsize grab
%prog -o foo http://google.com/     # save images as "foo-thumb.png" etc
%prog -                             # screengrab urls from stdin"""

    cmdparser = OptionParser(usage, version=("webkit2png "+__version__))
    # TODO: add quiet/verbose options
    cmdparser.add_option("-W", "--width",type="float",default=800.0,
       help="initial (and minimum) width of browser (default: 800)")
    cmdparser.add_option("-H", "--height",type="float",default=600.0,
       help="initial (and minimum) height of browser (default: 600)")
    cmdparser.add_option("--clipwidth",type="float",default=200.0,
       help="width of clipped thumbnail (default: 200)",
       metavar="WIDTH")
    cmdparser.add_option("--clipheight",type="float",default=150.0,
       help="height of clipped thumbnail (default: 150)",
       metavar="HEIGHT")
    cmdparser.add_option("-s", "--scale",type="float",default=0.25,
       help="scale factor for thumbnails (default: 0.25)")
    cmdparser.add_option("-m", "--md5", action="store_true",
       help="use md5 hash for filename (like del.icio.us)")
    cmdparser.add_option("-o", "--filename", type="string",default="",
       metavar="NAME", help="save images as NAME.png,NAME-thumb.png etc")
    cmdparser.add_option("-F", "--fullsize", action="store_true",
       help="only create fullsize screenshot")
    cmdparser.add_option("-T", "--thumb", action="store_true",
       help="only create thumbnail sreenshot")
    cmdparser.add_option("-C", "--clipped", action="store_true",
       help="only create clipped thumbnail screenshot")
    cmdparser.add_option("-d", "--datestamp", action="store_true",
       help="include date in filename")
    cmdparser.add_option("-D", "--dir",type="string",default="./",
       help="directory to place images into")
    (options, args) = cmdparser.parse_args()
    if len(args) == 0:
        cmdparser.print_help()
        return
    if options.filename:
        if len(args) != 1 or args[0] == "-":
          print "--filename option requires exactly one url"
          return
    if options.scale == 0:
      cmdparser.error("scale cannot be zero")
    # make sure we're outputing something
    if not (options.fullsize or options.thumb or options.clipped):
      options.fullsize = True
      options.thumb = True
      options.clipped = True
    # work out the initial size of the browser window
    #  (this might need to be larger so clipped image is right size)
    options.initWidth = (options.clipwidth / options.scale)
    options.initHeight = (options.clipheight / options.scale)
    if options.width>options.initWidth:
       options.initWidth = options.width
    if options.height>options.initHeight:
       options.initHeight = options.height
       
    print "Options ::: "
    print options
    print "Args :::"
    print args
    
    print "Try making a filename:"
    processor = WebSnapshotProcessor(args, options)
    #processor.processAllURLs()
    sys.exit(processor.view.app.exec_())
       
if __name__ == '__main__' : main()
