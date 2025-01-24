# Highlighted-2021

The app allows you to use the annotation of a PDF document to automatically generate cards for Anki. Annotations can be selected by type and color. It also allows annotations to be extracted as images or annotation text to isolate information from the document. 

## Requirements
Python 3.8.8
Highlighted uses following modules:
- PyMuPDF
- genanki
- pyQt5


This app was tested only on macOS with intel and M1. It should work on other platforms; this however cannot be guaranteed. M1 seems to have a problem with native installation of some of the required packages. Installing modules and using the app inside an anaconda environment works, since anaconda itself is not yet native to M1 and seems to run using Rosetta 2.


![](Images/main_window_empty.png)

![](Images/main_window_korean.png)

![](Images/add_info_window_korean.png)

![](Images/anki_image.png)

![](Images/anki_text.png)

## Pairings

![](Images/create_deck_paired_korean.png)
![](Images/digest_korean.png)

## From PDF to ANKI

![](Images/chinese_pdf.png)

![](Images/chinese_anki.png)

## From PDF to ANKI

![](Images/lina_pdf.png)

![](Images/lina_anki.png)
