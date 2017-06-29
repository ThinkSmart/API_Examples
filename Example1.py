# written and tested in Python 3.6.0
# last updated 06/29/17

import getpass
import requests
import json

# ---------------- #
# Global Variables #
# ---------------- #

url_root = 'https://default.tap.thinksmart.com/prod/'
client_id = 'b858d97c24124c959ec0d78f3eccd77d'
client_secret = '0WDF4cRc4gtEEhOBXkCH6dTj1NU18L8iL6+i3jHXoR4='

username = input("Please enter your TAP username: ")
password = getpass.getpass("Enter your password: ")

workflow_name = "CamTest"

# --------- #
# Functions #
# --------- #

def getToken(url_root, username, password, client_id, client_secret):
	"""
	Given: Environment, user credentials, and client info.
	Return: Access token, valid for 1 hour.
	"""

	# concatenate environment address with piece of URL specific to API
	url = url_root + 'auth/identity/connect/token'

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
	return json.loads(r.text)["access_token"]

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

	# make POST call
	requests.post(url, headers=headers, data=json_body)

# -------------- #
# Function Calls #
# -------------- #

token = getToken(url_root, username, password, client_id, client_secret)

template_id = getTemplateID(url_root, workflow_name, token)

body = {"element5": "Hello", "element6": "World", "element7": "Dogs"}

createWorkflow(url_root, template_id, token, body)