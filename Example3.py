# Example3.py
# Authorization Code Flow
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
client_secret = ''
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
	url = ('{}auth/identity/connect/authorize?client_id={}&scope=api&response_type=code&redirect_uri={}'
					.format(url_root, client_id, redirect_uri))

	# open browser
	webbrowser.open_new(url)

def getToken(url_root, code, client_id, client_secret):
	"""
	Given: URL root, code, and client info.
	Return: Access token, valid for 1 hour.
	"""

	# construct URL
	url = '{}auth/identity/connect/token'.format(url_root)

	# static header, see docs.thinksmart1.apiary.io for documentation
	headers = {'Content-Type' : 'x-www-form-urlencoded'}

	# create dict for body
	body = {'grant_type' : 'authorization_code',
					'scope' : 'api',
					'redirect_uri' : 'https://google.com',
					'code' : code,
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
	# workflow_name must be quoted, e.g. ?$filter=WorkflowName eq 'CamTest'
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

# open browser, take URL as input, parse for code
getBrowser(url_root, client_id, redirect_uri)
redirect = input("URL of redirect page: ")
# the parsing here works with redirect_uri = 'https://google.com'
code = redirect.split('code=')[1]

# get token
token = getToken(url_root, code, client_id, client_secret)

# get template ID
template_id = getTemplateID(url_root, workflow_name, token)

# a dictionary is used to fill fields in the workflow
# keys are field names, values are field values
# below is an example of what it may look like
body = {"element1": "Hello", "element2": "World"}

# initiate workflow
initiateWorkflow(url_root, template_id, token, body)
