import requests

# Test login
login_resp = requests.post("http://localhost:8000/api/auth/login", json={
    "username": "testuser",
    "password": "test123"
})

if login_resp.status_code == 200:
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Find horticulture project
    proj_resp = requests.get("http://localhost:8000/api/projects", headers=headers)
    projects = proj_resp.json()

    for p in projects:
        if '园艺' in p.get('project_name', ''):
            project_id = p['id']
            print(f"Project ID: {project_id}")

            # Initialize outline with force
            try:
                init_resp = requests.post(
                    f"http://localhost:8000/api/projects/{project_id}/outline/initialize?force=true",
                    headers=headers,
                    timeout=60
                )
                print(f"Status: {init_resp.status_code}")
                print(f"Response: {init_resp.text}")
            except Exception as e:
                print(f"Error: {e}")
            break
else:
    print(f"Login failed: {login_resp.status_code}")
