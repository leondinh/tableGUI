import sys
from tableGUI_mv import *
from pandas import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from pandasql import *
from matplotlib import *

class EditCellDialog(QDialog):
    """Prompts user for row, column names and value to be
        inserted into table cell.

    Attributes:
        view: The view of the controller which created the dialog.
        editRow: The text field for row name.
        editColumn: The text field for column name.
        value: Value to be inserted at specified row, column.
        buttonBox: Allow user to select Ok or cancel.
        form: The layout of the dialog for adding text fields and buttonBox.
    """
    def __init__(self, view):
        """Creates the dialog and puts the correct text fields and buttons.

        Args:
            view: The view of the controller which created the dialog.

        Returns:

        """
        
        super(QDialog, self).__init__()

        # Save view into attribute.
        self.view = view

        # Create the form.
        self.editRow = QLineEdit(self)
        self.editColumn = QLineEdit(self)
        self.value = QLineEdit(self)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.form = QFormLayout(self)

        # Add labels.
        labelRow = QLabel('row:', self)
        labelColumn = QLabel('column:', self)
        labelValue = QLabel('value:', self)
    
        self.form.addRow(labelRow, self.editRow)
        self.form.addRow(labelColumn, self.editColumn)
        self.form.addRow(labelValue, self.value)
        self.form.addWidget(self.buttonBox)

        # Map the buttons to their correct methods.
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.accepted)
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.rejected)
        
    def accepted(self):
        """Take user's input when Ok is pressed. Will do error checking on row
            and column names. Then, updates view and model.

        Args:

        Returns:
        """
                
        # try to convert to bool, int, floats, or object based on value
        # change corresponding model
        columnName = self.editColumn.text()
        rowName = self.editRow.text()
        columnIndex= -1
        rowIndex = -1

        # Check to see if column and row name exist
        for i in range (0, self.view.columnCount()):
            if columnName == self.view.horizontalHeaderItem(i).text():
                columnIndex = i

        for i in range (0, self.view.rowCount()):
            if rowName == str(self.view.item(i, 0).text()): # look at dataframe.index
                rowIndex = i


        if columnIndex == -1 or rowIndex == -1:
            error = QMessageBox.about(self, 'Error', 'Enter valid row and column names!')

        # Set the view item to new value.
        self.view.setItem(rowIndex, columnIndex, MyTableWidgetItem(str(self.value.text()), self.view))

        # Set the model data cell to new value.
        model = self.view.model
        model.setDataCell(rowIndex, columnIndex-1, self.value)
        
        self.close()
        
    def rejected(self):
        """User decides to press cancel.
        """
        
        self.close()

class CreateHistogramDialog(QDialog):
    """Prompts user for column name and number of bins for
        creating a histogram.

    Attributes:
        view: The view of the controller which created the dialog.
        manager: The event manager, needed to create new histogram window.
        columnName: The name of column to graph.
        numBins: The number of bins for the specified column.
        buttonBox: Allow user to select Ok or cancel.
        form: The layout of the dialog for adding text fields and buttonBox.
    """
    
    def __init__(self, view, manager):
        """Creates the dialog and puts the correct text fields and buttons.

        Args:
            view: The view of the controller which created the dialog.
            manager: The event manager, needed to create new histogram window.

        Returns:
        """
        super(QDialog, self).__init__()

        # Save args into attributes.
        self.view = view
        self.manager = manager

        # Create the form.
        self.columnName = QLineEdit(self)
        self.numBins = QLineEdit(self)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.form = QFormLayout(self)

        # Create labels.
        labelColumnName = QLabel('column name:', self)
        labelNumBins = QLabel('number of bins:', self)

        self.form.addRow(labelColumnName, self.columnName)
        self.form.addRow(labelNumBins, self.numBins)
        self.form.addWidget(self.buttonBox)

        # Map buttons to methods when clicked.
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.accepted)
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.rejected)
        
    def accepted(self):
        """Take user's input when Ok is pressed.

        Args:

        Returns:
        """
        
        # Get column name + number of bins
        columnName = str(self.columnName.text())
        try:
            numBins = int(self.numBins.text())
        except ValueError:
            error = QMessageBox.about(self, 'Error', 'Bin value must be an integer less than or equal to column length.')
            self.close()
            return

        # Make sure column name exists.
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
        """User decides to press cancel.
        """
        
        self.close()
        
