# Example3.py
# written and tested in Python 3.6.0
# last updated 07/06/17

import webbrowser
import requests
import json
import time

# ---------------- #
# Global Variables #
# ---------------- #

url_root = 'https://default.tap.thinksmart.com/prod/'
client_id = '157b66c9f77c4283b807f23d245b3c72'
client_secret = '+jlq7YVyAq2OB5/SghSOXOA2/8AzqO/br/Yn8Hpoz/Y='
redirect_uri = 'https://google.com'
workflow_name = 'InitiateTest'

# --------- #
# Functions #
# --------- #

def getCode(url_root, client_id, redirect_uri):
	"""
	Given: Environment, client ID, and redirect URI.
	Return: None, opens browser for user to enter credentials.
	"""

	# concatenate environment address with piece of URL specific to API
	url = url_root + ('auth/identity/connect/authorize?' +
										'client_id=' + client_id +
										'&scope=api&' +
										'response_type=code&' +
										'redirect_uri=' + redirect_uri)

	# open browser
	webbrowser.open_new(url)

def getToken(url_root, code, client_id, client_secret):
	"""
	Given: Environment, code, and client info.
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
	Given: Environment, name of workflow, and valid token.
	Return: Template ID of workflow.
	"""

	# construct URL
	# workflow_name must be quoted, e.g. ?$filter=WorkflowName eq 'CamTest'
	url = ("{}api/v1/templates/dashboard?$filter=WorkflowName eq '{}'"
					.format(url_root, workflow_name))

	# needs token
	headers = {'Authorization' : 'Bearer ' + token}

	# make API call
	r = requests.get(url, headers=headers)

	# parse GET call response, return template ID
	return json.loads(r.text).get('Items')[0].get('ID')

def createWorkflow(url_root, template_id, token, body):
	"""
	Given: Environment, ID of workflow, valid token, and field names and values.
	Return: None, makes POST call to initiate workflow.
	"""
	
	# construct URL
	url = '{}api/v1/workflows/{}/form'.format(url_root, template_id)

	# needs token
	headers = {'Authorization' : 'Bearer ' + token,
							'Content-Type' : 'application/json'}

	# encode body into JSON
	json_body = json.dumps(body)

	# make API call
	requests.post(url, headers=headers, data=json_body)

# -------------- #
# Function Calls #
# -------------- #

print("In a few seconds, a tab in your browser will open. " +
			"Enter your TAP credentials, and you will be redirected. " +
			"Please copy and paste the URL of the Google redirect page into the space below.")

time.sleep(3)

getCode(url_root, client_id, redirect_uri)
redirect = input("URL from Google redirect page: ")
code = redirect.split('code=')[1]

token = getToken(url_root, code, client_id, client_secret)

template_id = getTemplateID(url_root, workflow_name, token)

body = {"element5": "Hello", "element6": "World", "element7": "Dogs"}

createWorkflow(url_root, template_id, token, body)