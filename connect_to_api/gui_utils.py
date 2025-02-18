"""
gui_utils.py

This module provides helper functions for displaying message boxes.
"""

from PyQt5 import QtWidgets

def show_development_message(parent=None):
    """
    Display a warning message indicating that the selected sensor feature is under development.

    Parameters:
        parent (QWidget): The parent widget for the message box.
    """
    msg_box = QtWidgets.QMessageBox(parent)
    msg_box.setIcon(QtWidgets.QMessageBox.Warning)
    msg_box.setWindowTitle("Under Development")
    msg_box.setText("Unfortunately, this feature is under development.\nPlease select a different sensor type.")
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.exec_()

def show_error_message(message, parent=None):
    """
    Display an error message.

    Parameters:
        message (str): The error message to display.
        parent (QWidget): The parent widget for the message box.
    """
    msg_box = QtWidgets.QMessageBox(parent)
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)
    msg_box.setWindowTitle("Error")
    msg_box.setText(message)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.exec_()
