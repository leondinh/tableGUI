import sys
from pandas import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import re

class DataFrameModel:
    def __init__(self, manager, dataframe):
        self.manager    = manager
        self.dataframe  = dataframe

    def getDataFrame(self):
        return self.dataframe

    def setDataFrame(self, df):
        self.dataframe = df
        
    def setDataCell(self, row, column, value):

        cellType = self.dataframe[self.dataframe.columns[column]].dtypes
        val = QVariant(value)
        if (value == ""):
            if (cellType == "int64" or cellType == "float64"):
                self.dataframe[self.dataframe.columns[column]] = self.dataframe[self.dataframe.columns[column]].astype(float)
            else:
                self.dataframe[self.dataframe.columns[column]] = self.dataframe[self.dataframe.columns[column]].astype(object)
            self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],None)
            
        elif (value == "True" or value == "False"):
            val = val.toBool()
            if not cellType == "bool_":
                self.dataframe[self.dataframe.columns[column]] = self.dataframe[self.dataframe.columns[column]].astype(object)
            self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],val)

        elif (not re.search('[a-zA-Z.]', value) and val.canConvert(QVariant.Int)):
            val = val.toInt()
            if not (cellType == "int64" or cellType == "float64"):
                self.dataframe[self.dataframe.columns[column]] = self.dataframe[self.dataframe.columns[column]].astype(object)
            self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],val[0])

        elif (not re.search('[a-zA-Z]', value)):
            val = val.toFloat()            
            if cellType == "int64":
                self.dataframe[self.dataframe.columns[column]] = self.dataframe[self.dataframe.columns[column]].astype(float)
            elif not (cellType == "float64"):
                self.dataframe[self.dataframe.columns[column]] = self.dataframe[self.dataframe.columns[column]].astype(object)
            self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],val[0])

        else:
            val = val.toString()
            self.dataframe[self.dataframe.columns[column]] = self.dataframe[self.dataframe.columns[column]].astype(object)
            self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],val)
         
        return True

class MyTableWidgetItem(QTableWidgetItem):
    def __init__(self, number):
        QTableWidgetItem.__init__(self, number, QtGui.QTableWidgetItem.UserType)
        self.__number = number

    def __lt__(self, other):
        return self.__number < other.__number
    
class DataFrameTableView(QTableWidget):
    def __init__(self, model, parent=None):
        super(DataFrameTableView, self).__init__(parent)
        self.model = model
        self.setSortingEnabled(True)
        
        self.setColumnCount(len(self.model.getDataFrame().columns))
        self.setRowCount(len(self.model.getDataFrame().index))

	headers = list(self.model.getDataFrame().columns.values)
	self.setHorizontalHeaderLabels(headers)
	
        for i in range(len(self.model.getDataFrame().index)):
            for j in range(len(self.model.getDataFrame().columns)):
                if isnull(self.model.getDataFrame().iget_value(i,j)):
                    self.setItem(i,j, QTableWidgetItem(""))
                else:
                    self.setItem(i,j,QTableWidgetItem(str(self.model.getDataFrame().iget_value(i,j))))

        self.cellChanged.connect(self.setModelCell)

    def setModelCell(self):
        row = self.currentRow()
        column = self.currentColumn()
        value = self.item(row, column)
        self.model.setDataCell(row, column, value.text())
        return True

    def addRow(self):
        df = self.model.getDataFrame()
        self.insertRow(self.rowCount())
        emptyList = []
        for i in range(len(df.dtypes)):
            if (df.dtypes[i] == "bool_"):
                emptyList.append(False)
            else:
                emptyList.append(0)
                
        df.loc[len(df)+1] = emptyList
        for i in range(self.columnCount()):
            self.setItem(self.rowCount()-1, i, QTableWidgetItem(str(emptyList[i])))

    def deleteRow(self):
        df = self.model.getDataFrame()
        self.removeRow(self.rowCount()-1)
        df.drop(len(df.index)-1, inplace=True)
        
class DataFrameStatView(QListWidget):
    def __init__(self, model, parent=None):
        super(DataFrameStatView, self).__init__(parent)
        self.model = model
        
        currentFrame = self.model.getDataFrame()
        for i in range(len(currentFrame.columns)):
            df_s = currentFrame[currentFrame.columns[i]]
            df_s_notnas = df_s.dropna()
            columnName = currentFrame.columns[i]
            numMissing = len(df_s.index)-len(df_s_notnas.index)
            self.addItem(columnName + " is missing " + str(numMissing) + " out of " + str(len(df_s.index)))
