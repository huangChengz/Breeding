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

            # Find a leaf node
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
                print(f"Node: {leaf_node.get('node_code')} - {leaf_node.get('node_title')}")
                node_id = leaf_node['id']

                # Get scenes
                scenes_resp = requests.get(
                    f"http://localhost:8000/api/projects/{project_id}/scenes",
                    headers=headers
                )
                scenes = scenes_resp.json()
                print(f"Scenes: {len(scenes)}")

                if scenes:
                    scene = scenes[0]
                    print(f"Scene ID: {scene['id']}")

                    # Use the 'core' reference type
                    ref_type_id = "e46e3da2-ccd5-4b12-90bd-6779de0a1790"

                    # Add reference with ref_type_id
                    ref_resp = requests.post(
                        f"http://localhost:8000/api/outline/{node_id}/references",
                        headers=headers,
                        json={
                            "ref_entity_type": "scene",
                            "ref_entity_id": scene['id'],
                            "ref_type_id": ref_type_id,
                            "is_active": True
                        }
                    )
                    print(f"Add reference status: {ref_resp.status_code}")
                    print(f"Response: {ref_resp.text[:200]}")
            break
