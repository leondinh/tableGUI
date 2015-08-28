import sys
import numpy as np
from pandas import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import re

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

class Communicate(QObject):
    """Contains signals which can be emitted.
    """

    # Prompts updating statistics
    updateStatWindows = pyqtSignal()

    # Prompts updating table windows
    updateTableWindows = pyqtSignal()

    # prompts closing windows
    closeWindow = pyqtSignal()
    
class DataFrameModel:
    """Stores a dataframe which will be the model for a view.

    Attributes:
        manager: A reference to the event manager.
        dataframe: The main dataframe specific to the model.
        signaler: Used when other windows need to be updated.
    """
    
    def __init__(self, manager, dataframe):
        """Stores manager and dataframe into attributes,
            creates an instance of Communicate() for signaling.

        Args:
            manager: A reference to the event manager.
            dataframe: The main dataframe specific to the model.


        Returns:
        
        """
        
        self.manager    = manager
        self.dataframe  = dataframe
        self.signaler   = Communicate()
        
    def getDataFrame(self):
        """ Returns reference to the dataframe.

        Args:

        Returns:
            Reference to the dataframe.
        """
        
        return self.dataframe

    def setDataFrame(self, df):
        """ Change the dataframe attribute to reference new dataframe.

        Args:
            The new dataframe the model will use.

        Returns:

        """
        
        self.dataframe = df
        
    def setDataCell(self, row, column, value):
        """ Given a specific row, column, and value, set the corresponding data cell
            with the correct value making sure data types are properly adjusted.

        Args:
            row: Index/row name of the dataframe to be changed.
            column: Column name of the dataframe to be changed.
            value: The value to be inserted into row, column combination.

        Returns:
            True upon finishing.
        """

        # Obtain the column datatype (bool, int64, float64, object)
        cellType = self.dataframe[self.dataframe.columns[column]].dtypes

        # Value must be able to be converted to different types.
        val = QVariant(value)

        if cellType == "bool":
            # If not a valid boolean value, change type to object.
            if not str(value.text()) in ["True", "False", "0", "1"]:
                self.dataframe[self.dataframe.columns[column]] = self.dataframe[self.dataframe.columns[column]].astype(object)

            # Empty string means nan.
            if str(value.text()) == "":
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],np.nan)
            else:
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],val.toBool())

        elif cellType == "int64":
            # If valid integer, add value as an integer.
            if self.isInt(value.text()):
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],int(value.text()))

            # If valid float or nan, change column to float.
            elif self.isFloat(value.text()):
                self.dataframe[self.dataframe.columns[column]] = self.dataframe[self.dataframe.columns[column]].astype(float)
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],float(value.text()))
            elif value.text() == "":
                self.dataframe[self.dataframe.columns[column]] = self.dataframe[self.dataframe.columns[column]].astype(float)
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],np.nan)
            
            # Otherwise, change column to object.
            else:
                self.dataframe[self.dataframe.columns[column]] = self.dataframe[self.dataframe.columns[column]].astype(object)
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],str(value.text()))

        elif cellType == "float64":
            # If valid float or nan, add value normally.
            if self.isFloat(value.text()):
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],float(value.text()))
            elif value.text() == "":
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],np.nan)

            # Otherwise, change column to object.
            else:
                self.dataframe[self.dataframe.columns[column]] = self.dataframe[self.dataframe.columns[column]].astype(object)
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],str(value.text()))
                
        else:
            # When column data type is object, add string normally unless value added is "" which is interpretted as nan.
            if value.text() == "":
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],np.nan)
            else:
                self.dataframe.set_value(self.dataframe.index[row],self.dataframe.columns[column],str(value.text()))
                
        return True

    def emitUpdateStatSignal(self):
        """The statistics window is updated when
            a cell is changed from nan to valid or vice versa.
            It is also updated when a row is added or deleted.

        Args:

        Returns:
        """
        
        self.signaler.updateStatWindows.emit()

    def emitCloseWindowSignal(self):
        """Used for signaling model's windows to close.

        Args:

        Returns:
        """
        
        self.signaler.closeWindow.emit()
        
    def isInt(self, s):
        """Tells whether s is a valid integer.

        Args:
            s: Test value which is either an integer
            or not an integer.

        Returns:
            True if s is a valid integer.
        """
        
        try:
            int(s)
            return True
        except ValueError:
            return False

    def isFloat(self, s):
        """Tells whether s is a valid float.

        Args:
            s: Test value which is either a float
            or not a float.

        Returns:
            True if s is a valid float.
        """
        
        try:
            float(s)
            return True
        except ValueError:
            return False
        
