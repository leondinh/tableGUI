import sys
from pandas import *
from PyQt4.QtGui import *
import PyQt4.QtCore as QtCore

df = read_csv("test.csv")
def __baseView(dataframe, editOnly_list=None, addRows_flag=False, nonEditableEnabled_flag=True):
	# Create an PyQT4 application object.
	app 		= QApplication(sys.argv)
	window 		= QMainWindow()
	gridLayout 	= QGridLayout()
	centralWidget 	= QWidget()
        menuBar         = QMenuBar()
        
	# Create window w/ table
	datatable = QTableWidget()

	if addRows_flag:	
		# Create add row button
		addRowButton = QPushButton('add row')

		# Create handler
		def handleAddRowButton():
			datatable.insertRow(datatable.rowCount())

		# Connect to handler
		addRowButton.clicked.connect(handleAddRowButton)
		addRowButton.show()

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
	
	if addRows_flag:
		gridLayout.addWidget(addRowButton,0,1)

	# Add menu bar
        gridLayout.addWidget(menuBar,0,0)
        fileMenu = menuBar.addMenu('File')
        exitAction = QAction('Exit', window)
        exitAction.triggered.connect(exit)
        fileMenu.addAction(exitAction)
        
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
