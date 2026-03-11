import requests

# Test login
login_resp = requests.post("http://localhost:8000/api/auth/login", json={
    "username": "testuser",
    "password": "test123"
})

if login_resp.status_code == 200:
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # List all projects
    proj_resp = requests.get("http://localhost:8000/api/projects", headers=headers)
    projects = proj_resp.json()

    # Find horticulture project (园艺育种项目)
    print("Projects:")
    for p in projects:
        print(f"  {p['id']}: {p.get('project_name')}")
        if '园艺' in p.get('project_name', ''):
            project_id = p['id']
            print(f"\nFound horticulture project: {project_id}")

            # Initialize outline with force
            init_resp = requests.post(
                f"http://localhost:8000/api/projects/{project_id}/outline/initialize?force=true",
                headers=headers,
                timeout=60
            )
            print(f"Initialize result: {init_resp.status_code}")
            if init_resp.status_code == 200:
                print("Success!")
                # Get outline
                outline_resp = requests.get(
                    f"http://localhost:8000/api/projects/{project_id}/outline",
                    headers=headers
                )
                outline = outline_resp.json()
                print(f"Outline initialized: {len(outline)} chapters")
            else:
                print(f"Error: {init_resp.text[:500]}")
            break
