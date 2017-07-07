# Example2.py
# Implicit Flow
# written and tested in Python 3.6.0
# last updated 07/07/17

import webbrowser
import requests
import json
import time

# ---------------- #
# Global Variables #
# ---------------- #

# replace tenant with your own
url_root = 'https://tenant.tap.thinksmart.com/prod/'
# fill in (must be strings)
client_id = ''
redirect_uri = ''
workflow_name = ''

# --------- #
# Functions #
# --------- #

def getBrowser(url_root, client_id, redirect_uri):
	"""
	Given: URL root, client ID, and redirect URI.
	Return: None, opens browser for user to enter credentials.
	"""

	# construct URL
	url = ('{}auth/identity/connect/authorize?client_id={}&scope=api&response_type=token&redirect_uri={}'
					.format(url_root, client_id, redirect_uri))

	# open browser
	webbrowser.open_new(url)

def getTemplateID(url_root, workflow_name, token):
	"""
	Given: URL root, name of workflow, and valid token.
	Return: Template ID of workflow.
	"""

	# construct URL
	# workflow_name must be quoted, e.g. ?$filter=WorkflowName eq 'Test'
	url = ("{}api/v1/templates/dashboard?$filter=WorkflowName eq '{}'"
					.format(url_root, workflow_name))

	# needs token
	headers = {'Authorization' : 'Bearer {}'.format(token)}

	# make API call
	r = requests.get(url, headers=headers)

	# parse GET call response, return template ID
	return json.loads(r.text).get('Items')[0].get('ID')

def initiateWorkflow(url_root, template_id, token, body):
	"""
	Given: URL root, ID of workflow, valid token, and field names and values.
	Return: None, makes POST call to initiate workflow.
	"""
	
	# construct URL
	url = '{}api/v1/workflows/{}/form'.format(url_root, template_id)

	# needs token
	headers = {'Authorization' : 'Bearer {}'.format(token),
							'Content-Type' : 'application/json'}

	# encode body into JSON
	json_body = json.dumps(body)

	# make API call
	requests.post(url, headers=headers, data=json_body)

# -------------- #
# Function Calls #
# -------------- #

# give info
print("In a few seconds, a tab in your browser will open. " +
			"Please enter your TAP credentials, then copy and paste " +
			"the URL of the redirect page into the space below.")
# delay
time.sleep(3)

# open browser, take URL as input, parse for token
getBrowser(url_root, client_id, redirect_uri)
redirect = input("URL of redirect page: ")
# the parsing here works with redirect_uri = 'https://google.com'
token = redirect.split('token=')[1].split('&')[0]

# get template ID
template_id = getTemplateID(url_root, workflow_name, token)

# a dictionary is used to fill fields in the workflow
# keys are field names, values are field values
# below is an example of what it may look like
body = {"element1": "Hello", "element2": "World"}

# initiate workflow
initiateWorkflow(url_root, template_id, token, body)
