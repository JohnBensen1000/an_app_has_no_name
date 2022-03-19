import requests

body = {
    "path": "", 
    "comment": "python3 is the best programming language", 
    "uid": "sT7vOyCnVDUKk8QjOOPnQpzrX5u1"
}

response = requests.post('http://0.0.0.0:8000/v2/comments/164735815255', json=body)

print(response.status_code)