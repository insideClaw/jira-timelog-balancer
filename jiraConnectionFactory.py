import requests
import sys
import getpass

base_url = "https://tasks.novarumcloud.com/"
api_url = base_url + "rest/api/2"
headers = {'Content-Type': 'application/json'}
debug = False

class JiraSession:
    def __init__(self):
        pass

    def askUserForCreds(self):
        '''Interactively asks for credentials and returns both'''
        if debug:
            with open("creds", "r") as f:
                username, password = f.read().splitlines()
        else:
            username = input("Enter your Jira username (usually flastname): ")
            password = getpass.getpass("Enter your Jira password: ")
        return(username, password)

    def __enter__(self):
        '''Establish a session and returns it as a context managed object.'''
        s = requests.Session()
        USERNAME, PASSWORD = self.askUserForCreds()
        s.auth = USERNAME, PASSWORD
        s.headers = headers
        s.timeout = 5

        if s.get("{}/user?username={}".format(api_url, USERNAME)).status_code == 200:
            print("-=- Authenticated session established.")
        else:
            print("""-!- Failed to authenticate, check connection and password etc.\n
                If you continue to have problems - try logging out and in with a browser first\n
                Recaptcha may be required.""")
            sys.exit(1)

        return(s)

    def __exit__(self, exception_type, exception_value, traceback):
        pass
