# resource_owner.py
# written and tested in Python 3.6.0
# last updated 06/26/17

import requests
import json
import getpass
import webbrowser
import time

# ---------------- #
# Global Variables #
# ---------------- #

# https://default.tap.thinksmart.com/prod/auth/identity/connect/authorize?client_id=&scope=api&response_type=code&redirect_uri=https://google.com

url_root = 'https://default.tap.thinksmart.com/prod/'
redirect_uri = "https://google.com"
client_id = '157b66c9f77c4283b807f23d245b3c72'
client_secret = '+jlq7YVyAq2OB5/SghSOXOA2/8AzqO/br/Yn8Hpoz/Y='

workflow_name = "CamTest"


# --------- #
# Functions #
# --------- #


def getCode(url_root, client_id, redirect_uri):
	"""
	Given: Environment, user credentials, and client info.
	Return: Response of POST call for token.
	"""

	# concatenate environment address with piece of URL specific to API
	url = url_root + 'auth/identity/connect/authorize?client_id={}&scope=api&response_type=code&redirect_uri={}'.format(client_id, redirect_uri)

	webbrowser.open_new(url)

def getToken(url_root, code, client_id, client_secret):
	"""
	Given: Environment, id, secret, and code.
	Return: Response of GET call for ID of template.
	"""

	# construct URL
	url = '{}auth/identity/connect/token'.format(url_root)

	# needs token
	headers = {'Content-Type' : 'x-www-form-urlencoded'}

	payload = {
		"grant_type":"authorization_code",
		"scope":"api",
		"redirect_uri":"https://google.com",
		"code":code,
		"client_id":client_id,
		"client_secret":client_secret  
	}

	# return POST call response
	r = requests.post(url, headers=headers, data=payload)
	j = json.loads(r.text)

	token = j["access_token"]

	return token

def getTemplateID(url_root, workflow_name, token):
	"""
	Given: Environment, name of workflow, and valid token.
	Return: Response of GET call for ID of template.
	"""

	# construct URL
	# workflow_name must be quoted, e.g. ?$filter=WorkflowName eq 'CamTest'
	url = ("{}api/v1/templates/dashboard?$filter=WorkflowName eq '{}'"
					.format(url_root, workflow_name))

	# needs token
	headers = {'Authorization' : 'Bearer ' + token}

	# return GET call response
	r = requests.get(url, headers=headers)
	print(r)
	return json.loads(r.text).get('Items')[0].get('ID')

def createWorkflow(url_root, template_id, token, body):
	"""
	Given: Environment, ID of workflow, valid token, and field names and values.
	Return: Response of POST call to initiate workflow.
	"""
	
	# construct URL
	url = '{}api/v1/workflows/{}/form'.format(url_root, template_id)

	# needs token
	headers = {'Authorization' : 'Bearer ' + token,
							'Content-Type' : 'application/json'}

	# decode body into JSON
	json_body = json.dumps(body)

	# return POST call response
	return requests.post(url, headers=headers, data=json_body)




# -------------- #
# Function Calls #
# -------------- #

print("In 5 seconds, a window will open asking you to login. Then it will redirect you to google. Please copy and paste the url of the Google redirect page below. And don't worry about the execution error below")

time.sleep(3)

getCode(url_root, client_id, redirect_uri)
redirect = raw_input("URL from Google redirect page:")
code = redirect.split("code=")[1]

token = getToken(url_root, code, client_id, client_secret)

template_id = getTemplateID(url_root, workflow_name, token)

answersToSubmit = {"element5": "Hello", "element6": "World"}

createWorkflow(url_root, template_id, token, answersToSubmit)
















