from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
import os, sys, parsePDF, CreateAnkiDeck, CreateDigest


class overview_category(QtGui.QStandardItem):
	def __init__(self, text):
		super().__init__()
		self.setEditable(False)
		self.setText(text)
		self.setSelectable(False)

class overview_item(QtGui.QStandardItem):
	def __init__(self, text, colour):
		super().__init__()
		self.setEditable(False)
		self.setBackground(QtGui.QColor(colour))
		self.setText(text)
		self.setSelectable(False)

class main_window(QMainWindow):
	resized = QtCore.pyqtSignal()
	def __init__(self):
		super().__init__()
		# Basic setup
		self.document_name = ""
		self.setWindowTitle("Highlighted")
		self.resize(720, 480)
		self.setMinimumSize(720, 480)
		self.setAcceptDrops(True)
		self.resized.connect(self.resizeEvent)

		# Widgets
		## PDF viewer
		self.pdf_window = QGroupBox()
		self.pdf_window.setStyleSheet("font-size:14")

		self.pdf_viewer = QLabel("Drop a PDF file")
		self.pdf_viewer.setContentsMargins(0, 0, 0, 0)
		self.pdf_viewer.setStyleSheet("qproperty-alignment: AlignCenter;")

		self.pdf_viewer_scroll_bar = QScrollBar()
		self.pdf_viewer_scroll_bar.setMinimum(1)
		self.pdf_viewer_scroll_bar.sliderMoved.connect(self.pdf_viewer_page_changed)
		self.pdf_viewer_scroll_bar.valueChanged.connect(self.pdf_viewer_page_changed)

		## Overview
		self.overview = QTreeView()
		self.overview.setHeaderHidden(True)
		self.overview_model = QtGui.QStandardItemModel()
		self.overview.setModel(self.overview_model)
		self.overview.expandAll()

		## Page range
		self.lbl_range = QLabel("Pages from:")
		self.lbl_range2 = QLabel("to:")
		self.lbl_range2.setFixedWidth(16)

		self.min_range = QSpinBox()
		self.min_range.setValue(1)
		self.min_range.setMinimum(1)
		self.min_range.setDisabled(True)
		self.min_range.valueChanged.connect(self.min_range_value_changed)

		self.max_range = QSpinBox()
		self.max_range.setDisabled(True)
		self.max_range.setMinimum(1)
		self.max_range.valueChanged.connect(self.max_range_value_changed)

		## Buttons
		self.digest_window = None
		self.btn_create_digest = QPushButton("Create Digest")
		self.btn_create_digest.clicked.connect(self.btn_create_digest_clicked)
		self.btn_create_digest.setDisabled(True)

		self.anki_window = None
		self.btn_create_anki = QPushButton("Create Anki Deck")
		self.btn_create_anki.clicked.connect(self.btn_create_anki_clicked)
		self.btn_create_anki.setDisabled(True)

		# ==========
		# Layouts
		self.main_widget = QWidget(self)
		self.setCentralWidget(self.main_widget)
		self.main_layout = QHBoxLayout()

		## PDF viewer
		self.pdf_viewer_layout = QHBoxLayout()
		self.pdf_viewer_layout.setContentsMargins(0, 0, 0, 0)
		self.pdf_viewer_layout.addWidget(self.pdf_viewer)
		self.pdf_viewer_layout.addWidget(self.pdf_viewer_scroll_bar)
		self.pdf_window.setLayout(self.pdf_viewer_layout)

		## Overview
		self.data_window = QVBoxLayout()
		self.data_window.addWidget(self.overview)

		## Buttons and page range
		self.btn_box = QVBoxLayout()

		self.range_box = QHBoxLayout()
		self.range_box.addWidget(self.lbl_range)
		self.range_box.addWidget(self.min_range)
		self.range_box.addWidget(self.lbl_range2)
		self.range_box.addWidget(self.max_range)

		self.btn_box.addLayout(self.range_box)
		self.btn_box.addWidget(self.btn_create_digest)
		self.btn_box.addWidget(self.btn_create_anki)

		# Main layouts
		self.main_layout.addWidget(self.pdf_window,1)
		self.data_window.addLayout(self.btn_box)
		self.main_layout.addLayout(self.data_window)
		self.main_widget.setLayout(self.main_layout)

	def create_over_view_model_data(self, data, root=None):
		'''Adds data to the overview tree widget, data are a dictionary with categories as keys;
		values contain a dictionary of number of annotations of a given colour as values and colour value as key; data model uses
		the overview_category and overview_item classes to diferentiate categories and annotations in style.'''
		self.overview_model.setRowCount(0)
		if root is None:
			root = self.overview_model.invisibleRootItem()
		for categories in data.keys():
			category = overview_category(categories)
			for colour in data[categories].keys():
				colour_row = overview_item(str(data[categories][colour]), colour)
				category.appendRow(colour_row)
			root.appendRow(category)

	def pdf_viewer_page_changed(self, page_num):
		'''Displays a page of the pdf in the PDF viewer'''

		# Get a pixmap of the page
		if parsePDF.get_document() != None:
			self.pdf_window.setTitle("Page "+str(page_num)+" of "+ str(parsePDF.max_document_page()) + " | "+self.document_name)
			pix = parsePDF.document_page(page_num - 1)

			# Create an image
			fmt = QtGui.QImage.Format_RGBA8888 if pix.alpha else QtGui.QImage.Format_RGB888
			image = QtGui.QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
			# Display it in the viewer, fit to height or width
			self.pdf_viewer.setPixmap(QtGui.QPixmap(image).scaled(self.pdf_viewer.size(), QtCore.Qt.KeepAspectRatio,QtCore.Qt.SmoothTransformation))

	#Page Range changed
	def min_range_value_changed(self,value):
		'''Sets the min page number (located in parsePDF)from which the annotations will be taken'''
		parsePDF.set_min_parse(value)
		# Moves the max value if needed
		if value >= self.max_range.value():
			self.max_range.setValue(value)

	def max_range_value_changed(self,value):
		'''Sets the max page number (located in parsePDF)from which the annotations will be taken'''
		parsePDF.set_max_parse(value)
		if value <= self.min_range.value():
			self.min_range.setValue(value)

	# Buttons clicked
	def btn_create_digest_clicked(self):
		'''Opens Create Digest window'''
		self.digest_window = CreateDigest.digest_window()
		self.digest_window.exec_()

	def btn_create_anki_clicked(self):
		'''Opens Create Anki Deck window'''
		self.anki_window = CreateAnkiDeck.anki_window()
		self.anki_window.exec_()

	# Window events
	def resizeEvent(self,value):
		'''When the window is resized the same function for changing is called but for the same page, this allows the current page to rescale'''
		if parsePDF.get_document():
			self.pdf_viewer_page_changed(self.pdf_viewer_scroll_bar.value())

	def dragEnterEvent(self, event):
		''' Allows user to drop a file, url is the file path '''
		if event.mimeData().hasUrls(): event.accept()
		else: event.ignore()

	def dropEvent(self, event):
		'''Loads the document and sets up the main window'''
		paths = [u.toLocalFile() for u in event.mimeData().urls()]
		for path in paths:
			if path[-3:] == "pdf":
				# Set dropped file as the document
				parsePDF.reset_values()
				parsePDF.load_document(path)
				self.pdf_viewer_scroll_bar.setMaximum(parsePDF.max_document_page())

				self.document_name = os.path.basename(path)
				self.pdf_viewer_page_changed(1)
				#Load the overview
				self.create_over_view_model_data(parsePDF.overview_parse())
				self.overview.expandAll()

				self.min_range.setEnabled(True)
				self.min_range.setMaximum(parsePDF.max_document_page())
				parsePDF.set_min_parse(1)

				self.max_range.setEnabled(True)
				self.max_range.setMaximum(parsePDF.max_document_page())
				self.max_range.setValue(parsePDF.max_document_page())
				parsePDF.set_max_parse(parsePDF.max_document_page())

				self.btn_create_digest.setEnabled(True)
				self.btn_create_anki.setEnabled(True)

			else:
				# Error message if something other than a pdf was dropped
				msg = QMessageBox()
				msg.setIcon(QMessageBox.Warning)

				msg.setText("Only PDF documents can be imported.")
				msg.setInformativeText("You have tried to import a file which does not end with .pdf.")
				msg.setWindowTitle("MessageBox demo")
				msg.setStandardButtons(QMessageBox.Ok)
				retval = msg.exec_()

	def keyPressEvent(self, event):
		'''Event for keys up, down, left and right. Changes pdf viewer.'''
		key = event.key()
		if key == QtCore.Qt.Key_Up or key == QtCore.Qt.Key_Left:
			new_value = self.pdf_viewer_scroll_bar.value() -1
			if new_value > 0: self.pdf_viewer_scroll_bar.setValue(new_value)
		elif key == QtCore.Qt.Key_Down or key == QtCore.Qt.Key_Right:
			new_value = self.pdf_viewer_scroll_bar.value() + 1
			if new_value <  self.pdf_viewer_scroll_bar.maximum(): self.pdf_viewer_scroll_bar.setValue(new_value)
		event.accept()

	def wheelEvent(self, event):
		'''Event for mouse and touchpad scroll. Changes pdf viewer.'''
		numPixels = event.pixelDelta()
		numDegrees = event.angleDelta() / 8
		if not numPixels.isNull():
			if numPixels.y() > 1:
				new_value = self.pdf_viewer_scroll_bar.value() -1
				if new_value > 0: self.pdf_viewer_scroll_bar.setValue(new_value)
			elif  numPixels.y() < -1:
				new_value = self.pdf_viewer_scroll_bar.value() + 1
				if new_value <=  self.pdf_viewer_scroll_bar.maximum(): self.pdf_viewer_scroll_bar.setValue(new_value)
			elif numPixels.y() > 100:
				new_value = self.pdf_viewer_scroll_bar.value() -5
				if new_value > 0: self.pdf_viewer_scroll_bar.setValue(new_value)
			elif  numPixels.y() < -100:
				new_value = self.pdf_viewer_scroll_bar.value() + 5
				if new_value <=  self.pdf_viewer_scroll_bar.maximum(): self.pdf_viewer_scroll_bar.setValue(new_value)
		elif not numDegrees.isNull():
			numSteps = numDegrees / 15
			if numSteps > 1:
				new_value = self.pdf_viewer_scroll_bar.value() -1
				if new_value > 0: self.pdf_viewer_scroll_bar.setValue(new_value)
			elif  numPixels < -1:
				new_value = self.pdf_viewer_scroll_bar.value() + 1
				if new_value <  self.pdf_viewer_scroll_bar.maximum(): self.pdf_viewer_scroll_bar.setValue(new_value)
			elif numSteps > 100:
				new_value = self.pdf_viewer_scroll_bar.value() -5
				if new_value > 0: self.pdf_viewer_scroll_bar.setValue(new_value)
			elif  numSteps < -100:
				new_value = self.pdf_viewer_scroll_bar.value() + 5
				if new_value <  self.pdf_viewer_scroll_bar.maximum(): self.pdf_viewer_scroll_bar.setValue(new_value)
		event.accept()

	def reset(self):
		parsePDF.reset_values()
		self.__init__()

def main():
	app = QApplication(sys.argv)
	highlighted = main_window()
	highlighted.show()
	sys.exit(app.exec_())

# Testing
if __name__ == '__main__':
	pass
