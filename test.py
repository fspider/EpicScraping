import requests

base_url = 'https://electoralsearch.in/Home/GetCaptcha?image=true&id=Wed%20Apr%2007%202021%2004:50:30%20GMT+0800%20(China%20Standard%20Time)'
session = requests.Session()
r = session.get(base_url, headers={})

