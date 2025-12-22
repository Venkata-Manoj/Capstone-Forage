import requests
import time
import os
import sys

BASE_URL = "http://localhost:8000"

def create_dummy_file():
    with open("dummy_input.txt", "w") as f:
        f.write("This is a dummy capstone project report content for testing purposes.\n" * 100)
    return "dummy_input.txt"

def wait_for_server():
    print("Waiting for server to be ready...")
    for _ in range(10):
        try:
            resp = requests.get(f"{BASE_URL}/health")
            if resp.status_code == 200:
                print("Server is ready!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)
    print("Server not reachable.")
    return False

def run_test():
    if not wait_for_server():
        return

    # 1. Upload
    print("\n--- Uploading File ---")
    filename = create_dummy_file()
    try:
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "text/plain")}
            data = {"title": "Test Project Title", "student_name": "Test User"}
            resp = requests.post(f"{BASE_URL}/api/upload", files=files, data=data)
            
        if resp.status_code != 200:
            print(f"Upload failed: {resp.status_code} - {resp.text}")
            return
            
        upload_data = resp.json()
        file_id = upload_data.get("file_id")
        print(f"File uploaded successfully. ID: {file_id}")
        
    except Exception as e:
        print(f"Upload Exception: {e}")
        return

    # 2. Generate
    print("\n--- Triggering Generation ---")
    try:
        payload = {
            "file_id": file_id,
            "title": "Test Project Title",
            "student_name": "Test User",
            "department": "Computer Science"
        }
        resp = requests.post(f"{BASE_URL}/api/generate", json=payload)
        
        if resp.status_code != 200:
            print(f"Generation start failed: {resp.status_code} - {resp.text}")
            return
            
        gen_data = resp.json()
        report_id = gen_data.get("report_id")
        print(f"Generation started. Report ID: {report_id}")
        
    except Exception as e:
        print(f"Generation Exception: {e}")
        return

    # 3. Poll Status
    print("\n--- Polling Status ---")
    for _ in range(30): # Wait up to 60 seconds
        try:
            resp = requests.get(f"{BASE_URL}/api/reports/{report_id}")
            if resp.status_code == 200:
                report = resp.json()
                status = report.get("status")
                print(f"Current Status: {status}")
                
                if status == "completed":
                    print("✅ Report generation COMPLETED successfully!")
                    return
                elif status == "failed":
                    print(f"❌ Report generation FAILED!")
                    print(f"Error Message: {report.get('error_message', 'Unknown error')}")
                    return
            else:
                print(f"Status check failed: {resp.status_code}")
        except Exception as e:
            print(f"Polling Exception: {e}")
            
        time.sleep(2)
        
    print("❌ Timeout waiting for generation.")

if __name__ == "__main__":
    run_test()
