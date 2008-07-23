from PyQt4 import QtGui, QtCore, QtWebKit

class WebShot(QtGui.QWidget):
  
  def __init__(self, parent = None):
    print "Initialise"
    QtGui.QWidget.__init__(self, parent)
    #QtWebKit.QWebView.__init__(self, parent)
    
    web = QtWebKit.QWebView(self)
    url = QtCore.QUrl("http://news.bbc.co.uk") 
    web.setUrl(url)
    self.view = web
    
    # Doesn't work!
    self.connect(web, QtCore.SIGNAL("loadFinished(bool)"), self.doSnapshot)
    
  def doSnapshot(self, finishedVal):
    print finishedVal
    size = self.view.page().mainFrame().contentsSize()
    self.view.setFixedSize(size)
    QtGui.QPixmap.grabWidget(self.view).save("mysavefile.png", None, 100)
    sys.exit()

if __name__ == "__main__":

    import sys
    
    app = QtGui.QApplication(sys.argv)
    web_view = WebShot()
    sys.exit(app.exec_())