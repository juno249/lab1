#coding: utf8
import sys
import os
import logging
import numpy as np
import re
import csv
import pandas as pd

from PyQt5.QtCore import *
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QFileDialog, QMessageBox
from PyQt5.uic import loadUiType


app = QApplication(sys.argv)
app.setApplicationName('')
form_class, base_class = loadUiType('mainwindow.ui')

# create logger
logger = logging.getLogger('app.log')
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

class MainWindow(QMainWindow, form_class):
    def __init__(self, *args):
        super(MainWindow, self).__init__(*args)
        self.setupUi(self)
        self.init()

        self.tbResultsModel = QtGui.QStandardItemModel(self)
        self.tbResults.setModel(self.tbResultsModel)

    def init(self):
        self.comboBoxFrom.clear()

        for dirpath, dirnames, filenames in os.walk("./db"):
            for filename in [f for f in filenames if f.endswith(".csv")]:
                self.comboBoxFrom.addItem(filename)
        globals()['current_table'] = str(self.comboBoxFrom.itemText(0))
        self.lineEditSelect.setText('name, group')
        self.lineEditWhere.setText('(id>1 and id < 3 ) or name == "Ivan"')

    def onComboBoxFromChanged(self, currentText):
        self.statusbar.showMessage('Current Table: %s' % currentText, 4000)
        globals()['current_table'] = currentText
        logger.info('Current table: %s' % currentText)
        data = pd.read_csv('./db/%s' % globals()['current_table'])
        columns = ''
        for column_name in list(data.columns.values):
            columns += '%s, ' % column_name
        self.lineEditColumnName.setText(columns[:-2])
        globals()['table_data'] = data

    def matchSelectStatement(self, select_statement):
        # match = re.match('(?:\w+\s*|,\s*)+', select_statement)
        return re.findall(r'(?:\w+\s*)+', select_statement)

    def splitColumn(self, select_statement):
        select_statement.lower() # convert all uppercase letters to lowercase
        select_statement = select_statement.replace(' ', '') # remove all whitespaces
        columns_name = self.matchSelectStatement(select_statement)
        if columns_name is not None:
            return columns_name

    def splitOperations(self, where_statement):
        where_statement = where_statement.replace(" ", "")
        or_operations = re.split('OR', where_statement)
        or_counter = len(or_operations)
        for op in or_operations:
            and_operations = re.split('AND', op)
            print(and_operations)
        # out = list()
        # for operation in operations:
        #     out.append(re.findall(r"(?:\w+|=|>|<|<>\w+)+", operation))
        # return out

    def isColumn(self, name):
        return name in [cols for cols in list(globals()['table_data'].columns.values)]

    def onBtnSubmitClicked(self):
        select_statement = self.lineEditSelect.text()
        where_statement = self.lineEditWhere.text()
        self.statusbar.showMessage('Getting data from table %s' % globals()['current_table'], 4000)
        logger.info('Query: SELECT %s FROM %s WHERE %s' % (select_statement, globals()['current_table'],
                                                           where_statement))

        if select_statement is not '':
            if where_statement is '':
                QMessageBox.information(None, "Error!", "Please input WHERE statement!")
                return
            else:
                try:
                    columns_name = self.splitColumn(select_statement)
                    data = pd.read_csv('./db/%s' % globals()['current_table'])
                    # check SELECT statement validation
                    for column in columns_name:
                        is_column = self.isColumn(column)
                    if is_column: # input columns is valid
                        #operations = self.splitOperations(where_statement) # get input OR operation
                        # print(operations)
                        # for operation in operations:
                        #     (key, value) = re.split(r"=|>|<|><",operation[0])
                        #     print(key)
                        #     print(value)
                        where_statement = where_statement.replace(" ", "").replace("AND", " and ")\
                                        .replace("and", " and ").replace("OR", " or ").replace("or", " or ")\
                                        .replace("==", " == ").replace('="', ' == ' )
                        try:
                            results = data.query(where_statement)
                        except Exception as e:
                            QMessageBox.information(None, "Error!", "Query string is invalid!")
                            logger.info(str(e))
                            return
                        # show result in table view
                        self.tbResultsModel.clear()
                        results = results[columns_name]
                        print(results)
                        i = 0
                        for row in results.values:
                            if i == 0:
                                self.tbResultsModel.setColumnCount(len(columns_name))
                                self.tbResultsModel.setHorizontalHeaderLabels(columns_name)
                                self.tbResults.horizontalHeader().setStretchLastSection(1)
                                items = [
                                    QtGui.QStandardItem(field)
                                    for field in row
                                ]
                                self.tbResultsModel.appendRow(items)
                                i = i + 1
                            else:
                                items = [
                                    QtGui.QStandardItem(field)
                                    for field in row
                                ]
                                self.tbResultsModel.appendRow(items)

                    else:
                        QMessageBox.information(None, "Error!", 'Column name not found')
                        logger.info('Column name not found')
                except ValueError as e:
                    logger.info(str(e))
        else:
            QMessageBox.information(None, "Error!", "Please input SELECT statement!")
            return



if __name__ == '__main__':
    form = MainWindow()
    form.setWindowTitle('Database Helper')
    form.show()
    sys.exit(app.exec_())