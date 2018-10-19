#!/usr/bin/env python3
import requests
import sys
import getpass
import base64

def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)

class JiraSession:
    def __init__(self):
        self.base_url = "https://tasks.novarumcloud.com/"
        self.api_url = self.base_url + "rest/api/2"
        self.headers = {'Content-Type': 'application/json'}
        self.debug = True

    def askUserForCreds(self):
        '''Interactively asks for credentials and returns both'''
        if self.debug:
            with open("creds", "r") as f:
                username, passwordEncrypted = f.read().splitlines()
                password = decode("mysalt", passwordEncrypted)
        else:
            username = input("Enter your Jira username (usually flastname): ")
            password = getpass.getpass("Enter your Jira password: ")
        return(username, password)

    def __enter__(self):
        '''Establish a session and returns it as a context managed object.'''
        s = requests.Session()
        USERNAME, PASSWORD = self.askUserForCreds()
        s.auth = USERNAME, PASSWORD
        s.headers = self.headers
        s.timeout = 5

        if s.get("{}/user?username={}".format(self.api_url, USERNAME)).status_code == 200:
            print("-=- Authenticated session established.")
        else:
            print("""-!- Failed to authenticate, check connection and password etc.\n
                If you continue to have problems - try logging out and in with a browser first\n
                Recaptcha may be required.""")
            sys.exit(1)

        return(s)

    def __exit__(self, exception_type, exception_value, traceback):
        pass
