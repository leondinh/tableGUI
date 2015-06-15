import sys
from pandas import *
from PyQt4.QtGui import *

def __baseView(dataframe, editCellOnly_flag, addRows_flag):
	# Create an PyQT4 application object.
	app 		= QApplication(sys.argv)
	window 		= QMainWindow()
	gridLayout 	= QGridLayout()
	centralWidget 	= QWidget()

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

	# Disable edit
	if not editCellOnly_flag:
		datatable.setEditTriggers(QAbstractItemView.NoEditTriggers)

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
	gridLayout.addWidget(datatable,0,0)
	if addRows_flag:
		gridLayout.addWidget(addRowButton,0,1)

	window.setCentralWidget(centralWidget)
	centralWidget.setLayout(gridLayout)

	# Set window size
	width = min((j+1)*105, app.desktop().screenGeometry().width() - 50)
	height = min((i+1)*41, app.desktop().screenGeometry().height() - 100)
	window.resize(width, height)
 
	# Set window title  
	window.setWindowTitle("") 
 
	# Show window
	window.show()
	app.exec_()

	return datatable

def view(dataframe):
	__baseView(dataframe, False, False)
	return

def edit(dataframe, addRows_flag):
	datatable = __baseView(dataframe, True, addRows_flag)

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
