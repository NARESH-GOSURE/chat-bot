import urllib.parse
from gosure.login import TenantLogin
from src import config
import time
import json
from gosure.api import GosureApi
import requests
from bson import ObjectId
access_token = None
token_expiration_time = None
TOKEN_EXPIRATION_DURATION = 3600
TOKEN_FILE = "token_info.json"

url = config.get_gosure_base_url()
tenant = config.get_gosure_tenant()
username = config.get_gosure_tenant_username()
password = config.get_gosure_tenant_password()


def jobtypes_payload(name):
    jobtype_payload = {
        "jobType": {
            "name": "",
            "description": "",
            "isPublished": True,
            "isSubJobType": False,
            "containsStoreId": False,
            "report": "",
            "enableServices": False,
            "sendMailRequired": False,
            "icon": None,
            "isEmailTemplate": False,
            "isAttachmentEmailTemplate": False,
            "isReadOnly": False,
            "parentJobType": "",
            "parentJobIdentifier": "",
            "identifier": "",
            "enablePromoteTrackableChangesToParent": False,
            "riskScoreProperty": None,
            "maxRiskScoreProperty": "",
            "onSubmitActions": "",
            "downloadURL": "",
            "displayAPI": "",
            "associationRule": "",
            "enableWizard": False,
            "acknowledgeText": "",
            "hideBrowse": None,
            "isPivotParam": None,
            "isPivotRowParam": None,
            "isReportColumnParam": None,
            "isAggregate": None,
            "isAllowPublicAccess": False,
            "jobTypeConfig": {"jobTypeKind": "STANDARD"},
            "properties": [],
            "jobInstanceACL": None,
        }
    }
    jobtype_payload["jobType"]["name"] = name
    jobtype_payload["jobType"]["description"] = name
    return jobtype_payload


def jobinstance_payload(id,sessionid, instance):
    jobinstance = {
        "jobTypeId": id,
        "data": {"session_id":sessionid,
                 f'{sessionid}':[instance]},
    }
    return jobinstance


def load_token_from_file():
    global access_token, token_expiration_time
    try:
        with open(TOKEN_FILE, "r") as f:
            token_info = json.load(f)
            access_token = token_info.get("access_token")
            token_expiration_time = token_info.get("token_expiration_time")
    except FileNotFoundError:
        access_token = None
        token_expiration_time = None
    except json.JSONDecodeError:
        access_token = None
        token_expiration_time = None


def save_token_to_file():
    global access_token, token_expiration_time
    token_info = {
        "access_token": access_token,
        "token_expiration_time": token_expiration_time,
    }
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_info, f)


def get_access():
    global access_token, token_expiration_time

    load_token_from_file()
    if access_token and time.time() < token_expiration_time:
        remaining_time = token_expiration_time - time.time()
        print(
            f"Access token is still valid. Time remaining: {remaining_time:.2f} seconds."
        )
        return access_token
    print("Token is expired or not generated. Generating a new token...")
    login = TenantLogin(url, tenant, username, password)
    access_token = login.tenant_login()

    if access_token:
        # print("AccessToken generated:", access_token)
        token_expiration_time = time.time() + TOKEN_EXPIRATION_DURATION
        save_token_to_file()
    else:
        print("Error in getting access token.")

    return access_token


def use_access_token():
    valid_token = get_access()
    if valid_token:
        print("Using AccessToken:", valid_token)
    else:
        print("No valid access token available.")
    return valid_token


def create_new_job_type(g_api, job_type_name):
    get_existing_jobtype_id = g_api.get_jobtype_id(job_type_name)
    if get_existing_jobtype_id == False:
        job_type = g_api.create_jobtype(jobtypes_payload(job_type_name))
        new_job_type_id = job_type["jobType"]["id"]
        print("New Job Type has been Created  : ", new_job_type_id)
        return new_job_type_id
    else:
        print("Existing Job Type Id  :", get_existing_jobtype_id)
        return get_existing_jobtype_id


