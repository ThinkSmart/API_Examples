# API Examples

We will be adding examples around how to use our API to this GitHub repo.

Further documentation can be found on [Apiary](http://docs.thinksmart1.apiary.io/) and [Swagger](https://demo.tap.thinksmart.com/prod/api/swagger/ui/index).

[Example #1](https://github.com/ThinkSmart/API_Examples/blob/master/Example1.py?ts=2): This example uses the resource owner flow to get a token, get a template ID, and submit a workflow with predetermined values.

[Example #2](https://github.com/ThinkSmart/API_Examples/blob/master/Example2.py?ts=2): This example does the same thing as Example #1 but uses the authorization code flow. This will open an online login page, use the resulting code to get a token, and use the token to submit a workflow.

[Workflow_via_CSV](https://github.com/ThinkSmart/API_Examples/tree/master/Workflow_via_CSV): These files can be used to initiate a workflow any number of times with field names and values taken from a CSV file. Uses resource owner flow and reports on data for each workflow instance, including errors. 