class DataFrameController(QDialog):
    """The basic frame for creating a new window.
        Contains a menu which can be hidden.

    Attributes:
        setWindowFlags: Used to display the minimize, maximize, and close window
            buttons.
        idNum: Id number used by event manager to track controller.
        manager: The event manager which created the controller.
        view: The view which will be displayed to user.
        grid: Append new widgets to a grid.
        menu: A selection of options including edit, sort, statistics,
            and query which will be included in window if correct view is passed.
        signaler: Used to emit signals to child windows that do not reference
            the same model.
        setLayout: The layout will be set to the grid.
        containsValidData: Limits the number of times a window will add a
            message notifying user that data displayed is dirty. Only one message
            prompt is needed.
    """
    
    def __init__(self, idNum, manager, view, parent=None):
        """ Creates and sets up the controller window, adding all the necessary
            menu options if needed.

        Args:
            idNum: Id number used by event manager to track controller.
            manager: The event manager which created the controller.
            view: The view which will be displayed to user.

        Returns:
        """

        # DataFrameController inherits from QDialog.
        super(DataFrameController, self).__init__(parent)

        # Display minimize, maximize buttons on window bar.
        self.setWindowFlags(self.windowFlags() |
                              Qt.WindowSystemMenuHint |
                              Qt.WindowMinMaxButtonsHint)

        # Save args into atttributes.
        self.idNum = idNum
        self.manager = manager
        self.view = view

        # Create grid for easily appending widgets to window.
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        
        # Create menu bar.
        self.menu = QMenuBar()

        # Create menu bar for statistics windows.
        if (isinstance(self.view, DataFrameStatView)):
            self.statsMenu = QMenuBar()
            self.grid.addWidget(self.statsMenu)

            visualizeMenu = self.statsMenu.addMenu('Visualize')
            
            graphStats = QAction('Graph Statistics', self)
            graphStats.triggered.connect(self.prepareGraphStats)
            visualizeMenu.addAction(graphStats)

        # Create instance of Commnicate to allow controller to send signals.
        self.signaler = Communicate()

        # Data is currently not dirty.
        self.containsValidData = True

        # Only add menu bar if view is a DataFrameTableView.
        if not (isinstance(self.view, DataFrameStatView) or isinstance(self.view, DataFrameHistogramView)):
            self.grid.addWidget(self.menu)

        # Append view to grid.
        self.grid.addWidget(self.view)

        # Add menu options.
        editMenu = self.menu.addMenu('Edit')
        sortMenu = self.menu.addMenu('Sort')
        statMenu = self.menu.addMenu('Statistics')
        queryMenu = self.menu.addMenu('Query')

        # Specify menu actions with methods.
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
        """Creates a dialog window which prompts for column name,
            row name, and value to be inserted into the table.

        Args:

        Returns:
        """

        # Create the dialog window and display it to user.
        window = EditCellDialog(self.view)
        window.show()
        window.exec_()
        
    def prepareAddRow(self):
        """Connect to the table's addRow() method and insert a new row.

        Args:

        Returns:
        """

        self.view.addRow()

    def prepareDeleteRow(self):
        """Connect to the table's deleteRow() method and delete specified row.

        Args:

        Returns:
        """

        # Obtain row name from user.
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Delete row:')      
        if ok:
            # If valid, verify formatting and delete the row.
            self.view.deleteRow(str(text))

    def prepareAscendingSort(self):
        """Sorts the table's column in ascending order.

        Args:

        Returns:
        """

        # Obtain column name from user.
        columnName, boolVal = QInputDialog.getText(self.view, 'Sort', 'Column name:')
        columnExists = False


        # Iterate through column names to confirm it exists. If it does, sort the
        # column. If not, display error message.
        if boolVal:
            for i in range(self.view.columnCount()):
                if (self.view.horizontalHeaderItem(i).text() == columnName):
                    self.view.sortItems(i,0)
                    columnExists = True
        else:
            columnExists = True
            
        if not columnExists:
            error = QMessageBox.about(self, 'Error', 'Column does not exist!')
                    
    def prepareDescendingSort(self):
        """Sorts the table's column in descending order.

        Args:

        Returns:
        """

        # Obtain column name from user.
        columnName, boolVal = QInputDialog.getText(self.view, 'Sort', 'Column name:')
        columnExists = False

        # Iterate through column names to confirm it exists. If it does, sort the
        # column. If not, display error message.   
        if boolVal:
            for i in range(self.view.columnCount()):
                if (self.view.horizontalHeaderItem(i).text() == columnName):
                    self.view.sortItems(i,1)
                    columnExists = True
        else:
            columnExists = True
            
        if not columnExists:
            error = QMessageBox.about(self, 'Error', 'Column does not exist!')
    
    def prepareStatWindow(self):
        """Creates a statistics window.

        Args:

        Returns:
        """
        
        self.manager.createStatWindow(self.view)

    def prepareHistogram(self):
        """Creates a histogram window.

        Args:

        Returns:
        """
        
        window = CreateHistogramDialog(self.view, self.manager)
        window.show()
        window.exec_()
        
    def prepareSqlQueryWindow(self):
        """Prompts user for sqldf query with current table named "current."
            Will display returned dataframe in new window.

        Args:

        Returns:
        """

        # Obtain SQL query from user.
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'SQL Query:')

        # Attempt to pass query through sqldf and create new window
        # from dataframe returned.
        if ok:
            try:
                current = self.view.model.getDataFrame()
            
                # pandasql changes all bool columns to ints, need to convert back
                dataframe = sqldf(str(text).lower(), locals())
                boolColumns = []

                # get all names of columns which are of type boolean
                for i in range(0, len(current.columns)):
                    if str(current.ix[:,i].dtype) == 'bool':
                        boolColumns.append(current.ix[:,i].name)

                # convert the ones which were projected back to type boolean
                for i in range(0, len(dataframe.columns)):
                    for j in range(0, len(boolColumns)):
                        if dataframe.ix[:,i].name == boolColumns[j]:
                            name = dataframe.ix[:,i].name
                            dataframe[name] = dataframe[[i]].astype('bool')

                # create new window
                self.manager.createTableWindow(dataframe, "SQL Query: " + text, self.view)

            except Exception:
                error = QMessageBox.about(self, 'Error', 'Query was invalid. Another window will not open.')

    def prepareKeywordSearchWindow(self):
        """Prompts user for keyword and searches the current table for rows
            containing the string. Will display all of these rows in new window.

        Args:

        Returns:
        """
        
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
                    rowFrames.append(dataframe[i:i+1])
            try:
                newDataframe = concat(rowFrames)
                self.manager.createTableWindow(newDataframe, "Keyword Search: " + text, self.view)
            except ValueError:
                error = QMessageBox.about(self, 'Error', 'No matches. Another window will not open.')


    def prepareGraphStats(self):
        """Creates a graph of the current statistics being viewed.
            Assumption is that view is an instance of DataFrameStatView.

        Args:

        Returns:
        """
        
        self.manager.createStatGraphWindow(self.view)

  
    def getId(self):
        """Return the id number of the controller, ex usage: event manager
            removes closed windows from controllers list.

        Args:

        Returns:
        the id number of the controller
        """
        
        return self.idNum
    
    def isDirty(self):
        """ Appends label warning user that data in window is dirty/invalid
        due to a model update.

        Args:

        Returns:
        """
        
        if (self.containsValidData):
            label = QLabel("<font color='orange'>Warning: Data is no longer valid (dirty).</font>")
            self.grid.addWidget(label)
            self.containsValidData = False

    def closeEvent(self, evnt):
        """When window is closed, make sure to remove id from
            the event manager.

        Args:
            evnt: The close event.

        Returns:
        """

        # idNum = 1 is skipped because the initial controller is
        # not on controllers list.
        if (self.idNum != 1):
            self.manager.removeId(self.idNum)
            
            # Close window normally.
            super(DataFrameController, self).closeEvent(evnt)
        else:
            # Close all windows if user is closing main application window
            # and cascade is set to True.
            if flag_cascade:
                QCoreApplication.instance().closeAllWindows()
            else:
                super(DataFrameController, self).closeEvent(evnt)
        
