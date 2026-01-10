"""
TalentScout API Test Script

This script demonstrates the TalentScout API endpoints
and simulates a complete interview flow.

Run this after starting the Django server:
    python manage.py runserver

Then in another terminal:
    python test_api.py
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/api"
HEADERS = {"Content-Type": "application/json"}


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_response(response):
    """Print formatted JSON response"""
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")


def test_health_check():
    """Test the health check endpoint"""
    print_section("Health Check")
    
    response = requests.get(f"{BASE_URL}/health/")
    print_response(response)
    
    return response.status_code == 200


def test_start_session():
    """Test starting a new interview session"""
    print_section("Starting New Session")
    
    response = requests.post(f"{BASE_URL}/sessions/start/", headers=HEADERS)
    print_response(response)
    
    if response.status_code == 201:
        session_id = response.json()["session_id"]
        print(f"\n✓ Session created: {session_id}")
        return session_id
    
    return None


def test_chat_message(session_id, message):
    """Send a chat message"""
    print_section(f"Sending Message: '{message[:50]}...'")
    
    payload = {
        "message": message,
        "session_id": session_id
    }
    
    response = requests.post(
        f"{BASE_URL}/chat/",
        headers=HEADERS,
        data=json.dumps(payload)
    )
    
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Phase: {data['current_phase']}")
        print(f"✓ Profile Completeness: {data['profile_completeness']:.1f}%")
        print(f"\nAssistant Response:")
        print(f"  {data['message']}\n")
        return data
    
    return None


def test_get_session_status(session_id):
    """Get session status"""
    print_section("Getting Session Status")
    
    response = requests.get(f"{BASE_URL}/sessions/{session_id}/status/")
    print_response(response)
    
    return response.status_code == 200


def simulate_full_interview():
    """Simulate a complete interview flow"""
    print("\n" + "🎯" * 30)
    print("  TALENTSCOUT API - FULL INTERVIEW SIMULATION")
    print("🎯" * 30)
    
    # 1. Health check
    if not test_health_check():
        print("\n❌ Health check failed!")
        return
    
    time.sleep(1)
    
    # 2. Start session
    session_id = test_start_session()
    if not session_id:
        print("\n❌ Failed to start session!")
        return
    
    time.sleep(1)
    
    # 3. Onboarding - Provide name and position
    test_chat_message(
        session_id,
        "Hi! My name is John Doe and I'm applying for the Senior Backend Engineer position."
    )
    time.sleep(1)
    
    # 4. Information Gathering - Provide experience
    test_chat_message(
        session_id,
        "I have 7 years of professional experience working with Python, Django, and PostgreSQL."
    )
    time.sleep(1)
    
    # 5. Information Gathering - Provide email and location
    test_chat_message(
        session_id,
        "My email is john.doe@example.com and I'm based in San Francisco, CA."
    )
    time.sleep(1)
    
    # 6. Technical Screening - Answer first question
    test_chat_message(
        session_id,
        "Sure! In my last project, I optimized a Django API by implementing database connection pooling "
        "and query optimization. I used select_related and prefetch_related to reduce N+1 queries, "
        "and added Redis caching for frequently accessed data. This reduced response times by 60%."
    )
    time.sleep(1)
    
    # 7. Technical Screening - Answer second question
    test_chat_message(
        session_id,
        "I would design a microservices architecture with separate services for user management, "
        "content delivery, and analytics. I'd use Django REST Framework for the APIs, PostgreSQL "
        "for relational data, Redis for caching, and implement a message queue like RabbitMQ for "
        "async tasks. For scalability, I'd containerize with Docker and deploy on Kubernetes."
    )
    time.sleep(1)
    
    # 8. Continue answering questions
    test_chat_message(
        session_id,
        "I follow test-driven development practices. I write unit tests with pytest, integration "
        "tests for APIs, and use coverage.py to ensure at least 80% code coverage. I also implement "
        "CI/CD pipelines with GitHub Actions to run tests automatically on every commit."
    )
    time.sleep(1)
    
    # 9. Get final session status
    test_get_session_status(session_id)
    
    print("\n" + "✓" * 60)
    print("  INTERVIEW SIMULATION COMPLETE!")
    print("✓" * 60 + "\n")
    
    print(f"Session ID: {session_id}")
    print(f"View in admin: http://localhost:8000/admin/")


def test_error_handling():
    """Test error handling with invalid inputs"""
    print_section("Testing Error Handling")
    
    # Test with empty message
    print("\n1. Testing empty message...")
    response = requests.post(
        f"{BASE_URL}/chat/",
        headers=HEADERS,
        data=json.dumps({"message": "", "session_id": None})
    )
    print(f"Status: {response.status_code} (Expected: 400)")
    
    # Test with invalid session ID
    print("\n2. Testing invalid session ID...")
    response = requests.post(
        f"{BASE_URL}/chat/",
        headers=HEADERS,
        data=json.dumps({
            "message": "Hello",
            "session_id": "00000000-0000-0000-0000-000000000000"
        })
    )
    print(f"Status: {response.status_code} (Expected: 404)")


if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 60)
    print("  TalentScout API Test Suite")
    print("=" * 60)
    print("\nMake sure the Django server is running:")
    print("  $ python manage.py runserver\n")
    
    try:
        # Run full interview simulation
        simulate_full_interview()
        
        # Test error handling
        time.sleep(2)
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("  All tests completed!")
        print("=" * 60 + "\n")
    
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to Django server!")
        print("Make sure the server is running on http://localhost:8000")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
