import sys
from tableGUI_mv import *
from pandas import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from pandasql import *
from matplotlib import *

# For testing purposes
# df = read_csv("test.csv")
df = read_csv("test.csv")
class EditCellDialog(QDialog):
    def __init__(self, view):
        super(QDialog, self).__init__()

        self.view = view
        self.editRow = QLineEdit(self)
        self.editColumn = QLineEdit(self)
        self.value = QLineEdit(self)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.form = QFormLayout(self)
    
        labelRow = QLabel('row:', self)
        labelColumn = QLabel('column:', self)
        labelValue = QLabel('value:', self)
    
        self.form.addRow(labelRow, self.editRow)
        self.form.addRow(labelColumn, self.editColumn)
        self.form.addRow(labelValue, self.value)
        self.form.addWidget(self.buttonBox)

        #self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.accepted)
        #self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.rejected)
        
    def accepted(self):
        # try to convert to bool, int, floats, or object based on value
        # change corresponding model
        columnName = self.editColumn.text()
        rowName = self.editRow.text()
        columnIndex= -1
        rowIndex = -1
        
        for i in range (0, self.view.columnCount()):
            if columnName == self.view.horizontalHeaderItem(i).text():
                columnIndex = i

        for i in range (0, self.view.rowCount()):
            print str(self.view.item(i, 0).text())
            if rowName == str(self.view.item(i, 0).text()):
                rowIndex = i
                
        self.view.setItem(rowIndex, columnIndex, MyTableWidgetItem(str(self.value.text()), self.view))
        self.close()

    def rejected(self):
        self.close()
        
class DataFrameController(QDialog):
    def __init__(self, idNum, manager, view, parent=None):
        super(DataFrameController, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() |
                              Qt.WindowSystemMenuHint |
                              Qt.WindowMinMaxButtonsHint)
        self.idNum = idNum
        self.manager = manager
        self.view = view

        self.grid = QGridLayout()
        self.menu = QMenuBar()
        self.signaler = Communicate()
        self.setLayout(self.grid)

        self.containsValidData = True
        
        if not (isinstance(self.view, DataFrameStatView) or isinstance(self.view, DataFrameHistogramView)):
            self.grid.addWidget(self.menu)

        self.grid.addWidget(self.view)

        editMenu = self.menu.addMenu('Edit')
        sortMenu = self.menu.addMenu('Sort')
        statMenu = self.menu.addMenu('Statistics')
        queryMenu = self.menu.addMenu('Query')

        editCell = QAction('Edit Cell', self)
        editCell.triggered.connect(self.prepareEditCell)
        editMenu.addAction(editCell)
        
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

        histogram = QAction('View Histogram', self)
        histogram.triggered.connect(self.prepareHistogram)
        statMenu.addAction(histogram)

        sqlQuery = QAction('SQL Query', self)
        sqlQuery.triggered.connect(self.prepareSqlQueryWindow)
        queryMenu.addAction(sqlQuery)

    def prepareEditCell(self):
        window = EditCellDialog(self.view)
        window.show()
        window.exec_()
        
    def prepareAddRow(self):
        self.view.addRow()

    def prepareDeleteRow(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Delete row:')      
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
        else:
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
        else:
            columnExists = True
            
        if not columnExists:
            error = QMessageBox.about(self, 'Error', 'Column does not exist!')
            
        return
    
    def prepareStatWindow(self):
        self.manager.createStatWindow(self.view)

    def prepareHistogram(self):
        #Get column name + Obtain data set
        columnName, boolVal = QInputDialog.getText(self.view, 'Histogram', 'Column name:')
        columnExists = False
        
        if boolVal:
            for i in range(self.view.columnCount()):
                if (self.view.horizontalHeaderItem(i).text() == columnName) and (str(columnName) != ""):
                    columnExists = True

           
        if not columnExists:
            error = QMessageBox.about(self, 'Error', 'Column does not exist!')
        else:
            # Build histogram from data set
            self.manager.createHistogramWindow(self.view, columnName)
        
    def prepareSqlQueryWindow(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'SQL Query:')
        if ok:
            try:
                current = self.view.model.getDataFrame()
                dataframe = sqldf(str(text).lower(), locals())
                self.manager.createTableWindow(dataframe, text, self.view)
            except Exception:
                error = QMessageBox.about(self, 'Error', 'Query was invalid. Another window will not open.')
        
    def getId(self):
        return self.idNum
    
    def isDirty(self):
        self.view.model.emitUpdateTableSignal()
        if (self.containsValidData):
            label = QLabel("<font color='orange'>Warning: Data is no longer valid (dirty).</font>")
            self.grid.addWidget(label)
            self.containsValidData = False

    def closeEvent(self, evnt):
        if (self.idNum != 1):
            self.manager.removeId(self.idNum)
            self.view.model.emitCloseWindowSignal()
            super(DataFrameController, self).closeEvent(evnt)
        else:
            if flag_nested:
                QCoreApplication.instance().quit()
        
class EventManager():
    def __init__(self, dataframe):
        self.countId = 0

    def setup(self, dataframe):
        self.model          = DataFrameModel(self, dataframe)
        self.initView       = DataFrameTableView(self.model)
        self.initController = DataFrameController(self.generateId(), self, self.initView)
        self.initController.setWindowTitle("DataFrame Explorer")
        self.controllers = []
        return True

    def begin(self):
        self.initController.show()

    def createTableWindow(self, dataframe, title, callerView):
        view = DataFrameTableView(DataFrameModel(self, dataframe))
        controller = DataFrameController(self.generateId(), self, view)
        #callerView.model.signaler.updateTableWindows.connect(controller.isDirty)
        self.controllers.append(controller)
        controller.setWindowTitle("Query: " + title)
        controller.show()
            
    def createStatWindow(self, view):
        view = DataFrameStatView(view.model)
        controller = DataFrameController(self.generateId(), self, view)
        view.model.signaler.updateStatWindows.connect(controller.isDirty)
        self.controllers.append(controller)
        controller.setWindowTitle("Statistics: Missing Values")
        controller.show()

    def createHistogramWindow(self, view, columnName):
        model = view.model.getDataFrame()
        data = model[str(columnName)]
        view = DataFrameHistogramView(data)
        controller = DataFrameController(self.generateId(), self, view)
        self.controllers.append(controller)
        controller.setWindowTitle("Histogram: " + str(columnName))
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
            error = QMessageBox.about(self.initController, 'Error', 'There was an issue closing a window.')

    def generateId(self):
        self.countId = self.countId + 1
        return self.countId 

def explore(dataframe, nested=True, inPlace=True):
    global flag_nested
    flag_nested = nested
    dataframePassed = None
    DataFrame.hist(dataframe)
    if inPlace:
        dataframePassed = dataframe
    else:
        dataframePassed = dataframe.copy()
        
    app = QApplication(sys.argv)
    manager = EventManager(dataframe)
    
    if manager.setup(dataframePassed):
        manager.begin()
        app.exec_()
        if not inPlace:
            return dataframePassed
    else:
        print "Error: Could not setup explore."

if __name__ == '__main__':
    explore()
