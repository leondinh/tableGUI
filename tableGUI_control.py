import sys
from tableGUI_mv import *
from pandas import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from pandasql import *
from matplotlib import *

# For testing purposes
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

        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.accepted)
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.rejected)
        
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
            if rowName == str(self.view.item(i, 0).text()):
                rowIndex = i


        if columnIndex == -1 or rowIndex == -1:
            error = QMessageBox.about(self, 'Error', 'Enter valid row and column names!')
            
        self.view.setItem(rowIndex, columnIndex, MyTableWidgetItem(str(self.value.text()), self.view))
        model = self.view.model
        model.setDataCell(rowIndex, columnIndex-1, self.value)
        self.close()
        
    def rejected(self):
        self.close()

class CreateHistogramDialog(QDialog):
    def __init__(self, view, manager):
        super(QDialog, self).__init__()

        self.view = view
        self.manager = manager
        self.columnName = QLineEdit(self)
        self.numBins = QLineEdit(self)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.form = QFormLayout(self)
    
        labelColumnName = QLabel('column name:', self)
        labelNumBins = QLabel('number of bins:', self)
    
        self.form.addRow(labelColumnName, self.columnName)
        self.form.addRow(labelNumBins, self.numBins)
        self.form.addWidget(self.buttonBox)

        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.accepted)
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.rejected)
        
    def accepted(self):
        # Get column name + number of bins
        columnName = str(self.columnName.text())
        try:
            numBins = int(self.numBins.text())
        except ValueError:
            error = QMessageBox.about(self, 'Error', 'Bin value must be an integer less than or equal to column length.')
            self.close()
            return
        
        columnExists = False
        for i in range(self.view.columnCount()):
            if (self.view.horizontalHeaderItem(i).text() == columnName) and (str(columnName) != ""):
                columnExists = True
                
        if not columnExists:
            error = QMessageBox.about(self, 'Error', 'Column does not exist!')
        else:
            try:
                self.manager.createHistogramWindow(self.view, columnName, numBins)
            except ValueError:
                error = QMessageBox.about(self, 'Error', 'More than 1 data point needed!')
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

        keywordSearch = QAction('Keyword Search', self)
        keywordSearch.triggered.connect(self.prepareKeywordSearchWindow)
        queryMenu.addAction(keywordSearch)

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
        window = CreateHistogramDialog(self.view, self.manager)
        window.show()
        window.exec_()
        
    def prepareSqlQueryWindow(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'SQL Query:')
        if ok:
            try:
                current = self.view.model.getDataFrame()
                dataframe = sqldf(str(text).lower(), locals())
                self.manager.createTableWindow(dataframe, "SQL Query: " + text, self.view)
            except Exception:
                error = QMessageBox.about(self, 'Error', 'Query was invalid. Another window will not open.')

    def prepareKeywordSearchWindow(self):
        # text is keyword
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Keyword Search:')
        if ok:
            keyword = text

            # iterate through rows, look for regex match with keyword
            dataframe = self.view.model.getDataFrame()
            rowFrames = []
            
            for i in range(len(dataframe)): # for each row
                match = False
                for j in range(len(dataframe.columns)): # for each column
                    if str(keyword) in str(dataframe.iloc[i,j]):
                        match = True
                if match:
                    rowFrames.append(df[i:i+1])
            try:
                newDataframe = concat(rowFrames)
                self.manager.createTableWindow(newDataframe, "Keyword Search: " + text, self.view)
            except ValueError:
                error = QMessageBox.about(self, 'Error', 'No matches. Another window will not open.')
   
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
            if isinstance(self.view, DataFrameHistogramView):
                self.view.model.emitCloseWindowSignal()
            super(DataFrameController, self).closeEvent(evnt)
        else:
            if flag_cascade:
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
        self.controllers.append(controller)
        controller.setWindowTitle(title)
        controller.show()
            
    def createStatWindow(self, view):
        view = DataFrameStatView(view.model)
        controller = DataFrameController(self.generateId(), self, view)
        view.model.signaler.updateStatWindows.connect(controller.isDirty)
        self.controllers.append(controller)
        controller.setWindowTitle("Statistics: Missing Values")
        controller.show()

    def createHistogramWindow(self, view, columnName, numBins):
        # project out the column wanted, cast to dataframe
        dataframeOfView = view.model.getDataFrame()

        if len(dataframeOfView[str(columnName)]) < numBins or numBins <= 0:
            error = QMessageBox.about(self.initController, 'Error', 'Bin value must be an integer less than or equal to column length.')
            return

        # passed if column is composed of ints or floats
        if (str(dataframeOfView[columnName].dtype) != 'object'):
            dataframeToPass = DataFrame(dataframeOfView[str(columnName)])
        else:
            wordLengths = []
            for i in range(len(dataframeOfView[columnName])):         
                if str(dataframeOfView[columnName][i]).lower() == 'nan':
                    wordLengths.append(0)
                else:
                    wordLengths.append(len(dataframeOfView[columnName][i]))
            dataframeToPass = DataFrame(wordLengths)
            dataframeToPass.columns = [columnName + " (length of string)"]
                          
        # create model for view
        model = DataFrameModel(self, dataframeToPass)

        # create view
        view = DataFrameHistogramView(model, numBins)

        # create controller
        controller = DataFrameController(self.generateId(), self, view)
        self.controllers.append(controller)

        # display results
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

def explore(dataframe, inPlace=False, cascade=False):
    global flag_cascade
    flag_cascade = cascade
    dataframePassed = None
    
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
