import requests

s = requests.Session()
login_url = 'http://127.0.0.1:5000/auth/login'

# Get CSRF token
r = s.get(login_url)
print(f"GET Login: {r.status_code}")
if 'csrf_token' in r.text:
    print("CSRF token found in page.")
    # Extract token (naive)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    print(f"Token: {csrf_token}")
    
    # Post login
    data = {
        'csrf_token': csrf_token,
        'username': 'admin',
        'password': 'admin',
        'remember_me': 'y'
    }
    r = s.post(login_url, data=data, allow_redirects=False)
    print(f"POST Login Status: {r.status_code}")
    print(f"Redirect Location: {r.headers.get('Location')}")
else:
    print("No CSRF token found!")
