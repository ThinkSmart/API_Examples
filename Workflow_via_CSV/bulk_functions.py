# bulk_functions.py
# written and tested in Python 3.6.0
# last updated 10/02/17

import requests
import json

def getToken(url_root, username, password, client_id, client_secret):
	"""
	Given: URL root, user credentials, and client info.
	Return: Response of POST call for token.
	"""

	# concatenate environment address with piece of URL specific to API
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

	# return POST call response
	return requests.post(url, headers=headers, data=body)

def getTemplateID(url_root, workflow_name, token):
	"""
	Given: URL root, name of workflow, and valid token.
	Return: Response of GET call for ID of template.
	"""

	# construct URL
	# filtering here, but characters like '&' can cause problems
	url = ("{}api/v1/templates/dashboard?$filter=WorkflowName eq '{}'"
		.format(url_root, workflow_name))

	# needs token
	headers = {'Authorization' : 'Bearer {}'.format(token)}

	# return GET call response
	return requests.get(url, headers=headers)

def getFormInfo(url_root, template_id, token):
	"""
	Given: URL root, ID of workflow, and valid token.
	Return: Response of GET call for form info.
	"""

	# construct URL
	url = '{}api/v1/workflows/form?templateId={}'.format(url_root, template_id)

	# needs token
	headers = {'Authorization' : 'Bearer {}'.format(token),
		'Content-Type' : 'application/json'}

	# return GET call response
	return requests.get(url, headers=headers)

def initiateWorkflow(url_root, template_id, token, body):
	"""
	Given: URL root, ID of workflow, valid token, and field names and values.
	Return: Response of POST call to initiate workflow.
	"""
	
	# construct URL
	url = '{}api/v1/workflows/{}/form'.format(url_root, template_id)

	# needs token
	headers = {'Authorization' : 'Bearer {}'.format(token),
		'Content-Type' : 'application/json'}

	# encode body into JSON
	json_body = json.dumps(body)

	# return POST call response
	return requests.post(url, headers=headers, data=json_body)