class MyTableWidgetItem(QTableWidgetItem):
    """Overloaded QTableWidgetItem to allow for
        sorting based on numeric value as well as
        string value. Empty strings in the view (ie: nans in the model)
        are always largest.

    Attributes:
        self.__value: String value of item in table view.
        self.__view: Reference to the view the MyTableWidgetItem belongs to.
    """
    
    def __init__(self, value, view):
        """Saves the value inputed as a string as well as the reference to
            the view.

        Args:
            value: Value of item in table view.
            view: Reference to the view the MyTableWidgetItem belongs to.

        Returns:
        
        """

        # When displayed, it must be a string. Value internally is kept based
        # on actual datatype.
        QTableWidgetItem.__init__(self, str(value), QTableWidgetItem.UserType)

        self.__value = value
        self.__view = view
            
    def __lt__(self, other):
                model = self.__view.model.getDataFrame()

                # Obtain datatype of column
                if not self.column() == 0:
                    dtype = model.dtypes[self.column()-1]
                else:
                    return self.__value < other.__value

                # If datatype is not of type object, then no extra steps are needed.
                # The less than operation is interpretted as numeric.
                if dtype == "bool" or dtype == "int64" or dtype == "float64":       
                    return self.__value < other.__value
                
                # If datatype is of type object, we need to move the empty strings to
                # bottom, and specify an alphabetical sort.
                else:
                    myStringVal = str(self.__value)
                    otherStringVal = str(other.__value)

                    # Check whether either strings are empty.
                    if (myStringVal == ""):
                        return myStringVal > otherStringVal

                    if (otherStringVal == ""):
                        return myStringVal > otherStringVal
                                   
                    return str(self.__value) < str(other.__value)
    
    def changeValue(self, value):
        """Change the value of the cell specified by MyTableWidgetItem.

        Args:
            value: new value to be changed into.
        
        Returns:
        
        """
        
        self.__value = value

