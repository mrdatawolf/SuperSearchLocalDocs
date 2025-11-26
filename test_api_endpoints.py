"""Test the file open API endpoints"""
import requests
import json

# Test file that we know exists
test_file = r"\\192.168.203.207\Shared Folders\Retired\NetDocOld\2020\Network doc\Steve Morris.xlsx"

print("Testing file open endpoints...")
print(f"Test file: {test_file}")
print()

# Test 1: Open file
print("=" * 80)
print("TEST 1: /api/file/open")
print("=" * 80)
try:
    response = requests.post(
        'http://192.168.203.29:9000/api/file/open',
        json={'file_path': test_file},
        timeout=5
    )
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    print(f"Success: {response.ok}")
except Exception as e:
    print(f"ERROR: {e}")

print()

# Test 2: Open folder
print("=" * 80)
print("TEST 2: /api/file/open-folder")
print("=" * 80)
try:
    response = requests.post(
        'http://192.168.203.29:9000/api/file/open-folder',
        json={'file_path': test_file},
        timeout=5
    )
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    print(f"Success: {response.ok}")
except Exception as e:
    print(f"ERROR: {e}")

print()
print("Tests completed!")
