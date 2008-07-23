#!/usr/bin/env python

# webkit2png - makes screenshots of webpages
# http://www.paranoidfish.org/projects/webkit2png
__version__ = "0.1"

# $Id: webkit2png-0.4 398 2004-09-24 18:40:49Z paul $

# Copyright (C) 2004 Paul Hammond
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
  print "Can't find PyQt4 library files. Are you sure it's installed?"
  sys.exit()

from optparse import OptionParser

class WebRender(QtGui.QWidget):
  
  # initialise the Qt environment
  def __init__(self, options, parent = None):
    print "Initialising"        
    QtGui.QWidget.__init__(self, parent)
    
    web_view = QtWebKit.QWebView(self)
    self.web_view = web_view
    
    self.options = options
    
    # Connect load event
    self.connect(web_view, QtCore.SIGNAL("loadFinished(bool)"), self.render_finished)
  
  # render_url()
  # Renders a webpage to an image using the options
  # given.
  def render_url(self, url):
    print "Rendering ", url, "..."
    q_url = QtCore.QUrl(url)
    self.web_view.setUrl(q_url)
    self.filename = self.makeFilename(url, self.options)
    
  def render_finished(self, finished_result):
    print "Render is finished (", finished_result, ")"
    size = self.web_view.page().mainFrame().contentsSize()
    self.web_view.setFixedSize(size)
    QtGui.QPixmap.grabWidget(self.web_view).save(self.filename + ".png", None, 100)
    print "Done."
    
  def makeFilename(self,URL,options):
    # make the filename
    if options.filename:
     filename = options.filename
    elif options.md5:
     try:
            import md5
     except ImportError:
            print "--md5 requires python md5 library"
            sys.exit()
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
       
    # Begin program
    print "Options:"
    print options
    print "Args:"
    print args
    
    app = QtGui.QApplication([])
    
    web = WebRender(options)
    web.render_url(args[0])
    sys.exit(app.exec_())
    
if __name__ == '__main__' : main()