class DataFrameTableView(QTableWidget):
    """The graphical view which displays a DataFrameModel.

    Attributes:
        model: holds the dataframe which is iterated over and
        placed inside the DataFrameTableView.
    """
    
    def __init__(self, model, parent=None):
        """ Load dataframe into view and format initial settings.

        Args:
            model: holds the dataframe which is iterated over and
        placed inside the DataFrameTableView.
            
        Returns:

        """
        
        super(DataFrameTableView, self).__init__(parent)
        self.model = model

        # Allow sorting by clicking the column headers.
        self.setSortingEnabled(True)

        # Stretch table across entire window.
        self.horizontalHeader().setStretchLastSection(True)

        # Base the size of the widget on the size of the dataframe.
        self.setColumnCount(len(self.model.getDataFrame().columns)+1)
        self.setRowCount(len(self.model.getDataFrame().index))

        # First header is an empty because indices are also viewed in widget.
	headers = [""] + list(self.model.getDataFrame().columns.values)
	self.setHorizontalHeaderLabels(headers)
	
	self.setColumnWidth(0, 35)

	# Hide default indices in favor of extra column added to headers.
	self.verticalHeader().setVisible(False)

        # For indices column, remove ability to modify cells.
        for i in range(len(self.model.getDataFrame().index)):
            self.setItem(i, 0, MyTableWidgetItem(self.model.getDataFrame().index[i], self))
            self.item(i, 0).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        # Set the widget items to the corresponding dataframe cell.
        for i in range(len(self.model.getDataFrame().index)):
            for j in range(len(self.model.getDataFrame().columns)):
                
                if isnull(self.model.getDataFrame().iget_value(i,j)):
                    self.setItem(i,j+1,MyTableWidgetItem("", self))
                else:
                    self.setItem(i,j+1,MyTableWidgetItem(self.model.getDataFrame().iloc[i,j], self))

        # If a cell is changed directly via the table, go to setModelCell().
        self.cellChanged.connect(self.setModelCell)

    def setModelCell(self):
        """Take's user's change in a cell and updates the dataframe.

        Args:

        Returns:
        """

        # Save the order the table is currently sorted in.
        columnSortIndex = self.horizontalHeader().sortIndicatorSection()
        columnSortOrder = self.horizontalHeader().sortIndicatorOrder()
        shouldSort = False

        # If the table isn't in the default configuration, reset it so that
        # the indices are back in order. In order to properly map the widget
        # cells to the dataframe is if the indices match up.
        if (columnSortIndex < self.columnCount()):
            shouldSort = True

        if (shouldSort):
            self.sortItems(0,0)

        # Set the value of the dataframe.
        row = self.currentRow()
        column = self.currentColumn()
        value = self.item(row, column)
        oldValue = self.model.getDataFrame().iloc[row, column-1]
        self.model.setDataCell(row, column-1, value)

        value = self.model.getDataFrame().iloc[row,column-1]

        try:
            if (self.model.getDataFrame().dtypes[column-1] == "object" or self.model.getDataFrame().dtypes[column-1] == "float64")  and np.isnan(value):
                self.item(row,column).changeValue("")
            else:
                self.item(row,column).changeValue(value)
        except TypeError:
            self.item(row,column).changeValue(value)

        # Statistics windows sometimes will be dirty. 
        if (isnull(value) and notnull(oldValue)) or (notnull(value) and isnull(oldValue)):
            self.model.emitUpdateStatSignal()

        # Sort back to original configuration.
        if (shouldSort):
            self.sortItems(columnSortIndex, columnSortOrder)

        return True

    def addRow(self):
        """Adds an extra row to the dataframe and view.

        Args:

        Returns:
        """
        
        df = self.model.getDataFrame()
        self.insertRow(self.rowCount())

        # List will store default values of each row element based on datatypes of each column.
        emptyList = []

        # Save the order the table is currently sorted in.
        shouldSort = False
        columnSortIndex = self.horizontalHeader().sortIndicatorSection()
        columnSortOrder = self.horizontalHeader().sortIndicatorOrder()

        # Create row to be added.
        for i in range(len(df.dtypes)):
            if (df.dtypes[i] == "bool"):
                emptyList.append(False)
            else:
                emptyList.append(0)

        # Set the new index to the largest existing index number + 1.
        largestIndexNum = 0
        for i in range(len(df.index)):
            if (self.isFloat(df.index[i-1])) and (df.index[i-1] >= largestIndexNum):
                largestIndexNum = df.index[i-1] + 1

        # Add to dataframe.
        df.loc[largestIndexNum] = emptyList

        # Create list to add to view.
        emptyListViewed = [self.model.getDataFrame().index[len(self.model.getDataFrame().index)-1]] + emptyList

        # Sort if needed.
        if (columnSortIndex < self.columnCount()):
            shouldSort = True

        if (shouldSort):
            self.sortItems(0,0)

        # Add to view.
        for i in range(self.columnCount()):
            self.setItem(self.rowCount()-1, i, MyTableWidgetItem(emptyListViewed[i], self))

        # Revert back to original table configuration before sorting.
        if (shouldSort):
            self.sortItems(columnSortIndex, columnSortOrder)

        # Statistics windows sometimes will be dirty. 
        self.model.emitUpdateStatSignal()
        
    def deleteRow(self, row):
        """Deletes a row based on name.
            Row name is the index, which could be numeric or not numeric.

        Args:
            row: name of row to be deleted.
        """

        success = True
        shouldEmitSignal = False

        # Find the correct row which matches the name given.
        # Remove from view.
        for i in range(self.rowCount()):
            if str(self.item(i,0).text()) == str(row):
                savedValue = i
        try:
            self.removeRow(savedValue)
        except UnboundLocalError:
            success = False
            error = QMessageBox.about(self, 'Error', 'Row does not exist!')

        # If succesfully removed from view, try both removing row as a float
        # or as a string.
        if (success): 
            try:
                row = float(row)
                self.model.getDataFrame().drop(float(row), inplace=True)
                shouldEmitSignal = True
            except ValueError:
                try:
                    self.model.getDataFrame().drop(row, inplace=True)
                    shouldEmitSignal = True
                except ValueError:
                    error = QMessageBox.about(self, 'Error', 'Row does not exist!')

        # Statistics windows sometimes will be dirty. 
        if shouldEmitSignal:
            self.model.emitUpdateStatSignal()
            
    def isFloat(self, s):
        """Tells whether s is a valid float.

        Args:
            s: Test value which is either a float
            or not a float.

        Returns:
            True if s is a valid float.
        """

        try:
            float(s)
            return True
        except ValueError:
            return False
        