class EventManager():
    """Keeps creates and tracks the number of windows.

    Attributes:
        countID: The number which is incremented and assigned to new windows when created.
        model: The dataframe passed by user which will be used in initial window.
        initView: The initial table which will be used to visualize dataframe.
        initController: The initial window with the view embedded within it.
        controllers: A list of the current windows.
    """
    
    def __init__(self, dataframe):
        """Initializes countId which holds every new window's id number.
        """ 
        self.countId = 0

    def setup(self, dataframe):
        """Creates the initial model, view, controller, and list of controllers.

        Args:
            dataframe: initial dataframe to be displayed in window.
            
        Returns:
            True on successfully creating all attributes.
        """
        self.model          = DataFrameModel(self, dataframe)
        self.initView       = DataFrameTableView(self.model)
        self.initController = DataFrameController(self.generateId(), self, self.initView)
        self.initController.setWindowTitle("DataFrame Explorer")
        self.controllers = []
        return True

    def begin(self):
        """ The initial window is displayed and no longer invisible.

        Args:
        
        Returns:
        """
        self.initController.show()

    def createTableWindow(self, dataframe, title, callerView):
        """ Creates a new window displaying the dataframe as a table
            by embedding a DataFrameTableView inside a new controller.

        Args:
            dataframe: To be passed into the model for new DataFrameTableView.
            title: The string to appear in window title bar.
            callerView: A reference to the previous view. To be used in the
                future for when the new table requires to act on a previous
                view's signal.
                
        Returns:
        """

        view = DataFrameTableView(DataFrameModel(self, dataframe))
        controller = DataFrameController(self.generateId(), self, view)

        # Add to running list of controllers.
        self.controllers.append(controller)
        
        controller.setWindowTitle(title)
        controller.show()
            
    def createStatWindow(self, view):
        """ Creates a new window displaying relevant statistics based off of
            view's model.

        Args:
            view: Take the view's model and display its statistics.
            
        Returns:
        """
        view = DataFrameStatView(view.model)
        controller = DataFrameController(self.generateId(), self, view)

        # If model updates, view will now be dirty.
        view.model.signaler.updateStatWindows.connect(controller.isDirty)

        # Add to running list of controllers.
        self.controllers.append(controller)
        
        controller.setWindowTitle("Statistics: Missing Values")
        controller.show()

    def createHistogramWindow(self, view, columnName, numBins):
        """ Creates a new window displaying a histogram based on a specific
            column of a view's model.

        Args:
            view: Take the view's model and project the column wanted to graph.
            columnName: Name of the column to be graphed.
            numBins: Number of bins for the histogram.

        Returns:
        """
        
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

        # If model updates, view will now be dirty.
        view.model.signaler.updateStatWindows.connect(controller.isDirty)
        
        # display results
        controller.setWindowTitle("Histogram: " + str(columnName))
        controller.show()

    def createStatGraphWindow(self, view):        
        """ Creates a new window displaying a graph based on a specific
            view's dataframe model.

        Args:
            view: Take the view's model and project stats needed.

        Returns:
        
        """

        # Get data and column info
        index = view.columnNames
        values = view.numMissingList

        dataframeToPass = DataFrame(values, index=index)

        # create model for view
        model = DataFrameModel(self, dataframeToPass)

        # create view
        newView = DataFrameHistogramView(model, len(index), histogram=False)

        # create controller
        controller = DataFrameController(self.generateId(), self, newView)
        self.controllers.append(controller)

        # If model updates, view will now be dirty.
        view.model.signaler.updateStatWindows.connect(controller.isDirty)

        # display results
        controller.setWindowTitle("Visualize: Missing Values Bar Chart")
        controller.show()
        
    def removeId(self, idNum):
        """ Removes the id of a controller/window from the list of running windows
            affilated with the event manager.

        Args:
            idNum: ID number affilated with a particular window. Get using the controller's
            getId() method.

        Returns:
        
        """
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
    """Creates event manager for windows and begins the QApplication.

    Initial method called by user to start the explorer application. User passes
    the dataframe that he wishes to view.

    Args:
    dataframe: The pandas dataframe to be displayed in explorer.
    inPlace: A flag which will decide whether the dataframe is modified directly
        or whether the edited dataframe will be returned.
    cascade: A flag which will decided whether to close all windows upon
        closing main explorer window.

    Returns:
    The edited dataframe if inPlace is True.
    """

    # Whether or not to implement cascading needs to be known globally.
    global flag_cascade
    flag_cascade = cascade

    # Decide whether or not to pass original dataframe or copy into the Event Manager.
    dataframePassed = None
    
    if inPlace:
        dataframePassed = dataframe
    else:
        dataframePassed = dataframe.copy()

    # Create and start the program.
    app = QApplication(sys.argv)
    manager = EventManager(dataframe)
    
    if manager.setup(dataframePassed):
        manager.begin()
        app.exec_()

        # User obtains the edited copy of the dataframe.
        if not inPlace:
            return dataframePassed
    else:
        print "Error: Could not setup explore."

if __name__ == '__main__':
    explore()