def create_job_instance(g_api,get_existing_jobtype_id,  sessionid,instances):
    # get_existing_jobtype_id = g_api.get_jobtype_id(job_type_name)
    if get_existing_jobtype_id != False:
        final_payload = jobinstance_payload(get_existing_jobtype_id,sessionid, instances)
        # print(final_payload)
        # print(type(final_payload))
        new_job_instance_id = g_api.create_jobinstance(final_payload)
        print("New Job Instance has been Created  : ", new_job_instance_id)
        return new_job_instance_id
    else:
        print("Error in Creating Instances")
        return None

payload = [{
            "timestamp": "2025-01-02T08:54:56.081000+00:00",
            "text": None,
            "type": "conversationUpdate",
            "role": None
        },
        {
            "timestamp": "2025-01-02T08:55:00.037000+00:00",
            "text": "hi",
            "type": "message",
            "role": "user"
        },
        {
            "timestamp": "2025-01-02T08:55:00.043500",
            "text": "Hello! I am Procurity ChatBot. How can I assist you today?",
            "type": "message",
            "role": "bot"
        }]

def save_conversation(job_type_name,session_id,input_instances):
    # use_access_token()
    access_token='eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiJvbmdvLWp3dCIsInN1YiI6ImFkbWluQGdvc3VyZS5haSIsImF1dGhvcml0aWVzIjpbXSwidGVuYW50IjoibmlhIiwib3JnSWQiOiI2NzBmNTQ0MzUwZDJmMzg5ODZlYjQ4ZGMiLCJyb2xlTmFtZSI6IlN1YiBBZG1pbiIsInVzZXJJZCI6IjY2YjRmZjI4ODQ2YzZhNmZkMmQ4NzNhZCIsImlhdCI6MTczNTgxMTc0NywiZXhwIjoxNzM2NDE2NTQ3fQ.YuF5wmbfbrlRy44NTlZn3azhP2seMMs523SudjP9qFG1LbjvTBmzcDIjwNUKk6oiorSvA2VkQm9nKVcGtvnc7w'
    g_api = GosureApi(access_token, url)
    new_job_type_id = create_new_job_type(g_api, job_type_name)
    job_instance = check_session_id_from_db_return_its_jobinstance_payload(g_api,job_type_name,session_id)
    if job_instance.get('totalNumRecords')!=0:
        upload_to_db(g_api,job_instance,input_instances)
    else:
        job_instance_id = create_job_instance(g_api, new_job_type_id, session_id,input_instances)
    



def check_session_id_from_db_return_its_jobinstance_payload(g_api,job_type_name,session_id):
    filter = json.dumps([{"fieldName":"session_id","condition":"is","value":session_id}])
    response = g_api.get_jobinstance_by_filter(job_type_name,filter)
    if response:
        return response
    else:
        return None



def upload_to_db(g_api,document,job_instance_json):
    job_instance_id = document['jobs'][0]['id']
    data = document['jobs'][0]["data"]
    session_id = data["session_id"]
    if session_id not in data:
        data[session_id] = []
    data[session_id].append(job_instance_json)

    job_instance = {
        "data": data
    }
    updated_job_instnces = g_api.update_jobinstance(job_instance_id,job_instance)



instances = {
    "session_id":"4813c14d-29fb-4afe-b89f-e18ae06a1dfa",
    "4813c14d-29fb-4afe-b89f-e18ae06a1dfa": [
        {
            "timestamp": "2025-01-02T08:54:56.081000+00:00",
            "text": None,
            "type": "conversationUpdate",
            "role": None
        },
        {
            "timestamp": "2025-01-02T08:55:00.037000+00:00",
            "text": "hi",
            "type": "message",
            "role": "user"
        },
        {
            "timestamp": "2025-01-02T08:55:00.043500",
            "text": "Hello! I am Procurity ChatBot. How can I assist you today?",
            "type": "message",
            "role": "bot"
        }
    ]
}
incoming_data={
            "timestamp": "pavi naresh",
            "text": "I can help you upload a PDF or search its contents. Try typing 'upload' or 'search'.",
            "type": "message",
            "role": "bot"
        }



# CHAT_BOT_JOBTYPE ='Chatbot'
# document = save_conversation(CHAT_BOT_JOBTYPE,"3813c14d-29fb-4afe-b89f-e18ae06a1dfa",incoming_data)



