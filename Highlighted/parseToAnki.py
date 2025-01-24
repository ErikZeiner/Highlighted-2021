from genanki import *
from random import randrange
import os, parsePDF

deck = None

def random_id():
	'''generates a random number'''
	return randrange(1 << 30, 1 << 31)

def create_deck(name):
	'''Creates an empty deck'''
	global deck
	deck = Deck(random_id(),name)

def get_deck():
	return deck

def save_deck(file_path):
	''' Adds images from /images to media_files, deletes them from the dir and saves .apkg file'''
	global deck
	package = Package(deck)
	for f in os.listdir('images/'):
		p = os.path.basename(f)
		if p[-3:]=="jpg":
			path = 'images/'+ p
			package.media_files.append(path)
	package.write_to_file(str(file_path))
	for f in os.listdir('images/'):
		os.remove('images/'+f)


def add_card(front, back):
	'''Adds a card to deck'''
	global deck
	note = Note(model=model,fields=[front, back])
	deck.add_note(note)

	
model = Model(
	1238852258,
	'Highlights Model',
	fields=[
		{'name': 'Front'},
		{'name': 'Back'},
	],
	templates=[
		{
			'name': 'Card 1',
			'qfmt': '{{Front}}',
			'afmt': '{{Front}}<hr id="answer">{{Back}}',
			'tags': 'sadfksdf,dfksdlfjlf'
		},
	],
	css = ".card {font-family: arial; font-size: 20px; text-align: center; color: black;background-color: white;}"
)


# Testing
if __name__ == '__main__':
	pass
