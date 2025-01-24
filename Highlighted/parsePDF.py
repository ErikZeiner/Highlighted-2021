import fitz, os, parseToAnki
from collections import Counter
from math import trunc
from operator import attrgetter

# Translate between highlight names and indexes
annotation_types = {8 : "HIGHLIGHT", 9 : "UNDERLINE", 10 : "SQUIGGLY"}
types_annotation = {"HIGHLIGHT": 8 , "UNDERLINE" : 9 , "SQUIGGLY" : 10}

document = None	# Contains the document; used in all parsing functions
min_parse = 0	# Min and Max pages; these set the range for parsing outside of the main window, where they are set
max_parse = 0

image_export = True	# Determines whether the annotations are exported as an image or text
image_export_colour = False # . whether the annotations have highlighted colour in anki

pages_list = [] # list of page annotations objects, used to store pages and
annotations_list = [] # Used to store info about all annotations in one list

class page_annotations():
	''' Used in pages_list to store page and index which indicates the last index of annot which belongs to that page'''
	def __init__(self,page):
		global annotations_list
		super().__init__()
		self.page = page
		self.annot_index = len(annotations_list)
		annotations_list.extend([0]*len(list(filtered_annots(page))))

	def __str__(self):
		'''for priniting while testing'''
		global annotations_list
		s = ""
		for i in range(self.annot_index, self.annot_index + len(list(filtered_annots(self.page)))):
			s += str(annotations_list[i]) + ", "
		return str(str(self.page) + "\n" + s)

	def length(self):
		''' number of annotations on a page'''
		return len(list(filtered_annots(self.page)))

	def get_annot(self,index):
		'''Index is the index inside annotations_list'''
		annotations = annot_sort(filtered_annots(self.page))
		return annotations[index]


def filtered_annots(page):
	''' Returns only annotation types: highlight, underline and squiggly'''
	filtered = [annot for annot in page.annots() if annot.type[0] in (8,9,10)]
	return filtered

def mark_annotations(enabled, paired):
	'''Assigns 1 or single number and assigns the same number to pairs, 0 are not enabled'''
	global annotations_list
	pairing_index = 2
	for index in range(len(annotations_list)):
		colour = get_annot_data_string(get_annot(index))
		if colour in enabled and annotations_list[index] == 0:
			annotations_list[index] = 1
			if colour in paired.keys():
				if index < len(annotations_list) - 1:
					if paired[colour] == get_annot_data_string(get_annot(index+1)):
						annotations_list[index], annotations_list[index+1] = pairing_index, pairing_index
						pairing_index += 1
				elif index > 0:
					if paired[colour] == get_annot_data_string(get_annot(index-1)):
						annotations_list[index], annotations_list[index-1] = pairing_index, pairing_index
						pairing_index += 1

def get_next_card():
	'''Used in addinfowindow to get the next annotation. When annotations are used they are labeled as such by changing the index to be negative.
	Returns annotations as images as well as text.'''
	global annotations_list, pages_list
	try:
		current_index = next(x for x,y in enumerate(annotations_list) if y > 0)
		if annotations_list[current_index] > 1 and annotations_list[current_index+1] == annotations_list[current_index]:
				if image_export:
					front = parse_as_picture(current_index)
					back = parse_as_picture(current_index+1)
				else:
					front = parse_as_text(current_index)
					back = parse_as_text(current_index+1)
				annotations_list[current_index] = -annotations_list[current_index]
				annotations_list[current_index+1] = -annotations_list[current_index+1]
				return front, back
		else:
			text = get_annot(current_index).info['content']
			if image_export:
				highlight = parse_as_picture(current_index)
			else:
				highlight = parse_as_text(current_index)
			annotations_list[current_index] = -annotations_list[current_index]
			return text, highlight
	except StopIteration:
		return False, False
	except:
		return None, None

def annot_sort(annots):
	'''Uses coordinates of the annotations to sort it in order on the page; otherwise it is sorted by date created'''
	annots_list = list(annots)
	return sorted(annots_list, key=lambda x: (x.rect.y0, x.rect.x0,x.rect.y1,x.rect.x1))

def load_page_annotations():
	'''Fills pages_list with page_annotations from the document within range, this also populates annotation_list to the correct length with zeros'''
	global min_parse, max_parse,pages_list
	for page_num in range(min_parse-1,max_parse):
		pages_list.append(page_annotations(document.load_page(page_num)))

def document_page(page_num):
	'''Returns a pixmap of the whole page'''
	global document
	if document:
		if page_num <= document.page_count:
			page = document.load_page(page_num)
			# Set resolution for Picture Mode
			zoom = 2
			mat = fitz.Matrix(zoom, zoom)
			#Create a pixmap with the size of the rect around an annot
			return page.get_pixmap(matrix=mat, clip=page.rect)
	else:
		return None

def max_document_page():
	''' Returns the maximum page number in the document'''
	global document
	if document: return document.page_count
	else: return 0

def load_document(file_name):
	''' Load a document to a variable which is used in other functions'''
	global document
	document = fitz.open(file_name)

# Getters/Setters
def get_page_index(index):
	global pages_list
	for page_annotation in pages_list:
		if index in range(page_annotation.annot_index,page_annotation.annot_index+ page_annotation.length()):
			return page_annotation
	return None

def get_annot_and_page(index):
	page_annotation = get_page_index(index)
	inner_index = index - page_annotation.annot_index
	return page_annotation.page, page_annotation.get_annot(inner_index)

