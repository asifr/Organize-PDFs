Organize-PDFs
=============

A python script that copies PDF files from a source directory into a destination directory and extracts pages as PNG images and fulltext.

The script is very barebones at the moment but functional.

Usage
=====

	python ./organizepdfs.py ~/source ~/destination

The source directory contains the PDF files you want to move. The destination directory should look like this:

	.
	|-- /images
	|-- /pdfs
	|-- /text

The original PDFs will be copied to the `/pdfs` directory. Each page of a PDF will be converted into a small 500px width PNG image and saved to the `/images` directory with the page number appended to the file name. The fulltext will also be extracted and saved as `.txt` files in `/text`.

Requirements
============

There are several dependencies including:

GraphicsMagick:

	[aptitude | port | brew] install graphicsmagick

Ghostscript:

	[aptitude | port | brew] install ghostscript