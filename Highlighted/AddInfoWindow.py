from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
import os, sys, fitz, parsePDF, parseToAnki

class add_info_window(QDialog):
	def __init__(self, deck_name):
		super().__init__()
		# Basic setup
		self.deck_name = deck_name
		self.resize(720, 480)
		self.setMinimumSize(720, 480)

		# Widgets
		## Front & Back
		self.front_side = QGroupBox("Front")
		self.back_side = QGroupBox("Back")

		## Fields for showing image and note of the annoation
		self.text_side = QTextEdit()
		self.text_side.textChanged.connect(self.add_check)
		self.highlight_side = QLabel()
		self.highlight_side.setStyleSheet("background-color: #ffaa2d")
		self.highlight_side.setStyleSheet("qproperty-alignment: AlignLeft;")

		## Button which flips which side has the text and which the image
		self.btn_switch_sides = QPushButton("Switch Front/Back")
		self.btn_switch_sides.setCheckable(True)
		self.btn_switch_sides.setChecked(False)
		self.btn_switch_sides.clicked.connect(self.btn_switch_sides_clicked)

		## Buttons
		self.btn_add_card = QPushButton("Add Card")
		self.btn_add_card.clicked.connect(self.btn_add_card_clicked)

		self.btn_skip_card = QPushButton("Skip Card")
		self.btn_skip_card.clicked.connect(self.btn_skip_card_clicked)

		# Shows the first card
		self.refresh()

		# Layout
		self.main_layout = QGridLayout()
		self.front_side_layout = QHBoxLayout()
		self.scroll_front_side = QScrollArea()
		self.back_side_layout = QHBoxLayout()
		self.scroll_back_side = QScrollArea()
		self.button_layout = QHBoxLayout()

		## Put image and text into the correct boxes
		self.populate_sides(True)

		self.scroll_front_side.setWidgetResizable(True)
		self.scroll_back_side.setWidgetResizable(True)

		self.front_side_layout.addWidget(self.scroll_front_side)
		self.back_side_layout.addWidget(self.scroll_back_side)

		self.front_side.setLayout(self.front_side_layout)
		self.back_side.setLayout(self.back_side_layout)

		self.button_layout.addWidget(self.btn_add_card)
		self.button_layout.addWidget(self.btn_skip_card)

		# ==========
		# Layouts
		self.main_layout.addWidget(self.btn_switch_sides,0,0)
		self.main_layout.addWidget(self.front_side,1,0)
		self.main_layout.addWidget(self.back_side,2,0)
		self.main_layout.addLayout(self.button_layout,3,0)
		self.setLayout(self.main_layout)

	def refresh(self):
		'''Refresh layout and get a new card to display'''
		self.front = True
		self.card_front, self.card_back = parsePDF.get_next_card()
		if (type(self.card_front) is str and type(self.card_back) is not str) or (self.card_front == "" and type(self.card_back) is str):
			if self.card_front == "": self.btn_add_card.setDisabled(True)
			self.text_side.setPlainText(self.card_front)
			if parsePDF.get_export_type():
				fmt = QtGui.QImage.Format_RGBA8888 if self.card_back.alpha else QtGui.QImage.Format_RGB888
				image = QtGui.QImage(self.card_back.samples, self.card_back.width, self.card_back.height, self.card_back.stride, fmt)
				pixmap = QtGui.QPixmap(image)
				self.highlight_side.setPixmap(pixmap.scaled(self.highlight_side.size(), QtCore.Qt.KeepAspectRatio,QtCore.Qt.SmoothTransformation))
			else:
				if self.card_front == "":
					self.text_side.setPlainText(self.card_front)
					self.highlight_side.setText(self.card_back)
				else:
					if self.front:
						parseToAnki.add_card(self.card_front, self.card_back)
					else:
						parseToAnki.add_card(self.card_back, self.card_front)
					self.refresh()
		elif self.card_front is False:
			self.save_deck_clicked()
			parsePDF.reset_values_lite()
			self.close()
		elif self.card_front is None:
			self.refresh()
		else:
			if parsePDF.get_export_type():
				path1 = os.path.basename(parsePDF.save_picture_pix(self.card_front))
				path2 = os.path.basename(parsePDF.save_picture_pix(self.card_back))
				if self.front: parseToAnki.add_card('<img src="'+ path1 + '">', '<img src="'+path2+ '">')
				else: parseToAnki.add_card('<img src="'+ path2 + '">', '<img src="'+path1+ '">')
			else:
				if self.front:
					parseToAnki.add_card(self.card_front, self.card_back)
				else:
					parseToAnki.add_card(self.card_back, self.card_front)
			self.refresh()

	def populate_sides(self, first=False):
		''' Sets text_side and highlight_side to front or back'''
		if first:
			self.scroll_front_side.setWidget(self.text_side)
			self.scroll_back_side.setWidget(self.highlight_side)
		else:
			if self.front:
				self.text_side = self.scroll_back_side.takeWidget()
				self.highlight_side = self.scroll_front_side.takeWidget()

				self.scroll_front_side.setWidget(self.text_side)
				self.scroll_back_side.setWidget(self.highlight_side)
			else:
				self.text_side = self.scroll_front_side.takeWidget()
				self.highlight_side = self.scroll_back_side.takeWidget()

				self.scroll_front_side.setWidget(self.highlight_side)
				self.scroll_back_side.setWidget(self.text_side)

	def add_check(self):
		'''allows to add card only if there is text in QEditText'''
		if self.text_side.toPlainText() != '': self.btn_add_card.setDisabled(False)
		else: self.btn_add_card.setDisabled(True)

	# Buttons clicked
	def save_deck_clicked(self):
		'''Opens a dialog window and saves the deck to a selected location'''
		path, _ = QFileDialog.getSaveFileName(self,"",self.deck_name+".apkg")
		if path: parseToAnki.save_deck(path)

	def btn_switch_sides_clicked(self,pressed):
		'''Specifies orientation'''
		if pressed: self.front = False
		else: self.front = True
		self.populate_sides()

	def btn_add_card_clicked(self):
		'''Adds currently viewed data as a card'''
		if self.front:
			if parsePDF.get_export_type():
				a = os.path.basename(parsePDF.save_picture_pix(self.card_back))
				parseToAnki.add_card(self.text_side.toPlainText(), '<img src="'+a+ '">')
			else:
				parseToAnki.add_card(self.text_side.toPlainText(), self.card_back)
		else:
			if parsePDF.get_export_type():
				a = os.path.basename(save_picture_pix(self.card_back))
				parseToAnki.add_card('<img src="'+a+ '">', self.text_side.toPlainText())
			else:
				parseToAnki.add_card(self.card_back, self.text_side.toPlainText())
		self.refresh()

	def btn_skip_card_clicked(self):
		'''Doesn't add the currently viewed data as a card and skips to the next one'''
		self.refresh()

# Testing
if __name__ == '__main__':
	pass
