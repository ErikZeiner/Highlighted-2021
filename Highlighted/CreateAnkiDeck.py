from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
import os, sys, parsePDF,parseToAnki, AddInfoWindow

class anki_window(QDialog):
	def __init__(self):
		super().__init__()
		# Basic setup
		self.setWindowTitle("Create Anki Deck")
		self.resize(720, 480)
		self.setMinimumSize(720, 480)
		self.create = False
		self.paired = dict()
		self.enabled = list()

		# Widgets
		## Deck Name
		self.line_deck_name = QLineEdit()
		self.line_deck_name.textChanged.connect(self.create_check)

		## Choose between image and text export
		self.export_type_layout = QHBoxLayout()
		self.image_export = QRadioButton("Highlighted area as an Image")
		self.image_export.setChecked(True)
		self.image_export.type = "Image"
		self.image_export.clicked.connect(lambda: parsePDF.set_export_type(True))

		self.cb_export_colour = QCheckBox("Export with the highlighted colour")
		self.cb_export_colour.stateChanged.connect(self.cb_export_colour_changed)

		self.text_export = QRadioButton("Highlighted area as plaintext")
		self.text_export.clicked.connect(lambda: parsePDF.set_export_type(False))
		self.text_export.type = "PlainText"

		## Pairing window
		self.pairing_window = QGroupBox("Pair annotations")
		self.pairing_window.setStyleSheet("font-size:14")
		self.scroll_pairing_window = QScrollArea()
		self.widget_pairing_window = QWidget()

		## Selecting window
		self.selecting_window = QGroupBox("Select annotations")
		self.selecting_window.setStyleSheet("font-size:14")
		self.scroll_selecting_window = QScrollArea()
		self.widget_selecting_window = QWidget()

		## Footer with buttons
		self.btn_create_deck = QPushButton("Create Anki Deck")
		self.btn_create_deck.clicked.connect(self.btn_create_deck_clicked)
		self.btn_create_deck.setDisabled(True)

		self.btn_close = QPushButton("Close")
		self.btn_close.clicked.connect(self.close)

		#Layout
		self.main_layout = QGridLayout()

		## Deck Name
		self.deck_name_layout = QFormLayout()
		self.deck_name_layout.addRow("Anki Deck Name:", self.line_deck_name)

		## Choose between image and text export
		self.export_type_layout.addWidget(self.image_export)
		self.export_type_layout.addWidget(self.text_export)

		## Pairing window
		self.widget_pairing_window_layout = QGridLayout()
		self.pairing_window_layout = QHBoxLayout()

		self.widget_pairing_window.setLayout(self.widget_pairing_window_layout)
		self.scroll_pairing_window.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
		self.scroll_pairing_window.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.scroll_pairing_window.setWidgetResizable(True)
		self.scroll_pairing_window.setWidget(self.widget_pairing_window)
		self.pairing_window_layout.addWidget(self.scroll_pairing_window)
		self.pairing_window.setLayout(self.pairing_window_layout)

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

		self.button_layout.addWidget(self.btn_create_deck)
		self.button_layout.addWidget(self.btn_close)

		self.controls_layout.addWidget(self.cb_export_colour)
		self.controls_layout.addLayout(self.button_layout)

		# ==========
		# Layouts
		self.main_layout.addLayout(self.deck_name_layout,0,0)
		self.main_layout.addLayout(self.export_type_layout,0,1)
		self.main_layout.addWidget(self.selecting_window,2,0)
		self.main_layout.addWidget(self.pairing_window,2,1)
		self.main_layout.addLayout(self.controls_layout,3,0,1,2)
		self.setLayout(self.main_layout)

		# Show contents of the selecting window
		self.populate_selecting_window()

		# Create page_annotations
		parsePDF.load_page_annotations()

	def populate_pairing_window(self):
		''' Show all colour with comboboxes, which can be used to pair up the colour'''
		# Delete all current widgets
		for i in reversed(range(self.widget_pairing_window_layout.count())):
			item = self.widget_pairing_window_layout.itemAt(i)
			if str(type(item)) != "<class 'PyQt5.QtWidgets.QSpacerItem'>": item.widget().deleteLater()

		row = 0
		data = parsePDF.page_range_parse(parsePDF.get_min_parse(), parsePDF.get_max_parse())
		for categories in data.keys():
			for colour in data[categories].keys():
				colour_data = "%s%s" %(parsePDF.types_annotation[categories], colour)
				if colour_data in self.enabled:
					highlight = QLabel(categories.title())
					highlight.setStyleSheet("background-color: %s;" %colour)
					highlight.setAlignment(QtCore.Qt.AlignCenter)

					highlight_pair = QComboBox()
					highlight_pair.setObjectName(colour_data)
					highlight_pair.activated.connect(self.highlight_pair_changed)
					highlight_pair.addItem("")
					highlight_pair.setItemData(0,[colour_data,None])
					
					highlight2 = QLabel()
					highlight2.setAlignment(QtCore.Qt.AlignCenter)
					
					for categories2 in data.keys():
						for colour2 in data[categories2].keys():
							colour_data2 = "%s%s" %(parsePDF.types_annotation[categories2], colour2)
							if (colour_data in self.paired.values() and colour_data2 in self.paired.keys()) and colour_data2 != colour_data:
								highlight_pair.setItemText(0,"BACK - FRONT")
								highlight_pair.setEnabled(False)
								highlight_pair.setCurrentIndex(i)
								highlight2.setText(categories2.title())
								highlight2.setStyleSheet("background-color: %s;" %colour2)
								break
							
							if colour_data2 == self.paired.get(colour_data,""):
								highlight_pair.insertItem(1,"FRONT - BACK")
								highlight_pair.setCurrentIndex(1)
								highlight2.setText(categories2.title())
								
								highlight2.setStyleSheet("background-color: %s;" %colour2)
							elif colour_data2 in self.enabled and (colour_data2 not in self.paired.keys() or colour_data2 not in self.paired.values()):
								if colour_data != colour_data2 and (colour_data2 not in self.paired.keys() and colour_data2 not in self.paired.values()):
									highlight_pair.addItem(str(parsePDF.annotation_types[int(colour_data2[0])]).title())
									highlight_pair.setItemData(highlight_pair.count()-1,QtGui.QColor(colour2), QtCore.Qt.BackgroundRole)
									highlight_pair.setItemData(highlight_pair.count()-1,[colour_data,colour_data2])

					self.widget_pairing_window_layout.addWidget(highlight,row,0)
					self.widget_pairing_window_layout.addWidget(highlight_pair,row,1)
					self.widget_pairing_window_layout.addWidget(highlight2,row,2)
					row += 1

	def populate_selecting_window(self):
		'''Show all categories and colours and allow to select the ones which will be added to the deck'''
		data = parsePDF.page_range_parse(parsePDF.get_min_parse(), parsePDF.get_max_parse())
		row = 0
		for categories in data.keys():
			category = QLabel(categories)
			self.widget_selecting_window_layout.addWidget(category, row, 0)
			row += 1
			for colour in data[categories].keys():
				# Coloured line with number of annotations
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

	def create_check(self):
		'''Only allow the create deck button to be pressed when a name has been given to the deck'''
		global deck_name
		if self.line_deck_name.text() != '':
			deck_name = self.line_deck_name.text()
			self.btn_create_deck.setEnabled(True)
		else:
			self.btn_create_deck.setDisabled(True)
	# Things clicked/changed
	def highlight_pair_changed(self):
		''' Selected colour to be paired'''
		data_dict = self.sender().currentData()
		if data_dict is not None:
			if data_dict[1] is not None:
				self.paired[data_dict[0]] = data_dict[1]
			else:
				if data_dict[0] in self.paired.keys(): del self.paired[data_dict[0]]
		self.populate_pairing_window()

	def highlight_colour_checked(self):
		'''Enable or disable colour to be added to the deck'''
		sender_colour = self.sender().objectName()
		if self.sender().isChecked():
			if sender_colour not in self.enabled: self.enabled.append(sender_colour)
		else:
			self.enabled.remove(sender_colour)
			self.paired = {key:val for key, val in self.paired.items() if val != sender_colour and key != sender_colour}
		self.populate_pairing_window()

	def cb_export_colour_changed(self):
		'''Changes whether annotations will have colour in images'''
		parsePDF.set_export_colour(self.sender().isChecked())

	def btn_create_deck_clicked(self):
		'''Creates the deck and opens the window to add cards'''
		parsePDF.mark_annotations(self.enabled, self.paired)
		parseToAnki.create_deck(self.line_deck_name.text())
		self.close()
		self.add_info = AddInfoWindow.add_info_window(self.line_deck_name.text())
		self.add_info.exec()

# Testing
if __name__ == '__main__':
	pass
