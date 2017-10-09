# Workflow_via_CSV

The files in this folder can be used for bulk workflow initiation, i.e. submitting the first stage of a workflow any number of times, with potentially different field values in each instance. Specifically, [bulk_initiate.py](https://github.com/ThinkSmart/API_Examples/blob/master/Workflow_via_CSV/bulk_initiate.py?ts=2) retrieves an access token via resource owner flow, finds the template ID for the workflow of interest, and uses data in a CSV file to initiate workflows. Calls to the ThinkSmart API are made with functions imported from [bulk_functions.py](https://github.com/ThinkSmart/API_Examples/blob/master/Workflow_via_CSV/bulk_functions.py?ts=2). 

To get started, here's what to do.
            
1. First, build your workflow in TAP

Preferably avoid punctuation in the workflow name
	Also be sure it's been published and saved

2. Then, create a CSV file based on your workflow

In the first row of your CSV file, add the labels of the fields shown in the first stage of your workflow (at a minimum, include all required fields)

This is a good place for us to pause and explain an important distinction -- fields in TAP have two attributes we're interested in: label and name. The field label will appear as "Click to edit" while the field name will be the word 'element' followed by a number appearing below the field. The files here expect to be given field labels, and will convert those into names for you before initiating the workflows. 

In the second row of your CSV, add values for the fields that you specified in the first row
	The value for a field should be in the same column/position as the name for that field
	Each subsequent row represents a different workflow instance, and you can specify the field values in the same way

3. Fill in the global variables

You'll need to ask your ThinkSmart account manager for client id/secret, which are specific to your tenant and environment
TAP shows this information in your browser's address bar: https://{tenant}.{environment}.thinksmart.com/

4. Finally, check for best practices

Check that Form access is configured in your workflow
	We can only submit a value to a field set to "Show"

When entering field names in the first row of your CSV file, watch for extraneous spaces or line breaks
	These need to match exactly with the field names in TAP

If a particular field is unused in all of your workflows, there's no harm in excluding it

If your field name or value includes commas, wrap it in quotes (text editor, Excel should do this for you)

All apostrophes and quotes must be straight instead of curly
	When these punctuation are curly, they may not be read correctly

When specifying a user in your workflow, don't use a dropdown with registered users
	Instead, use two text fields: one for the name, and another for the Email (with Email validation)

If choosing an option from a dropdown, use "Edit option values" to set labels and values the same
	The code will try to match your input with the values in a dropdown


After you've run the bulk_initiate file, a txt file will appear in the same directory as the code. 

The report will include a summary for each row of the CSV. If a workflow was successfully initiated for a particular row, each name-value pair will be listed below the row number. If not, an error message will be shown. 

If there are field names from the workflow that don't match those in the CSV file, or vice-versa, this will be visible at the top of the report. If the workflow contains more than one field with the same name, they will be selected based on position within the form (specifically, the field closest to the top of the form will be filled in first). In addition, the element number (field name) for each will be listed in parentheses next to its label, making it easier to differentiate between duplicates (as field names are unchangeable).

If you have questions or suggestions, send them to cpierce@thinksmart.com