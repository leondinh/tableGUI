import sys
import numpy as np
from pandas import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import re

class Communicate(QObject):
    updateStatWindows = pyqtSignal()
    closeWindow = pyqtSignal()
    
class DataFrameModel:
    def __init__(self, manager, dataframe):
        self.manager    = manager
        self.dataframe  = dataframe
        self.signaler   = Communicate()
        
    def getDataFrame(self):
        return self.dataframe

    def setDataFrame(self, df):
        self.dataframe = df
        
    def setDataCell(self, row, column, value):
        cellType = self.dataframe[self.dataframe.columns[column]].dtypes
        val = QVariant(value)
        
        if cellType == "bool":
            if not str(value.text()) in ["True", "False", "0", "1"]:
                self.dataframe[self.dataframe.columns[column]] = self.dataframe[self.dataframe.columns[column]].astype(object)
                
            if str(value.text()) == "":
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],np.nan)
            else:
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],val.toBool())

        elif cellType == "int64":
            if self.isInt(value.text()):
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],int(value.text()))
            elif self.isFloat(value.text()):
                self.dataframe[self.dataframe.columns[column]] = self.dataframe[self.dataframe.columns[column]].astype(float)
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],float(value.text()))
            elif value.text() == "":
                self.dataframe[self.dataframe.columns[column]] = self.dataframe[self.dataframe.columns[column]].astype(float)
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],np.nan)
            else:
                self.dataframe[self.dataframe.columns[column]] = self.dataframe[self.dataframe.columns[column]].astype(object)
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],str(value.text()))

        elif cellType == "float64":
            if self.isFloat(value.text()):
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],float(value.text()))
            elif value.text() == "":
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],np.nan)
            else:
                self.dataframe[self.dataframe.columns[column]] = self.dataframe[self.dataframe.columns[column]].astype(object)
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],str(value.text()))
                
        else:
            if value.text() == "":
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],np.nan)
            else:
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],str(value.text()))
                
        return True

    def emitUpdateStatSignal(self):
        self.signaler.updateStatWindows.emit()
    
    def isInt(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def isFloat(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False
        
class MyTableWidgetItem(QTableWidgetItem):
    # type is either: bool, int, float, or object
    def __init__(self, value, view):
        if value == "":
            QTableWidgetItem.__init__(self, "", QTableWidgetItem.UserType)
        else:
            QTableWidgetItem.__init__(self, str(value), QTableWidgetItem.UserType)

        self.__value = value
        self.__view = view
            
    def __lt__(self, other):
                model = self.__view.model.getDataFrame()

                if not self.column() == 0:
                    dtype =  model.dtypes[model.index[self.column()]-1]
                else:
                    return self.__value < other.__value

                if dtype == "bool" or dtype == "int64" or dtype == "float64":
                    myVal = self.__value
                    otherVal = other.__value                    
                    return self.__value < other.__value
                else:
                    myStringVal = str(self.__value)
                    otherStringVal = str(other.__value)

                    if (myStringVal == ""):
                        return myStringVal > otherStringVal

                    if (otherStringVal == ""):
                        return myStringVal > otherStringVal
                                   
                    return str(self.__value) < str(other.__value)
    
    def changeValue(self, value):
        self.__value = value

class DataFrameTableView(QTableWidget):
    def __init__(self, model, parent=None):
        super(DataFrameTableView, self).__init__(parent)
        self.model = model
        self.setSortingEnabled(True)
        self.horizontalHeader().setStretchLastSection(True)
        
        self.setColumnCount(len(self.model.getDataFrame().columns)+1)
        self.setRowCount(len(self.model.getDataFrame().index))


	headers = [""] + list(self.model.getDataFrame().columns.values)
	self.setHorizontalHeaderLabels(headers)
	self.setColumnWidth(0, 35)
	self.verticalHeader().setVisible(False)

        for i in range(len(self.model.getDataFrame().index)):
            self.setItem(i, 0, MyTableWidgetItem(self.model.getDataFrame().index[i], self))
            self.item(i, 0).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        for i in range(len(self.model.getDataFrame().index)):
            for j in range(len(self.model.getDataFrame().columns)):
                
                if isnull(self.model.getDataFrame().iget_value(i,j)):
                    self.setItem(i,j+1,MyTableWidgetItem("", self))
                else:
                    self.setItem(i,j+1,MyTableWidgetItem(self.model.getDataFrame().iloc[i,j], self))

        self.cellChanged.connect(self.setModelCell)

    def setModelCell(self):
        columnSortIndex = self.horizontalHeader().sortIndicatorSection()
        columnSortOrder = self.horizontalHeader().sortIndicatorOrder()
        shouldSort = False
        
        if (columnSortIndex < self.columnCount()):
            shouldSort = True

        if (shouldSort):
            self.sortItems(0,0)

        row = self.currentRow()
        column = self.currentColumn()
        value = self.item(row, column)

        self.model.setDataCell(row, column-1, value)

        value = self.model.getDataFrame().iloc[row,column-1]
        
        try:
            if (self.model.getDataFrame().dtypes[column-1] == "object" or self.model.getDataFrame().dtypes[column-1] == "float64")  and np.isnan(value):
                self.item(row,column).changeValue("")
            else:
                self.item(row,column).changeValue(value)
        except TypeError:
            self.item(row,column).changeValue(value)

        if (shouldSort):
            self.sortItems(columnSortIndex, columnSortOrder)

        self.model.emitUpdateStatSignal()
        
        return True

    def addRow(self):
        df = self.model.getDataFrame()
        self.insertRow(self.rowCount())
        emptyList = []
        shouldSort = False
        
        columnSortIndex = self.horizontalHeader().sortIndicatorSection()
        columnSortOrder = self.horizontalHeader().sortIndicatorOrder()
        
        for i in range(len(df.dtypes)):
            if (df.dtypes[i] == "bool"):
                emptyList.append(False)
            else:
                emptyList.append(0)

        largestIndexNum = 0
        for i in range(len(df.index)):
            if (self.isFloat(df.index[i-1])) and (df.index[i-1] >= largestIndexNum):
                largestIndexNum = df.index[i-1] + 1
                
        df.loc[largestIndexNum] = emptyList

        emptyListViewed = [self.model.getDataFrame().index[len(self.model.getDataFrame().index)-1]] + emptyList
        if (columnSortIndex < self.columnCount()):
            shouldSort = True

        if (shouldSort):
            self.sortItems(0,0)
            
        for i in range(self.columnCount()):
            self.setItem(self.rowCount()-1, i, MyTableWidgetItem(emptyListViewed[i], self))

        if (shouldSort):
            self.sortItems(columnSortIndex, columnSortOrder)
            
    def deleteRow(self, column):
        success = True
        for i in range(self.rowCount()):
            if str(self.item(i,0).text()) == str(column):
                savedValue = i
        try:
            self.removeRow(savedValue)
        except UnboundLocalError:
            success = False
            error = QMessageBox.about(self, 'Error', 'Column does not exist!')

        if (success): 
            try:
                column = float(column)
                self.model.getDataFrame().drop(float(column), inplace=True)
            except ValueError:
                try:
                    self.model.getDataFrame().drop(column, inplace=True)
                except ValueError:
                    error = QMessageBox.about(self, 'Error', 'Column does not exist!')

    def isFloat(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False
        
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
            
