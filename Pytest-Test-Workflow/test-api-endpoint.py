import pytest
import requests

def test_validate_object_count():
    # Send a GET request to the API endpoint
    response = requests.get("https://api.restful-api.dev/objects")

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Parse the JSON response
    data = response.json()

    # Validate the number of objects in the response
    assert len(data) == 13, f"Expected 13 objects, but received {len(data)}"
