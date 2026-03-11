import requests

# Test login
login_resp = requests.post("http://localhost:8000/api/auth/login", json={
    "username": "testuser",
    "password": "test123"
})

if login_resp.status_code == 200:
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # List reference types
    ref_types_resp = requests.get("http://localhost:8000/api/reference-types", headers=headers)
    print(f"Reference types: {ref_types_resp.status_code}")
    if ref_types_resp.status_code == 200:
        print(ref_types_resp.json())
    else:
        print(ref_types_resp.text)
