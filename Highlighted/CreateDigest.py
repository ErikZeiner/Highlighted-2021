from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
import os, sys, parsePDF,parseToAnki, AddInfoWindow


class digest_window(QDialog):
	def __init__(self):
		super().__init__()
		# Basic setup
		self.setWindowTitle("Create Digest")
		self.resize(720, 480)
		self.setMinimumSize(720, 480)
		self.create = False
		self.enabled = list()

		# Widgets
		self.cb_export_colour = QCheckBox("Export with the highlighted colour")
		self.cb_export_colour.stateChanged.connect(self.cb_export_colour_changed)

		## Selecting window
		self.selecting_window = QGroupBox("Select annotations")
		self.selecting_window.setStyleSheet("font-size:14")
		self.scroll_selecting_window = QScrollArea()
		self.widget_selecting_window = QWidget()

		## Footer with buttons
		self.btn_create_image_files = QPushButton("Export Images")
		self.btn_create_image_files.clicked.connect(self.btn_create_image_files_clicked)

		self.btn_create_text_file = QPushButton("Export Text")
		self.btn_create_text_file.clicked.connect(self.btn_create_text_file_clicked)

		self.btn_close = QPushButton("Close")
		self.btn_close.clicked.connect(self.close)

		#Layout
		self.main_layout = QGridLayout()
		## Selecting window
		self.widget_selecting_window_layout = QGridLayout()
		self.selecting_window_layout = QHBoxLayout()

		self.widget_selecting_window.setLayout(self.widget_selecting_window_layout)
		self.scroll_selecting_window.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
		self.scroll_selecting_window.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.scroll_selecting_window.setWidgetResizable(True)
		self.scroll_selecting_window.setWidget(self.widget_selecting_window)
		self.selecting_window_layout.addWidget(self.scroll_selecting_window)
		self.selecting_window.setLayout(self.selecting_window_layout)

		## Footer
		self.controls_layout = QVBoxLayout()
		self.button_layout = QHBoxLayout()

		self.button_layout.addWidget(self.btn_create_image_files)
		self.button_layout.addWidget(self.btn_create_text_file)
		self.button_layout.addWidget(self.btn_close)

		self.controls_layout.addWidget(self.cb_export_colour)
		self.controls_layout.addLayout(self.button_layout)

		# ==========
		# Layouts
		self.main_layout.addWidget(self.selecting_window,2,0,1,2)

		self.main_layout.addLayout(self.controls_layout,3,0,1,2)
		self.setLayout(self.main_layout)

		# Show contents of the selecting window
		self.populate_selecting_window()

		# Create page_annotations
		parsePDF.load_page_annotations()

	def populate_selecting_window(self):
		'''Show all categories and colours and allow to select the ones which will be added to the deck'''
		data = parsePDF.page_range_parse(parsePDF.get_min_parse(), parsePDF.get_max_parse())
		row = 0
		for categories in data.keys():
			category = QLabel(categories)
			self.widget_selecting_window_layout.addWidget(category, row, 0)
			row += 1
			for colour in data[categories].keys():
				highlight = QCheckBox()
				highlight.setStyleSheet("background-color: %s;" % colour)
				highlight.setText(str(data[categories][colour]))
				highlight.setObjectName("%s%s" %(parsePDF.types_annotation[categories], colour))
				highlight.stateChanged.connect(self.highlight_colour_checked)
				self.widget_selecting_window_layout.addWidget(highlight,row, 0)
				row += 1
		# Push all to the top
		spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
		self.widget_selecting_window_layout.addItem(spacer)

	# Things clicked/changed
	def highlight_colour_checked(self):
		'''Enable or disable colour to be added'''
		sender_colour = self.sender().objectName()
		if self.sender().isChecked():
			if sender_colour not in self.enabled: self.enabled.append(sender_colour)
		else:
			self.enabled.remove(sender_colour)

	def cb_export_colour_changed(self):
		'''Changes whether annotations will have colour in images'''
		parsePDF.set_export_colour(self.sender().isChecked())

	def btn_create_image_files_clicked(self):
		'''Saves selected annotations as images to a folder'''
		path = QFileDialog.getExistingDirectory(self)
		if path:
			for page_num in range(parsePDF.get_min_parse()-1,parsePDF.get_max_parse()):
					page = parsePDF.get_document().load_page(page_num)
					for annot_num, annot in enumerate(parsePDF.annot_sort(page.annots())):
						if parsePDF.get_annot_data_string(annot) in self.enabled:
							parsePDF.save_picture(annot, path, page_num, annot_num)
		parsePDF.reset_values_lite()
		self.close()

	def btn_create_text_file_clicked(self):
		'''Saves selected annotations as text to a markdown document'''
		path, _ = QFileDialog.getSaveFileName(self,"",parsePDF.get_document().name+"_digest.md")
		if path:
			if os.path.exists(path): os.remove(path)
			md_file = open(path, 'a')
			md_file.write("# "+os.path.basename(parsePDF.get_document().name) + "\n\n")
			for page_num in range(parsePDF.get_min_parse()-1,parsePDF.get_max_parse()):
				page = parsePDF.get_document().load_page(page_num)
				if len(list(page.annots())) > 0:
					md_file.write("## Page "+str(page_num+1) + "\n\n")
				for annot in parsePDF.annot_sort(page.annots()):
					if parsePDF.get_annot_data_string(annot) in self.enabled:
						md_file.write(parsePDF.parse_as_text2(page,annot) + "   \n")
						if annot.info['content'] !="":
							md_file.write("_Note_: "+annot.info['content'] + "   \n")
						if parsePDF.get_export_colour():
							md_file.write("_"+parsePDF.get_annot_colour(annot) + "_"+"  \n\n")
						else: md_file.write("\n")
			md_file.close()
		parsePDF.reset_values_lite()
		self.close()

# Testing
if __name__ == '__main__':
	pass
