import functions_framework
import sys
import os
import requests

#sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#from shared.models.gcloud_integration import GCloudIntegrations

@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    #request_json = request.get_json(silent=True)
    #request_args = request.arg
    # request_method = request.method

    # if request_method == 'POST':
    #     return '200', 200
    # elif request_method == 'GET':
    #     return '400', 400
    # elif request_method in ['PUT', 'DELETE']:
    #     return '500', 500
    # else:
    #     return 'Method unsupported'

    return "test_print_anything"