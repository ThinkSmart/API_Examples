# initTemplate.py
# written and tested in Python 3.6.0
# last updated 07/28/17

"""
This script initiates workflows using field data from a CSV file. The first
row of the CSV should contain field labels, and all other rows should hold 
field values (each row will be a separate instance of the workflow). The script
creates a new txt file (in the same directory as this file) each time it is run, 
and writes the result of each workflow instance, including error messages.

To use, create a workflow, create a CSV based on the workflow, and update the 
global variables below. If you find bugs or errors that are not handled, 
please send them to cpierce@thinksmart.com
"""

import getpass
import time
import os
import sys
import json
from resource_owner import *
import csv
from collections import defaultdict

# ---------------- #
# Global Variables #
# ---------------- #

# replace tenant with your own
url_root = 'https://tenant.tap.thinksmart.com/prod/'
# fill in (must be strings)
client_id = ''
client_secret = ''
workflow_name = ''
csv_name = ''
# enter username and password in command line during runtime
username = input("Username: ")
password = getpass.getpass()

# ---------------------------- #
# Start Timer, Create txt File #
# ---------------------------- #

# get start time
t0 = time.time()

# find name for new txt file
i = 0
while os.path.exists('{}{}.txt'.format(workflow_name, i)):
	i += 1

# create txt file, write header
f = open('{}{}.txt'.format(workflow_name, i), 'w')
f.write(time.asctime() + "\n\n")
f.write("Submitting {} with field values from {}...\n\n"
				.format(workflow_name, csv_name))

# --------- #
# Get Token #
# --------- #

# get token response
r = getToken(url_root, username, password, client_id, client_secret)

# invalid url_root causes 404 response
if (str(r) == '<Response [404]>'):
	f.write("Invalid url_root")
	sys.exit()
elif (str(r) == '<Response [400]>'):
	# invalid user credentials or client info causes 400 response
	if (json.loads(r.text).get('error') == 'invalid_grant'):
		f.write("Invalid username or password")
	else:
		f.write("Invalid client_id or client_secret")
	sys.exit()

# decode JSON, get token
token = json.loads(r.text).get('access_token')

# --------------- #
# Get Template ID #
# --------------- #

# get template ID response
r = getTemplateID(url_root, token)

# search for template
template_id = None
for w in json.loads(r.text).get('Items'):
	if (w.get('WorkflowName') == workflow_name):
		template_id = w.get('ID')
		break

# if template not found, report error
if (not template_id):
	f.write("Invalid workflow_name (has a field been added to the repository?)")
	sys.exit()

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
except UnicodeDecodeError as e:
	f.write("Please use a .csv with UTF-8 encoding.")
	sys.exit()

# ----------------------------- #
# Convert Field Labels to Names #
# ----------------------------- #

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
# use a while loop here, because popping labels inside for loop will skip some
while (i < len(csv_labels)):
	# v = value for key from csv_labels, False if not present
	v = d.get(csv_labels[i], False)
	# if v is True (k is False if key not present, OR list empty)
	if (v):
		# append now-validated name and label to lists
		labels.append("{} ({})".format(csv_labels.pop(i), v[0]))
		names.append(v.pop(0))
	else:
		i += 1

# gather remaining fields from d
remainder = []
# for each key, if value list is not empty...
for k, v in d.items():
	if (v):
		# if value has multiple values, put list in parens
		if (len(v) > 1):
			remainder.append("{} ({})".format(k, ", ".join(v)))
		# else put single value in parens
		else:
			remainder.append("{} ({})".format(k, v[0]))

# report on comparison
mismatch = "Labels from {} that do not match {}:\n{}\n\n"
if ((not csv_labels) and (not remainder)):
	f.write("All field names from {} and {} match\n\n"
					.format(csv_name, workflow_name))
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
	if ((time.time()-t0) > 3600):
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
	if (str(r) == '<Response [400]>'):
		f.write("Row {}: Error\n".format(row))
		f.write("------------" + "\n")
		f.write(str(r.text) + "\n\n")
	else:
		f.write("Row {}: Submitted\n".format(row))
		f.write("----------------" + "\n")
		for i, val in enumerate(body):
			f.write("{} : {}\n".format(labels[i], body[val]))
		f.write("\n")
		submit_count += 1

# report on submits and errors, time
f.write("{} submitted on {} of {} tries\n"
				.format(workflow_name, submit_count, row-1))
f.write("Time elapsed: {}s".format(round(time.time()-t0, 3)))