class DataFrameStatView(QListWidget):
    """ A view containing a list of missing values per column
        to be displayed in a window.

    Attributes:
        model: The model the DataFrameStatView is referencing to
        generate the list.
    """
    
    def __init__(self, model, parent=None):
        """Create the list and add items to it for each column.

        Args:
            model: The model the DataFrameStatView is referencing to
        generate the list.
            
        Returns:

        """
        
        super(DataFrameStatView, self).__init__(parent)
        self.model = model
        self.columnNames = []
        self.numMissingList = []

        # Iterate through each column and calculate the number of missing
        # values based on the total length and the length of the column without missing values.
        # For each column add information to list widget.
        currentFrame = self.model.getDataFrame()
        for i in range(len(currentFrame.columns)):
            df_s = currentFrame[currentFrame.columns[i]]
            df_s_notnas = df_s.dropna()
            columnName = currentFrame.columns[i]
            numMissing = len(df_s.index)-len(df_s_notnas.index)
            self.addItem(columnName + " is missing " + str(numMissing) + " out of " + str(len(df_s.index)))
            self.columnNames.append(columnName)
            self.numMissingList.append(float(numMissing*100)/len(df_s.index))
            
class DataFrameHistogramView(QDialog):
    """View a histogram about a particular dataframe column.

    Attributes:
        model: Column of dataframe to be viewed.
        numBins: Number of bins of the histogram.
        figure: A figure instance to plot on.
        canvas: Displays the figure.
        toolbar: Has options to move graph, save image, etc
    """
    
    def __init__(self, model, numBins, histogram=True, parent=None):
        """ Create view with histogram plot.

        Args:
            model: Column of dataframe to be viewed.
            numBins: Number of bins of the histogram.
            
        Returns:
        """
        
        super(DataFrameHistogramView, self).__init__(parent)
        # set variables
        self.histogram = histogram
        self.model = model
        self.numBins = numBins
        
        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Plot
        self.plot()

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def plot(self):
        """The data plot which will be included in the view.

        Args:

        Returns:

        """
        
        # create an axis
        ax = self.figure.add_subplot(111)

        # discards the old graph
        ax.hold(False)

        # plot data
        if (self.histogram):
            self.model.getDataFrame().hist(0, ax=(ax), bins=self.numBins)
            ax.set_xlabel('Bins')
            ax.set_ylabel('Frequency')
        else:
            N = len(self.model.getDataFrame().index) # number of columns
            ind = np.arange(N)
            width = 0.8 # width of each bar
            heights = self.model.getDataFrame().ix[:,0]

            # create bar chart
            ax.bar(ind, heights, width)

            # store name of each column in array
            labels = self.model.getDataFrame().index

            # format x axis
            ax.set_xticks(ind+width - width/2)
            ax.set_xticklabels(labels)
            ax.set_xlabel('Column Name')

            # format y axis
            fmt = '%s%%'
            yticks = mtick.FormatStrFormatter(fmt)
            
            ax.set_ylim([0,100])
            ax.yaxis.set_major_formatter(yticks)
            ax.set_ylabel('Percentage of Values Missing in Each Column')

            # add title
            ax.set_title('Missing Values')
            
        # refresh canvas
        self.canvas.draw()
