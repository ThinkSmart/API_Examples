# Initiate_Template.py
# written and tested in Python 3.6.0
# last updated 07/05/17

"""
This script initiates workflows using field data from a CSV file. The first
row of the CSV should contain field names, and subsequest rows should hold 
field values (each row will be a separate instance of the workflow). The script
creates a new txt file (in the same directory as main.py) each time it is run, 
and writes the result of each workflow instance, including error messages.

To use, create a workflow (don't change field names, i.e. element1), create a 
CSV based on the workflow, and update the global vars below. If you find bugs
or errors that are not handled, please send them to cpierce@thinksmart.com
"""

import getpass
import time
import os
import sys
import json
from Initiate_Functions import *
import csv

# global vars
url_root = 'https://default.tap.thinksmart.com/prod/'
username = input("Enter your TAP username: ")
password = getpass.getpass()
client_id = 'b858d97c24124c959ec0d78f3eccd77d'
client_secret = '0WDF4cRc4gtEEhOBXkCH6dTj1NU18L8iL6+i3jHXoR4='
workflow_name = 'InitiateTest'
csv_name = 'TestFields.csv'

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

# get template ID response
r = getTemplateID(url_root, workflow_name, token)
# invalid workflow_name causes empty list value for 'Items' key in response dict
if (not json.loads(r.text).get('Items')):
	f.write("Invalid workflow_name")
	sys.exit()
# decode JSON, get ID
template_id = json.loads(r.text).get('Items')[0].get('ID')

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
	f.write("Please use a .csv with UTF-8 encoding.\n" +
					"In Sublime Text 3: File -> Save with Encoding -> UTF-8")
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
if (not csv_unused) and (not accepted_unused):
	f.write("All field names from {} and {} match\n\n"
					.format(csv_name, workflow_name))
elif (not accepted_unused):
	f.write("Field names from {} that do not match {}: {}\n\n"
					.format(csv_name, workflow_name, csv_unused))
elif (not csv_unused):
	f.write("Field names from {} that do not match {}: {}\n\n"
					.format(workflow_name, csv_name, accepted_unused))
else:
	f.write("Field names from {} that do not match {}: {}\n"
					.format(csv_name, workflow_name, csv_unused))
	f.write("Field names from {} that do not match {}: {}\n\n"
				.format(workflow_name, csv_name, accepted_unused))

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
	r = createWorkflow(url_root, template_id, token, body)
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
