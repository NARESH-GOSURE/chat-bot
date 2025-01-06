import urllib.parse

from gosure.http_handler import Handler


class GosureApi:

    def __init__(self, token=None, base_url=None):
        # print(f"Received token & url : {token}, {base_url}")
        if token == None:
            raise Exception("Gosure Platform Token unavailable")
        self.token = token
        if base_url == None:
            raise Exception("Base url is Not Configured")
        self.base_url = base_url
        self.http = Handler()

    def get_token(self):
        return self.token

    def get_headers(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        print(f"headers: {headers}")
        return headers

    def get_attachment(self, file_url):
        encoded_url = urllib.parse.quote(file_url)
        url = f"{self.base_url}/api/v1/s3-objects/download?url={encoded_url}"
        return self.http.get_file(url, self.get_headers())

    def get_jobtype_id(self, name):
        jobtype_fields = self.get_jobtype_fields(name)
        if jobtype_fields == 404:
            print(f"[get_jobtype_id] Jobtype not found with name: {name}", flush=True)
            return False
        return jobtype_fields["orgs"][0]["id"]

    def get_jobinstance_id(self, name, filter):
        jobinstance = self.get_jobinstance_by_filter(name, filter)
        if len(jobinstance["jobs"]) > 0:
            return jobinstance["jobs"][0]["id"]
        print(
            f"[get_jobinstance_id] Jobinstance not found with the provided filter: {filter}",
            flush=True,
        )
        return False

    def get_jobtype_fields(self, name):
        encoded_name = urllib.parse.quote(name)
        url = f"{self.base_url}/api/v1/job-types/name/{encoded_name}/fields"
        return self.http.get(url, self.get_headers())

    def get_jobinstance_by_filter(self, name, filter):
        encoded_name = urllib.parse.quote(name)
        url = f"{self.base_url}/api/v1/job-types/name/{encoded_name}/instances?pageNumber=1&pageSize=10&filters={filter}"
        return self.http.get(url, self.get_headers())
    
    def get_jobinstance(self, id):
        url = f"{self.base_url}/api/v1/job-instances/{id}"
        return self.http.get(url, self.get_headers())

    def get_first_jobinstance_by_jobtype(self, name):
        url = f"{self.base_url}/api/v1/job-types/name/{name}/instances?pageNumber=1&pageSize=10"
        resp = self.http.get(url, self.get_headers())
        if "jobs" in resp:
            return resp["jobs"][0] if len(resp["jobs"]) > 0 else None
        return None

    def update_jobinstance(self, id, payload):
        url = f"{self.base_url}/api/v1/job-instances/{id}"
        return self.http.put(url, self.get_headers(), payload)

    def update_jobinstance_workflow(self, id, payload):
        url = f"{self.base_url}/api/v1/job-instances/update-workflow-status"
        return self.http.post(url, self.get_headers(), payload)

    def get_jobinstance(self, id):
        url = f"{self.base_url}/api/v1/job-instances/{id}"
        return self.http.get(url, self.get_headers())

    def create_jobtype(self, jobtype):
        path = f"{self.base_url}/api/v1/job-types"
        return self.http.post(path, self.get_headers(), jobtype)

    def create_jobinstance(self, jobinstance):
        path = f"{self.base_url}/api/v1/job-instances"
        resp = self.http.post(path, self.get_headers(), jobinstance)
        return resp["id"]

    def create_subjobtype(self):
        pass