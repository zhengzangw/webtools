# NJU grade achiever

A script for quickly achieve grades from NJU eas.

## Prerequisite

You need to install: python3, requests, bs4, matplotlib, pytesseract(with tesseract and English package) to run this script

## Usage

Set your student id and password in nju.py. If you want to enter the valicode by your self, use

`python nju.py -m`

If you want to automatically achieve the grade, just use

`python nju.py`

Your grades summary (such as GPA for each year) will appear in your terminal and grades for each subject is stored in grade.json.