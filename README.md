# API Examples
README (last updated 07/06/17)

We will be adding examples around how to use our API to this GitHub repo. 

Further documentation can be found on [Apiary](http://docs.thinksmart1.apiary.io/) and [Swagger](https://demo.tap.thinksmart.com/prod/api/swagger/ui/index).

[Example #1](https://github.com/ThinkSmart/API_Examples/blob/master/Example1.py?ts=2): This example uses the resource owner flow to get an access token, get a template ID, and submit a workflow with values defined in the script. 

[Example #2](https://github.com/ThinkSmart/API_Examples/blob/master/Example2.py?ts=2): This example does the same thing as Example #1 but uses implicit flow. The script will open a login page in the web browser, ask the user to copy and paste the URL of the redirect page, parse for an access token, and submit a workflow. 

[Example #3](https://github.com/ThinkSmart/API_Examples/blob/master/Example3.py?ts=2): This example does the same thing as Example #1 but uses the authorization code flow (the most secure of the three flows). The script will open a login page in the web browser, ask the user to copy and paste the URL of the redirect page, parse for the code, use the code to get an access token, and submit a workflow. 

[Workflow_via_CSV](https://github.com/ThinkSmart/API_Examples/tree/master/Workflow_via_CSV): These files can be used to initiate a workflow any number of times with field names and values taken from a CSV file. Uses resource owner flow and reports on data for each workflow instance, including errors. 