def get_annot(index):
	page = get_page_index(index)
	inner_index = index - page.annot_index
	return page.get_annot(inner_index)
# ---
def get_annot_colour(annot):
	'''Returns hex colour value'''
	rgb = [trunc(x * 255) for x in annot.colors["stroke"]]
	return '#{:02x}{:02x}{:02x}'.format(rgb[0],rgb[1],rgb[2])

def get_annot_data_string(annot):
	'''Returns string in format X#000000, where X is 8,9,10 and rest is hex colour value'''
	return '%s%s' %(annot.type[0], get_annot_colour(annot))
# ---
def get_min_parse():
	global min_parse
	return min_parse

def set_min_parse(min):
	global min_parse
	min_parse = min

def get_max_parse():
	global max_parse
	return max_parse

def set_max_parse(max):
	global max_parse
	max_parse = max

def get_export_type():
	global image_export
	return image_export

def set_export_type(state):
	global image_export
	image_export = state

def get_export_colour():
	global image_export_colour
	return image_export_colour

def set_export_colour(state):
	global image_export_colour
	image_export_colour = state

def get_document():
	global document
	return document

# Parsing
def page_range_parse(min, max):
	'''return data like in overview_parse but from pages in a given range'''
	global document
	if document:
		data = dict()
		for page_num in range(min-1,max):
			page = document.load_page(page_num)
			for annot in page.annots():
				if annot.type[0] in (8, 9, 10):
					data.setdefault(annotation_types[annot.type[0]], [])
					data[annotation_types[annot.type[0]]].append(get_annot_colour(annot))
		for key in data.keys():
			data[key] = dict(Counter(item for item in data[key]))
		return data
	return None

def overview_parse():
	''' Returns types of annotations, used colours and number of each colour.
	Dictionary: key is annotation type value is Dictionary: key is annotation string and value is number of that kind of annotation'''
	global document
	if document:
		data = dict()
		for page_num in range(document.page_count):
			page = document.load_page(page_num)
			for annot in page.annots():
				if annot.type[0] in (8, 9, 10):
					data.setdefault(annotation_types[annot.type[0]], [])
					data[annotation_types[annot.type[0]]].append(get_annot_colour(annot))
		for key in data.keys():
			data[key] = dict(Counter(item for item in data[key]))
		return data

	return None
# Pictures
def parse_as_picture(index):
	''' Creates a rectangle image around each annotation and saves jpgs'''
	global image_export_colour
	# Set resolution for Picture Mode
	zoom = 2
	mat = fitz.Matrix(zoom, zoom)
	annot = get_annot(index)
	#Create a pixmap with the size of the rect around an annot
	return annot.parent.get_pixmap(matrix=mat, clip=annot.rect, annots = image_export_colour)

def parse_as_picture2(annot):
	''' Creates a rectangle image around each annotation and saves jpgs'''
	global image_export_colour
	# Set resolution for Picture Mode
	zoom = 2
	mat = fitz.Matrix(zoom, zoom)
	#Create a pixmap with the size of the rect around an annot
	return annot.parent.get_pixmap(matrix=mat, clip=annot.rect, annots = image_export_colour)

def save_picture(annot, path, page_num, annot_num):
	'''Saves picture as jpg.'''
	pix = parse_as_picture2(annot)
	output = path + "/"+ os.path.basename(document.name)[:-4] + "_page"+str(page_num)+"num"+str(annot_num) + ".jpg"
	pix.writeImage(output)
	return output

def save_picture_pix(pix):
	''''Saves picture as jpg.'''
	output = "images/" + os.path.basename(document.name)[:-4] + "_" + str(parseToAnki.random_id())+ ".jpg"
	pix.writeImage(output)
	return output

# Texts
def parse_as_text(index):
	''' Extracts the text from each annotation'''
	page, annot = get_annot_and_page(index)
	rect = annot.rect
	words = page.get_text("words")
	mywords = [w for w in words if fitz.Rect(w[:4]).intersects(rect)]
	text = make_text(mywords)
	return (text)

def parse_as_text2(page,annot):
	''' Extracts the text from each annotation'''
	rect = annot.rect
	words = page.get_text("words")
	mywords = [w for w in words if fitz.Rect(w[:4]).intersects(rect)]
	text = make_text(mywords)
	return (text)

def make_text(words):
	""" Function taken from https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/textbox-extraction/textbox-extract-1.py
	Return textstring output of get_text("words").
	Word items are sorted for reading sequence left to right,
	top to bottom.
	"""
	line_dict = {}
	words.sort(key=lambda w: w[0])
	for w in words:
		y1 = round(w[3], 1)
		word = w[4]
		line = line_dict.get(y1, [])
		line.append(word)
		line_dict[y1] = line
	lines = list(line_dict.items())
	lines.sort()
	return "\n".join([" ".join(line[1]) for line in lines])

def reset_values():
	''' Sets all document values to default.'''
	global document, min_parse, max_parse, image_export, pages_list, annotations_list, image_export_colour
	if document is not None: document.close()
	document = None
	min_parse = 0
	max_parse = 0

	image_export = True
	image_export_colour = False

	pages_list = []
	annotations_list = []
	
def reset_values_lite():
	''' Resets values necessary for next parse from the same document.'''
	global image_export, pages_list, annotations_list, image_export_colour
	image_export = True
	image_export_colour = False
	pages_list = []
	annotations_list = []
	
#Testing
if __name__ == '__main__':
	pass
	