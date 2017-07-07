# Example1.py
# Resource Owner Flow
# written and tested in Python 3.6.0
# last updated 07/07/17

import getpass
import requests
import json

# ---------------- #
# Global Variables #
# ---------------- #

# replace tenant with your own
url_root = 'https://tenant.tap.thinksmart.com/prod/'
# fill in (must be strings)
client_id = ''
client_secret = ''
workflow_name = ''
# enter username and password in command line during runtime
username = input("Please enter your TAP username: ")
password = getpass.getpass("Enter your password: ")

# --------- #
# Functions #
# --------- #

def getToken(url_root, username, password, client_id, client_secret):
	"""
	Given: URL root, user credentials, and client info.
	Return: Access token, valid for 1 hour.
	"""

	# construct URL
	url = '{}auth/identity/connect/token'.format(url_root)

	# static header, see docs.thinksmart1.apiary.io for documentation
	headers = {'Content-Type' : 'application/x-www-form-urlencoded'}

	# create dict for body
	body = {'grant_type' : 'password',
					'scope' : 'api',
					'redirect_uri' : 'testuri',
					'username' : username,
					'password' : password,
					'client_id' : client_id,
					'client_secret' : client_secret}

	# make API call
	r = requests.post(url, headers=headers, data=body)
	
	# parse POST call response, return token
	return json.loads(r.text).get('access_token')

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

# get token
token = getToken(url_root, username, password, client_id, client_secret)

# get template ID
template_id = getTemplateID(url_root, workflow_name, token)

# a dictionary is used to fill fields in the workflow
# keys are field names, values are field values
# below is an example of what it may look like
body = {"element1": "Hello", "element2": "World"}

# initiate workflow
initiateWorkflow(url_root, template_id, token, body)
