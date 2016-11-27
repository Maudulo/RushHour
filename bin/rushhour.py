#/usr/bin/python3
# -*- coding:utf-8 -*-

""" Main Module of the GooDoc Application.
    The application is started by launching this module.
    It contains the Window class and the main procedure.
"""

import sys
import os

from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QDialog, QFileDialog, QToolBar, QWidget)
from PyQt5.QtGui import QIcon
from controller import *
from dialogs import *
from displayer import *

# Images
ADD_FILES_ICON = "../img/addFiles.png"
START_ICON = "../img/start.png"
SETTINGS_ICON = "../img/settings.png"
NEXT_CONFIG_ICON = "../img/next.png"
PRED_CONFIG_ICON = "../img/pred.png"

# ToolTip
ADD_FILES_TIP = "Add files"
START_TIP = "Start generation"
NEXT_CONFIG_TIP = "Next config"
PRED_CONFIG_TIP = "Pred config"
SETTINGS_TIP = "Settings"

WINDOW_TITLE = "RUSH HOUR"

class Window (QMainWindow):
    """ This class is the main class of the application.
        It creates the main window of the application.
        Inherits: QMainWindow
    """

    def __init__(self):
        """ This method initialize the grid and set the toolbar
            Params: None
            Return: None
        """
        super().__init__()
        self.controller = ConfigController(self)
        self.initScreen()

    def initScreen(self):
        """ This method sets up the screen of the application.
            It sets the toolbar and the window title.
            Then the widget is shown.
            Params: None
            Return: None
        """
        self.createToolBar()
        self.setWindowTitle(WINDOW_TITLE)
        self.show()

    def createToolBar(self):
        """ Creates a ToolBar with 3 buttons: a file selector, a settings button and a start button. 
            Params: None
            Return: None
        """
        self.toolbar = QToolBar(self);
        
        addFileAction = QAction(QIcon(ADD_FILES_ICON), ADD_FILES_TIP, self)
        addFileAction.setShortcut('Ctrl+O')
        addFileAction.triggered.connect(self.fileSelectDialog)

        resolveAction=QAction(QIcon(START_ICON), START_TIP, self)
        resolveAction.triggered.connect(self.controller.solve)
        # resolveAction.setShortcut('Ctrl+K')

        settingsAction=QAction(QIcon(SETTINGS_ICON), SETTINGS_TIP, self)
        settingsAction.triggered.connect(self.settings)


        nextConfigAction = QAction(QIcon(NEXT_CONFIG_ICON), NEXT_CONFIG_TIP, self)
        nextConfigAction.triggered.connect(self.controller.displayNextConfig)

        predConfigAction = QAction(QIcon(PRED_CONFIG_ICON), PRED_CONFIG_TIP, self)
        predConfigAction.triggered.connect(self.controller.displayPredConfig)


        
        self.addToolBar(self.toolbar);
        self.toolbar.addAction(addFileAction)
        self.toolbar.addAction(resolveAction)
        self.toolbar.addAction(settingsAction)
        self.toolbar.addAction(predConfigAction)
        self.toolbar.addAction(nextConfigAction)



    def settings(self):
        """ Opens a settings dialog.
            Params: none
            Return: none
        """
        settingsDialog = SettingsDialog(self)
        settingsDialog.exec_()


    def fileSelectDialog(self):
        """ Opens a file selection dialog and display on the grid the selected file.
            Params: none
            Return: none
        """
        
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)

        if file_dialog.exec_() :
            print(file_dialog.selectedFiles())
            self.controller.setConfiguration(file_dialog.selectedFiles()[0])
    
    



if __name__ == "__main__":
    app = QApplication(sys.argv);
    rushhour = Window();
    sys.exit(app.exec_());

