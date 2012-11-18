#!/usr/bin/env python

import sys
import os
import re
import shutil
from pipes import quote
from datetime import datetime

def get_pdfs(directory):
	pdfs = [os.path.abspath(directory + '/' + f) for f in os.listdir(directory) if f.endswith('.pdf')]
	return pdfs

def contains_text(pdfs):
	needs_ocr = []
	for f in pdfs:
		p = os.popen('pdffonts %s 2>&1' % quote(f))
		o = p.readline()
		needs_ocr.append(re.match('name',o) == None)
		p.close()
	return needs_ocr

def pdf_info(pdfs, meta):
	matchers = {
		'author'	:	'^Author:\s+([^\n]+)',
		'date'		:	'^CreationDate:\s+([^\n]+)',
		'creator'	:	'^Creator:\s+([^\n]+)',
		'keywords'	:	'^Keywords:\s+([^\n]+)',
		'producer'	:	'^Producer:\s+([^\n]+)',
		'subject'	:	'^Subject:\s+([^\n]+)',
		'title'		:	'^Title:\s+([^\n]+)',
		'length'	:	'^Pages:\s+([^\n]+)'
    }
	pages = []
	fn = 0
	for f in pdfs:
		p = os.popen('pdfinfo %s 2>&1' % quote(f))
		o = p.readlines()
		if len(o) > 0:
			for i in range(0, len(o)):
				match = re.search(matchers[meta],o[i])
				if match != None:
					pages.append(match.group(1))
		p.close()
		fn = fn+1
		if len(pages) < fn:
			pages.append(None)
	return pages

def extract_text(pdfs, output_path):
	pdf_names = [os.path.splitext(os.path.basename(f))[0] for f in pdfs]
	needs_ocr = contains_text(pdfs)
	i = 0
	for f in pdfs:
		if needs_ocr[i] == False:
			text_path = os.path.abspath(os.path.join(output_path, 'text', pdf_names[i] + '.txt'))
			os.popen('pdftotext -enc UTF-8 %s %s 2>&1' % (quote(pdfs[i]), quote(text_path))).close()
		else:
			print '%s needs OCR to extract text' % pdf_names[i]
		i = i+1

def extract_images(pdfs, output_path):
	tmpdir = '/tmp'
	pdf_names = [os.path.splitext(os.path.basename(f))[0] for f in pdfs]
	pdf_lengths = pdf_info(pdfs,'length')
	i = 0
	for f in pdfs:
		if pdf_lengths[i] != None:
			for page in range(0,int(pdf_lengths[i])):
				image_path = os.path.abspath(os.path.join(output_path, 'images', pdf_names[i] + '-' + str(page) + '.png'))
				p = os.popen('MAGICK_TMPDIR=%s OMP_NUM_THREADS=2 gm convert +adjoin -limit memory 256MiB -limit map 512MiB -density 150 -resize 500 -quality 100 %s[%i] %s 2>&1' % (tmpdir, quote(pdfs[i]), page, quote(image_path)))
				p.close()
		i = i+1

def copy_originals(pdfs, output_path):
	existing_pdfs = get_pdfs(os.path.join(output_path, 'pdfs'))
	pdf_names = [os.path.splitext(os.path.basename(f))[0] for f in pdfs]
	i = 0;
	for f in pdfs:
		if any(os.path.splitext(os.path.basename(f))[0] in os.path.splitext(os.path.basename(s))[0] for s in existing_pdfs) == False:
			pdf_path = os.path.abspath(os.path.join(output_path, 'pdfs', pdf_names[i] + '.pdf'))
			shutil.copy2(pdfs[i],pdf_path)
		else:
			pdf_path = os.path.abspath(os.path.join(output_path, 'pdfs', pdf_names[i] + '-m' + str(datetime.now().month) + 'd' + str(datetime.now().day) + '.pdf'))
			shutil.copy2(pdfs[i],pdf_path)
		i = i+1;

if __name__ == '__main__':
	if len(sys.argv) > 2:
		pdfs = get_pdfs(sys.argv[1])
		copy_originals(pdfs, sys.argv[2])
		extract_text(pdfs, sys.argv[2])
		extract_images(pdfs, sys.argv[2])
	else:
		print 'Usage: python ./organizepdfs.py source destination'