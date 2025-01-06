import requests


class TenantLogin:
    def __init__(self, url, tenant_name, username, password):
        self.api_url = f"{url}/api/v1/users/login"
        self.headers = {"X-Tenant": tenant_name}
        self.json_data = {"username": username, "password": password}
        self.access_token = None

    def tenant_login(self):
        try:
            response = requests.post(
                self.api_url, headers=self.headers, json=self.json_data
            )
            if response.status_code == 200:
                api_response = response.json()
                self.access_token = api_response.get("accessToken")
                return self.access_token
                # return api_response
            else:
                print(f"Response Failed : {response.status_code}")
                return response.text
        except Exception as error:
            print(f"Error Occurred : {error}")
            return None
