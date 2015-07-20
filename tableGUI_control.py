import sys
from tableGUI_mv import *
from pandas import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *

# For testing purposes
df = read_csv("test.csv")

class DataFrameController(QDialog):
    def __init__(self, idNum, manager, view, parent=None):
        super(DataFrameController, self).__init__(parent)
        self.idNum = idNum
        self.manager = manager
        self.view = view

        self.grid = QGridLayout()
        self.menu = QMenuBar()
        self.signaler = Communicate()
        self.setLayout(self.grid)

        self.containsValidData = True
        
        if not (isinstance(self.view, DataFrameStatView)):
            self.grid.addWidget(self.menu)

        self.grid.addWidget(self.view)

        editMenu = self.menu.addMenu('Edit')
        sortMenu = self.menu.addMenu('Sort')
        statMenu = self.menu.addMenu('Statistics')

        addRow = QAction('Add Row', self)
        addRow.triggered.connect(self.prepareAddRow)
        editMenu.addAction(addRow)

        deleteRow = QAction('Delete Row', self)
        deleteRow.triggered.connect(self.prepareDeleteRow)
        editMenu.addAction(deleteRow)

        sortAscending = QAction('Sort Ascending', self)
        sortAscending.triggered.connect(self.prepareAscendingSort)
        sortMenu.addAction(sortAscending)

        sortDescending = QAction('Sort Descending', self)
        sortDescending.triggered.connect(self.prepareDescendingSort)
        sortMenu.addAction(sortDescending)
        
        missingVal = QAction('Missing Values', self)
        missingVal.triggered.connect(self.prepareStatWindow)
        statMenu.addAction(missingVal)

    def prepareAddRow(self):
        self.view.addRow()

    def prepareDeleteRow(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Delete column:')      
        if ok:
            self.view.deleteRow(str(text))

    def prepareAscendingSort(self):
        columnName, boolVal = QInputDialog.getText(self.view, 'Sort', 'Column name:')
        columnExists = False
        
        if boolVal:
            for i in range(self.view.columnCount()):
                if (self.view.horizontalHeaderItem(i).text() == columnName):
                    self.view.sortItems(i,0)
                    columnExists = True

        if not columnExists:
            error = QMessageBox.about(self, 'Error', 'Column does not exist!')
            
        return
                    
    def prepareDescendingSort(self):
        columnName, boolVal = QInputDialog.getText(self.view, 'Sort', 'Column name:')
        columnExists = False
        
        if boolVal:
            for i in range(self.view.columnCount()):
                if (self.view.horizontalHeaderItem(i).text() == columnName):
                    self.view.sortItems(i,1)
                    columnExists = True

        if not columnExists:
            error = QMessageBox.about(self, 'Error', 'Column does not exist!')
            
        return
    
    def prepareStatWindow(self):
        self.manager.createStatWindow(self.view)
        
    def getId(self):
        return self.idNum
    
    def isDirty(self):
        if (self.containsValidData):
            label = QLabel("<font color='orange'>Warning: Data is no longer valid (dirty).</font>")
            self.grid.addWidget(label)
            self.containsValidData = False

    def closeEvent(self, evnt):
        if (self.idNum != 1):
            self.manager.removeId(self.idNum)
        self.signaler.closeWindow.emit()
        super(DataFrameController, self).closeEvent(evnt)
        
class EventManager():
    def __init__(self, dataframe):
        self.countId = 0

    def setup(self, dataframe):
        self.model          = DataFrameModel(self, dataframe)
        self.initView       = DataFrameTableView(self.model)
        self.initController = DataFrameController(self.generateId(), self, self.initView)
        self.controllers = []
        return True

    def begin(self):
        self.initController.show()

    def createStatWindow(self, view):
        view = DataFrameStatView(self.model)
        controller = DataFrameController(self.generateId(), self, view)
        self.model.signaler.updateStatWindows.connect(controller.isDirty)
        self.controllers.append(controller)
        controller.show()

    def removeId(self, idNum):
        popNum = -1
        success = False
        for i in range(len(self.controllers)):
            if (self.controllers[i].getId() == idNum):
                popNum = i
                success = True

        if success:
            self.controllers.pop(popNum)
        else:
            error = QMessageBox.about(self.initController, 'Error', 'There was an issue closing the Statistics window.')

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
