# Initiate_Template.py
# written and tested in Python 3.6.0
# last updated 07/07/17

"""
This script initiates workflows using field data from a CSV file. The first
row of the CSV should contain field names, and all other rows should hold 
field values (each row will be a separate instance of the workflow). The script
creates a new txt file (in the same directory as this file) each time it is run, 
and writes the result of each workflow instance, including error messages.

To use, create a workflow (don't change field names, i.e. element1), create a 
CSV based on the workflow, and update the global variables below. If you find
bugs or errors that are not handled, please send them to cpierce@thinksmart.com
"""

import getpass
import time
import os
import sys
import json
from Initiate_Functions import *
import csv

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
username = input("Enter your TAP username: ")
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
r = getTemplateID(url_root, workflow_name, token)
# invalid workflow_name causes empty list value for 'Items' key in response dict
if (not json.loads(r.text).get('Items')):
	f.write("Invalid workflow_name")
	sys.exit()
# decode JSON, get ID
template_id = json.loads(r.text).get('Items')[0].get('ID')

# -------- #
# Read CSV #
# -------- #

# open CSV
try:
	readable = open(csv_name, 'r', encoding='utf-8')
# invalid csv_name causes FileNotFoundError
except FileNotFoundError:
	f.write("Invalid csv_name")
	sys.exit()

# create iterable with CSV
csv_fields = csv.reader(readable)
# assign first row of iterable to field_names
try:
	field_names = next(csv_fields)
# encoding may cause UnicodeDecodeError
except UnicodeDecodeError as e:
	f.write("Please use a .csv with UTF-8 encoding.")
	sys.exit()

# make list of field names from workflow for comparison
r = getFormInfo(url_root, template_id, token)
accepted_names = []
for form_field in json.loads(r.text).get("FormFields"):
	accepted_names.append(form_field.get("Name"))

# compare field names
csv_unused = set(field_names).difference(accepted_names)
accepted_unused = set(accepted_names).difference(field_names)

# report on comparison
mismatch = "Field names from {} that do not match {}: {}\n\n"
if ((not csv_unused) and (not accepted_unused)):
	f.write("All field names from {} and {} match\n\n"
					.format(csv_name, workflow_name))
elif (not accepted_unused):
	f.write(mismatch.format(csv_name, workflow_name, csv_unused))
elif (not csv_unused):
	f.write(mismatch.format(workflow_name, csv_name, accepted_unused))
else:
	f.write(mismatch.format(csv_name, workflow_name, csv_unused))
	f.write(mismatch.format(workflow_name, csv_name, accepted_unused))

# ------------------ #
# Initiate Workflows #
# ------------------ #

# count var for reporting
submit_count = 0
# for remaining rows, construct body and make API call
for index, field_vals in enumerate(csv_fields, 2):
	# refresh token if needed
	if ((time.time()-t0) > 3600):
		r = getToken(url_root, username, password, client_id, client_secret)
		token = json.loads(r.text).get('access_token')
	# clear body
	body = {}
	# fill body
	for i in range(len(field_names)):
		body[field_names[i]] = field_vals[i]
	# initiate workflow
	r = initiateWorkflow(url_root, template_id, token, body)
	# empty required field, unmatched dropdown value, etc. causes 400 response
	if (str(r) == '<Response [400]>'):
		f.write("Row {}: Error\n".format(index))
		f.write("------------" + "\n")
		f.write(str(r.text) + "\n\n")
	else:
		f.write("Row {}: Submitted\n".format(index))
		f.write("----------------" + "\n")
		for name, val in body.items():
			f.write("{} : {}\n".format(name, val))
		f.write("\n")
		submit_count += 1

# report on submits and errors, time
f.write("{} submitted on {} of {} tries\n"
				.format(workflow_name, submit_count, index-1))
f.write("Time elapsed: {}s".format(round(time.time()-t0, 3)))
