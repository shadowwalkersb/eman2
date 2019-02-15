from PyQt5 import QtGui, QtCore, QtWebEngineWidgets
import inspect
from pprint import pprint


module = QtWebEngineWidgets

pprint([c for c in dir(module) if inspect.isclass(getattr(module, c))])
