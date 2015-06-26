import sys
from pandas import *
from PyQt4.QtGui import *
import PyQt4.QtCore as QtCore

df = read_csv("test.csv", na_values=["hello","world","blah"])
df_s_notnas = None
def __baseView(dataframe, editOnly_list=None, addRows_flag=False, nonEditableEnabled_flag=True):
	# Create an PyQT4 application object.
	app 		= QApplication(sys.argv)
	window 		= QMainWindow()
	gridLayout 	= QGridLayout()
	centralWidget 	= QWidget()
        menuBar         = QMenuBar()
        
	# Create window w/ table
	datatable = QTableWidget()

	def handleAddRowButton():
                datatable.insertRow(datatable.rowCount())

        def sortAscending():
                nameExists = False
                columnName, boolVal = QInputDialog.getText(datatable, 'Sort', 'Column name:')
                if boolVal:
                        for i in range(datatable.columnCount()):
                                if datatable.horizontalHeaderItem(i).text() == columnName:
                                        datatable.sortItems(i, 0)
                                        nameExists = True
                if nameExists == False:
                        print "Error: Bad column name!"
                return
        
        def sortDescending():
                nameExists = False
                columnName, boolVal = QInputDialog.getText(datatable, 'Sort', 'Column name:')
                if boolVal:
                        for i in range(datatable.columnCount()):
                                if datatable.horizontalHeaderItem(i).text() == columnName:
                                        datatable.sortItems(i, 1)
                                        nameExists = True
                if nameExists == False:
                        print "Error: Bad column name!"
                return

        def viewStatMissingVals():
                dialog          = QDialog()
                gridLayout 	= QGridLayout()
                colList         = QListWidget()

                for i in range(len(dataframe.columns)):
                        df_s = dataframe[dataframe.columns[i]]
                        df_s_notnas = df_s.dropna()
                        columnName = dataframe.columns[i]
                        numMissing = len(df_s.index)-len(df_s_notnas.index)
                        colList.addItem(columnName + " is missing " + str(numMissing) + " out of " + str(len(df_s.index)))
                gridLayout.addWidget(colList,0,0)
                dialog.setLayout(gridLayout)
                dialog.exec_()
                        
                
	# Set number of columns and rows
	datatable.setColumnCount(len(dataframe.columns))
	datatable.setRowCount(len(dataframe.index))

	# Set column names
	listCol = list(dataframe.columns.values)
	datatable.setHorizontalHeaderLabels(listCol)

	# Set values in each cell
	for i in range(len(dataframe.index)):
		for j in range(len(dataframe.columns)):
			datatable.setItem(i,j,QTableWidgetItem(str(dataframe.iget_value(i, j))))
	gridLayout.addWidget(datatable,1,0)
	
	# Add menu bar
        gridLayout.addWidget(menuBar,0,0)
        fileMenu = menuBar.addMenu('File')
        editMenu = menuBar.addMenu('Edit')
        statMenu = menuBar.addMenu('Statistics')
        
        exitAction = QAction('Exit', window)
        exitAction.triggered.connect(exit)
        fileMenu.addAction(exitAction)

        sortActionAsc = QAction('Sort Ascending', window)
        sortActionAsc.triggered.connect(sortAscending)
        fileMenu.addAction(sortActionAsc)

        sortActionDesc = QAction('Sort Descending', window)
        sortActionDesc.triggered.connect(sortDescending)
        fileMenu.addAction(sortActionDesc)

        missingVal = QAction('Missing Values', window)
        missingVal.triggered.connect(viewStatMissingVals)
        statMenu.addAction(missingVal)
        
        if addRows_flag:
                addRow = QAction('Add Row', window)
                addRow.triggered.connect(handleAddRowButton)
                editMenu.addAction(addRow)
        
	window.setCentralWidget(centralWidget)
	centralWidget.setLayout(gridLayout)

        if editOnly_list is not None:
                for i in range(datatable.columnCount()):
                        headerName = datatable.horizontalHeaderItem(i).text()
                        inEditList = False
                        for j in range(len(editOnly_list)):
                                if headerName == editOnly_list[j]:
                                        inEditList = True
                        if inEditList == False:
                                for k in range(datatable.rowCount()):
                                        if nonEditableEnabled_flag == True:
                                                datatable.item(k, i).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                                        else:
                                                datatable.item(k, i).setFlags(QtCore.Qt.ItemIsSelectable)

        # Enable sorting on columns
        datatable.setSortingEnabled(True)
        
	# Set window size
	window.resize(430, 250)
 
	# Set window title  
	window.setWindowTitle("") 
 
	# Show window
	window.show()
	app.exec_()

	return datatable

def view(dataframe):
	__baseView(dataframe, [], nonEditableEnabled_flag=True)
	return

def edit(dataframe, editOnly_list=None, addRows_flag=False):
	datatable = __baseView(dataframe, editOnly_list, addRows_flag, nonEditableEnabled_flag=False)

	# Create new dataframe to return
	index = []
	for i in range(datatable.rowCount()):
		index.append(i)

	dfNew = DataFrame(index=index, columns=dataframe.columns)
        
	for i in range(datatable.rowCount()):
		for j in range(datatable.columnCount()):
			if not datatable.item(i,j):
				dfNew.set_value(dfNew.index[i], dfNew.columns[j], "")
			else:
				dfNew.set_value(dfNew.index[i], dfNew.columns[j], str(datatable.item(i, j).text()))
	return dfNew
