# Initiate_Functions.py
# written and tested in Python 3.6.0
# last updated 06/30/17

import requests
import json

def getToken(url_root, username, password, client_id, client_secret):
	"""
	Given: Environment, user credentials, and client info.
	Return: Response of POST call for token.
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

	# return POST call response
	return requests.post(url, headers=headers, data=body)

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
	return requests.get(url, headers=headers)

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

	# encode body into JSON
	json_body = json.dumps(body)

	# return POST call response
	return requests.post(url, headers=headers, data=json_body)

def getFormInfo(url_root, template_id, token):
	"""
	Given: Environment, ID of workflow, and valid token.
	Return: Response of GET call for form info.
	"""

	url = '{}api/v1/workflows/form?templateId={}'.format(url_root, template_id)

	headers = {'Authorization' : 'Bearer ' + token,
							'Content-Type' : 'application/json'}

	return requests.get(url, headers=headers)