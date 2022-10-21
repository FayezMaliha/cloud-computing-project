from app import app
from app import cache
import pytest
import io
import sys
sys.path.append('../backend')

AddedImageKey = 'myKey'

@pytest.fixture()
def main():
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture()
def client(main):
    return main.test_client()

@pytest.fixture()
def runner(main):
    return main.test_cli_runner()

# Test Adding an Image
def test_adding_image(client):
    data = {'Key': AddedImageKey, 'filename' : (io.BytesIO(b"some initial text data"), 'test.jpg')}
    response = client.post("/put", 
        data=data,
        follow_redirects=True,
        content_type='multipart/form-data'
    )
    assert response.status_code == 201
    
def test_get_image(client):
    response = client.post("/get", data={
        "Key": "m",#AddedImageKey,
    })
    assert response.status_code == 200

# * Test Non-exisitng Key an Image 
def test_get_failure(client):
    response = client.post("/get", data={
        "Key": "ThisKeyShouldNotBeThere"
    })
    assert response.status_code == 404

# * Test Changing Cache Config
def test_setting_size_and_policy(client):
    prePolicy = cache.lru
    response1 = client.post("/change_policy")
    response2 = client.post("/change_capacity", data={
        "new_size": 1,
    })
    assert response1.status_code != 404
    assert response2.status != 404
    assert int(cache.maxSizeByte/(1024*1024)) == 1 
    assert cache.lru != prePolicy

# * Test clearing Cache  
def test_clear_cache(client):
    # Add image to cache
    response = client.post("/get", data={
        "Key": "m", #addedImageKey,
    })
    assert response.status_code == 200
    # Clear cache
    response = client.post("/clear")
    assert response.status_code != 404
    assert cache.size == 0
    assert cache.count() == 0

# * Test deleting Cache Config
def test_delete_key(client):
    response = client.post("/delete_key", data={
        "key_to_delete": "m",#AddedImageKey,
    })
    assert response.status_code != 404