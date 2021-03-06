import requests
import json


SNOVIO_API_URL = 'https://api.snov.io/'
SNOVIO_USER_ID = 'your-user-id'
SNOVIO_USER_SECRET = 'your-user-secret'


class SnovioError(Exception):

    def __init__(self, response):
        self.response = response

    def __str__(self):
        return self.response


class IncorrectLoginError(SnovioError):
    pass

class InsufficientCreditsError(SnovioError):
    pass


class SnovioAPI:

    def __init__(self, client_id=None, client_secret=None, access_token=None):
        if (not client_id and not client_secret) and not access_token:
            raise IncorrectLoginError('Please provide an access_token or client_id \
                and client_secret keys.')
        if not access_token:
            access_token = self.get_access_token(client_id, client_secret)

        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret


    def get_access_token(self, client_id, client_secret):
        auth_endpoint = 'oauth/access_token'
        params = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }

        response = self.get_response(auth_endpoint, params)
        return response.json()['access_token']


    def _request(self, endpoint, data):
        if self.is_parameter_in_uri(endpoint):
            endpoint = self.update_endpoint_with_query_params(endpoint, data)
            data = {}

        # Add authentication
        data['access_token'] = self.access_token
        response = self.get_response(endpoint, data)

        # Response Validation
        if response.status_code == 200:
            response = response.json()
            response.pop('access_token', None)
            return response

        elif response.status_code == 400:
            error = response.json()
            if error:
                message = error.get('message', '')
                if 'you ran out of credits' in error:
                    raise InsufficientCreditsError(message)
                else:
                    raise SnovioError(message)
            else:
                raise SnovioError("Client Error, check request")

        elif response.status_code == 401:
            print('Refreshing token')
            if self.is_parameter_in_uri(endpoint):
                endpoint = self.update_endpoint_with_query_params(endpoint, data)
                data = {}
            self.access_token = self.get_access_token(self.client_id, self.client_secret)
            data['access_token'] = self.access_token
            response = self.get_response(endpoint, data)
            return response.json()


    def __getattr__(self, name):
        def wrapper(data={}):
            response = self._request(name.replace('_', '-'), data)
            if 'error' in response:
                raise SnovioError(response)
            return response
        return wrapper


    @staticmethod
    def is_parameter_in_uri(endpoint):
        query_params_endpoints = [
            'get-emails-verification-status', 
            'add-emails-to-verification'
        ]
        if endpoint in query_params_endpoints:
            return True
        return False

    @staticmethod
    def get_version(endpoint):
        #Overkill now, but assuming they'll have a mix of apis versions in future
        version_dict = {
            'v2': ['domain-emails-with-info']
        }
        for version in version_dict.keys():
            if endpoint in version_dict[version]:
                return version
        return 'v1'

    @staticmethod
    def get_response(endpoint, data):
        version = SnovioAPI.get_version(endpoint)
        endpoint_uri = f'{SNOVIO_API_URL}{version}/{endpoint}'
        response = None
        if version == 'v2': #In v2 they've changed to use get
            response = requests.get(endpoint_uri, params=data)
        else:
            response = requests.post(endpoint_uri, data=data)
        return response


    @staticmethod
    def update_endpoint_with_query_params(endpoint, data):
        if not data.get('emails', False):
            raise SnovioError(f"'emails' parameter missing from request to endpoint {endpoint}.")
        
        updated_endpoint = endpoint + '?' 
        for email in data['emails']:
            updated_endpoint = updated_endpoint + 'emails[]=' + email + '&'

        return updated_endpoint[:-1] # remove the last &



if __name__ == "__main__":
    # Initialize the instance with your credentials
    snovio = SnovioAPI(client_id=SNOVIO_USER_ID, client_secret=SNOVIO_USER_SECRET)

    # FREE: Get domain emails count √
    # domain_emails_count = snovio.get_domain_emails_count({
    #     'domain': 'riskpulse.com'
    # }) 
    # print(domain_emails_count)

    # 2 Credits: Get domain emails with info √
    # domain_emails_with_info = snovio.domain_emails_with_info({
    #     'domain':'riskpulse.com',
    #     'type': 'all',
    #     'limit': 100,
    #     'lastId': 0
    # })
    # print(domain_emails_with_info)

    # FREE: Get emails verification status √
    # emails = snovio.get_emails_verification_status({
    #     'emails': ['gavin.vanrooyen@octagon.com', 'lizi.hamer@octagon.com']
    # })
    # print(emails)

    # 0.5 Credits: Add emails to verification √
    # add_emails_to_verification = snovio.add_emails_to_verification({
    #    'emails': ['sales@riskpulse.com', 'lizi.hamer@octagon.com']
    # })
    # print(add_emails_to_verification)

    # 1 Credit: Get emails from names √
    # get_emails_from_names = snovio.get_emails_from_names({
    #    'firstName': 'Joe',
    #    'lastName': 'Thomas',
    #    'domain': 'loom.com'
    # })
    # print(get_emails_from_names)

    # 1 Credit: Add names to find emails √
    # add_names_to_find_emails = snovio.add_names_to_find_emails({
    #    'firstName': 'Joe',
    #    'lastName': 'Thomas',
    #    'domain': 'loom.com'
    # })
    # print(add_names_to_find_emails)

    # 1 Credit: Get profile by email √
    # get_profile_by_email = snovio.get_profile_by_email({
    #    'email': 'lizi.hamer@octagon.com',
    # })
    # print(get_profile_by_email)