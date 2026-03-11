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

            # Get outline
            outline_resp = requests.get(
                f"http://localhost:8000/api/projects/{project_id}/outline",
                headers=headers
            )
            outline = outline_resp.json()

            # Find a leaf node (one that has no children)
            def find_leaf(nodes):
                for node in nodes:
                    if node.get('is_leaf') or not node.get('children'):
                        return node
                    if node.get('children'):
                        leaf = find_leaf(node['children'])
                        if leaf:
                            return leaf
                return None

            leaf_node = find_leaf(outline)
            if leaf_node:
                print(f"Found leaf node: {leaf_node.get('node_code')} - {leaf_node.get('node_title')}")
                node_id = leaf_node['id']

                # Add a reference first (scene)
                scenes_resp = requests.get(
                    f"http://localhost:8000/api/projects/{project_id}/scenes",
                    headers=headers
                )
                scenes = scenes_resp.json()
                print(f"Scenes: {len(scenes)}")

                if scenes:
                    scene_id = scenes[0]['id']
                    # Add reference
                    ref_resp = requests.post(
                        f"http://localhost:8000/api/outline/{node_id}/references",
                        headers=headers,
                        json={
                            "ref_entity_type": "scene",
                            "ref_entity_id": scene_id,
                            "reference_type_id": None,
                            "is_active": True
                        }
                    )
                    print(f"Add reference status: {ref_resp.status_code}")

                # Try to generate content (non-streaming for testing)
                try:
                    gen_resp = requests.post(
                        f"http://localhost:8000/api/outline/{node_id}/generate",
                        headers=headers,
                        timeout=120
                    )
                    print(f"Generate status: {gen_resp.status_code}")
                    if gen_resp.status_code == 200:
                        print("Generate success!")
                        result = gen_resp.json()
                        print(f"Content length: {len(result.get('content', ''))}")
                    else:
                        print(f"Error: {gen_resp.text[:500]}")
                except Exception as e:
                    print(f"Generate error: {e}")
            else:
                print("No leaf node found")
            break
else:
    print(f"Login failed: {login_resp.status_code}")
