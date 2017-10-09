# bulk_initiate.py
# written and tested in Python 3.6.2
# last updated 10/02/17

"""
This script initiates workflows using data from a CSV file. The first row of 
the CSV should contain field labels, and all other rows should hold field 
values (each row will be a separate instance of the workflow). The script
creates a txt file (in same directory as this) each time it is run, and writes
the result of each workflow instance, including error messages.

To use, create a workflow, create a CSV based on the workflow, and update the 
global variables below. If you find bugs or errors that are not handled, 
please send them to cpierce@thinksmart.com
"""

import getpass
import time
import os
import sys
from bulk_functions import *
import json
import csv
from collections import defaultdict

# ---------------- #
# Global Variables #
# ---------------- #

# replace tenant, environment, and instance with your own
url_root = 'https://tenant.environment.thinksmart.com/instance/'
# fill in (must be strings)
client_id = ''
client_secret = ''
workflow_name = ''
csv_name = ''
# enter username and password in command line during runtime
username = input("Username: ")
password = getpass.getpass()

# -------------------------- #
# Start Timer, Create Report #
# -------------------------- #

# get start time
t0 = time.time()

# find name for new txt file
i = 0
while os.path.exists('{}{}.txt'.format(workflow_name, i)):
	i += 1

# create txt file, write timestamp
f = open('{}{}.txt'.format(workflow_name, i), 'w')
f.write(time.asctime() + "\n\n")

# --------- #
# Get Token #
# --------- #

# get time of first token (valid 3600 seconds)
token_timer = time.time()

# get token response
r = getToken(url_root, username, password, client_id, client_secret)

# invalid url_root causes 404 response
if (r.status_code == 404):
	f.write("Invalid url_root")
	sys.exit()
# invalid user credentials or client info causes 400 response
elif (r.status_code == 400):
	if (json.loads(r.text).get('error') == 'invalid_grant'):
		f.write("Invalid Username and/or Password.")
	elif (json.loads(r.text).get('error') == 'unauthorized_client'):
		f.write("Valid client_id and client_secret, invalid authentication flow.")
	else:
		f.write("Invalid client_id and/or client_secret.")
	sys.exit()

# decode JSON, get token
token = json.loads(r.text).get('access_token')

# --------------- #
# Get Template ID #
# --------------- #

# get template ID response
r = getTemplateID(url_root, workflow_name, token)

# parse to where ID should be
temp = json.loads(r.text).get('Items')

# if empty in that location, write and exit
if (not temp):
	f.write("Invalid workflow_name. This may occur when {} {}"
		.format("the name contains non-alphabetic characters or",
			"none of the workflow fields have been added to the repository."))
	sys.exit()
# else assign it
else:
	template_id = temp[0].get('ID')

# -------- #
# Read CSV #
# -------- #

# open CSV
try:
	readable = open(csv_name, 'r')
# invalid csv_name causes FileNotFoundError
except FileNotFoundError:
	f.write("Invalid csv_name")
	sys.exit()

# create iterable with CSV
csv_fields = csv.reader(readable)
# assign first row of iterable to csv_labels
try:
	csv_labels = next(csv_fields)
# encoding may cause UnicodeDecodeError
except UnicodeDecodeError:
	f.write("Please use a .csv with UTF-8 encoding.")
	sys.exit()

# ----------------------------- #
# Convert Field Labels to Names #
# ----------------------------- #

# features to add here:
	# accept names and labels
	# accept labels that meet word-similarity threshold (in event of typo)

# get form info from workflow
r = getFormInfo(url_root, template_id, token)

# get field info, use to create dict of label:name pairs
form_fields = json.loads(r.text).get('FormFields')
# fields that take no input from user
non_input = ['heading', 'static-text', 'static-html']
# if assigning value to non-existent key, put value in list
d = defaultdict(list)
# for each field, if it takes input, add it to d
for field in form_fields:
	if (field.get('FieldType') not in non_input):
		d[field.get('Label')].append(field.get('Name'))

# hold labels and names that are validated with d
labels, names = [], []
i = 0
# use a while loop b/c popping labels inside for loop will skip some
while (i < len(csv_labels)):
	# v = value for key from csv_labels
	v = d.get(csv_labels[i], False)
	# if v is True (is False if key not present)
	if (v):
		current = csv_labels.pop(i)
		# append now-validated name and label to lists
		labels.append("{} ({})".format(current, v[0]))
		names.append(v.pop(0))
		# if v is empty, pop key (lower time complexity w/ for loop below)
		if (len(v) == 0):
			d.pop(current)
	else:
		i += 1

# gather remaining fields from d
remainder = []
# for each remaining key...
for k, v in d.items():
	# if value has multiple values, put list in parens
	if (len(v) > 1):
		remainder.append("{} ({})".format(k, ", ".join(v)))
	# else put single value in parens
	else:
		remainder.append("{} ({})".format(k, v[0]))

# report on comparison
mismatch = "Labels from {} that do not match {}:\n{}\n\n"
if ((not remainder) and (not csv_labels)):
	pass
elif (not remainder):
	f.write(mismatch.format(csv_name, workflow_name, "\n".join(csv_labels)))
elif (not csv_labels):
	f.write(mismatch.format(workflow_name, csv_name, "\n".join(remainder)))
else:
	f.write(mismatch.format(csv_name, workflow_name, "\n".join(csv_labels)))
	f.write(mismatch.format(workflow_name, csv_name, "\n".join(remainder)))

# ------------------ #
# Initiate Workflows #
# ------------------ #

# count var for reporting
submit_count = 0

# for rows below first, construct body and make API call
for row, field_vals in enumerate(csv_fields, 2):

	# refresh token if needed
	if ((time.time()-token_timer) > 3500):
		token_timer = time.time()
		r = getToken(url_root, username, password, client_id, client_secret)
		token = json.loads(r.text).get('access_token')

	# clear body
	body = {}
	# fill body
	for i in range(min(len(names), len(field_vals))):
		body[names[i]] = field_vals[i]
	# initiate workflow
	r = initiateWorkflow(url_root, template_id, token, body)
	# empty required field, unmatched dropdown value, etc. causes 400 response
	if (r.status_code == 400):
		f.write("{0}\nRow {1}: Error\n{0}\n".format("-"*(len(str(row))+11),row))
		f.write("{}\n\n".format(r.text))
	else:
		f.write("{0}\nRow {1}: Submitted\n{0}\n".format("-"*(len(str(row))+15),row))
		for i, val in enumerate(body):
			f.write("{} : {}\n".format(labels[i], body[val]))
		f.write("\n")
		submit_count += 1

# report on submits and errors, time
f.write("{} submitted on {} of {} tries\n"
	.format(workflow_name, submit_count, row-1))
f.write("Time elapsed: {}s".format(round(time.time()-t0, 3)))
