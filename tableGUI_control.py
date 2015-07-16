import sys
from tableGUI_mv import *
from pandas import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *

# For testing purposes
df = read_csv("test.csv",  na_values=["hello","world","blah"])

class DataFrameController(QDialog):
    def __init__(self, id, manager, view, parent=None):
        super(DataFrameController, self).__init__(parent)
        self.id = id
        self.manager = manager
        self.view = view

        self.grid = QGridLayout()
        self.menu = QMenuBar()
        self.setLayout(self.grid)
        self.grid.addWidget(self.menu)
        self.grid.addWidget(self.view)

        editMenu = self.menu.addMenu('Edit')
        statMenu = self.menu.addMenu('Statistics')

        addRow = QAction('Add Row', self)
        addRow.triggered.connect(self.prepareAddRow)
        editMenu.addAction(addRow)

        deleteRow = QAction('Delete Row', self)
        deleteRow.triggered.connect(self.prepareDeleteRow)
        editMenu.addAction(deleteRow)

        missingVal = QAction('Missing Values', self)
        missingVal.triggered.connect(self.prepareStatWindow)
        statMenu.addAction(missingVal)


    def prepareAddRow(self):
        self.view.addRow()

    def prepareDeleteRow(self):
        self.view.deleteRow()
        
    def prepareStatWindow(self):
        self.manager.createStatWindow(self.view)
        
    def getId(self):
        return self.id

class EventManager():
    def __init__(self, dataframe):
        self.countId = 0

    def setup(self, dataframe):
        self.model          = DataFrameModel(self, dataframe)
        self.initView       = DataFrameTableView(self.model)
        self.initController = DataFrameController(self.generateId, self, self.initView)
        self.controllers = []
        return True

    def begin(self):
        self.initController.show()

    def createStatWindow(self, view):
        view = DataFrameStatView(self.model)
        controller = DataFrameController(self.generateId, self, view)
        self.controllers.append(controller)
        controller.show()
        
    def generateId(self):
        self.countId = self.countId + 1
        return self.countId 
 
def explore(dataframe):
    app = QApplication(sys.argv)
    manager = EventManager(dataframe)
    
    if manager.setup(dataframe):
        manager.begin()
        app.exec_()
    else:
        print "Error: Could not setup explore."

if __name__ == '__main__':
    explore()
