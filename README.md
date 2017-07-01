# API Examples

We will be adding examples around how to use our API to this Github repo.

Further documentation can be found on [Apiary](http://docs.thinksmart1.apiary.io/) and [Swagger](https://demo.tap.thinksmart.com/prod/api/swagger/ui/index)

[Example #1](https://github.com/ThinkSmart/API_Examples/blob/master/Example1.py): This example uses the resource owner flow to get a token, get a templateID, and submit a workflow with predetermined values.

[Example #2](https://github.com/ThinkSmart/API_Examples/blob/master/Example2.py): This example does the same thing as Example #1 but uses the Authorization Code flow. This will open a sign in page online, and use the resulting code to get a token, and use the token to submit a workflow.

[Initiate_Template.py](https://github.com/ThinkSmart/API_Examples/blob/master/Initiate_Template.py?ts=2): This script initiates a workflow any number of times with field names and values taken from a CSV file. Makes API calls using functions from Initiate_Functions.py, and is set up to submit field data in TestFields.csv to the InitiateTest workflow in the default production environment.
