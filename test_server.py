import requests
import json

# The URL where your local server is running.
SERVER_URL = "http://127.0.0.1:8000/query"

# A list of questions to test. These should match the keys in the query_map
# in your ipl_mcp_server.py file to ensure all functionality is tested.
TEST_QUERIES = [
    # Basic Match Information
    "Show me all matches in the dataset",
    "Which team won the most matches?",
    "What was the highest total score?",
    "Show matches played in Mumbai",
    
    # Player Performance
    "Who scored the most runs across all matches?",
    "Which bowler took the most wickets?",
    "Show me Virat Kohli's batting stats",
    "Who has the best bowling figures in a single match?",
    
    # Advanced Analytics
    "What's the average first innings score?",
    "Which venue has the highest scoring matches?",
    "Show me all centuries scored",

    # A test for a question that is NOT in our map
    "What is the airspeed velocity of an unladen swallow?"
]

def run_tests():
    """
    Sends each test query to the server and checks the response.
    """
    print("--- Starting Server Functionality Test ---")
    
    passed_tests = 0
    failed_tests = 0
    
    for i, question in enumerate(TEST_QUERIES):
        print(f"\n[{i+1}/{len(TEST_QUERIES)}] Testing question: '{question}'")
        
        try:
            # The payload to send, in JSON format.
            payload = {"question": question}
            
            # Send the POST request to the server.
            response = requests.post(SERVER_URL, json=payload, timeout=10)
            
            # Check if the request was successful (HTTP 200 OK).
            if response.status_code == 200:
                response_data = response.json()
                # Check if the response contains the 'response' key.
                if 'response' in response_data and response_data['response']:
                    print(f"✅ PASS: Server returned a valid response.")
                    # print("   " + response_data['response'].split('\n')[0] + "...") # Optional: print first line of response
                    passed_tests += 1
                else:
                    print(f"❌ FAIL: Server response was empty or malformed.")
                    failed_tests += 1
            else:
                print(f"❌ FAIL: Server returned status code {response.status_code}")
                failed_tests += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ FAIL: Could not connect to the server at {SERVER_URL}.")
            print(f"   Error: {e}")
            print("   Please ensure the 'uvicorn ipl_mcp_server:app --reload' server is running in another terminal.")
            failed_tests += 1
            # If we can't connect, no point in continuing.
            break

    # --- Print Final Summary ---
    print("\n--- Test Summary ---")
    print(f"Total Tests: {len(TEST_QUERIES)}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print("--------------------")

if __name__ == "__main__":
    run_tests()