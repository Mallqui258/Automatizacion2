#!/usr/bin/env python3
"""
Backend API Test Suite for CASM-83 R2014 Psychological Test
Tests all backend endpoints with comprehensive scenarios
"""

import requests
import json
import sys
from datetime import datetime

# Use the production URL from frontend/.env
BASE_URL = "https://evalpsych-app.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.session_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def test_get_questions(self):
        """Test GET /api/questions endpoint"""
        try:
            response = requests.get(f"{BASE_URL}/questions", timeout=10)
            
            if response.status_code != 200:
                self.log_test("GET /api/questions", False, 
                            f"Status code: {response.status_code}", response.text)
                return False
                
            data = response.json()
            
            # Verify structure
            if "questions" not in data:
                self.log_test("GET /api/questions", False, 
                            "Missing 'questions' field in response")
                return False
                
            questions = data["questions"]
            
            # Verify count (should be 143)
            if len(questions) != 143:
                self.log_test("GET /api/questions", False, 
                            f"Expected 143 questions, got {len(questions)}")
                return False
                
            # Verify structure of first question
            first_q = questions[0]
            required_fields = ["number", "block", "optionA", "optionB"]
            for field in required_fields:
                if field not in first_q:
                    self.log_test("GET /api/questions", False, 
                                f"Missing field '{field}' in question structure")
                    return False
                    
            # Verify blocks (should have 11 blocks)
            blocks = set(q["block"] for q in questions)
            if len(blocks) != 11:
                self.log_test("GET /api/questions", False, 
                            f"Expected 11 blocks, got {len(blocks)}")
                return False
                
            self.log_test("GET /api/questions", True, 
                        f"Retrieved {len(questions)} questions in {len(blocks)} blocks")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("GET /api/questions", False, "", str(e))
            return False
        except Exception as e:
            self.log_test("GET /api/questions", False, "", str(e))
            return False

    def test_start_test(self):
        """Test POST /api/start-test endpoint"""
        try:
            payload = {"sex": "masculino"}
            response = requests.post(f"{BASE_URL}/start-test", 
                                   json=payload, timeout=10)
            
            if response.status_code != 200:
                self.log_test("POST /api/start-test", False, 
                            f"Status code: {response.status_code}", response.text)
                return False
                
            data = response.json()
            
            # Verify response structure
            if "session_id" not in data:
                self.log_test("POST /api/start-test", False, 
                            "Missing 'session_id' in response")
                return False
                
            if "sex" not in data or data["sex"] != "masculino":
                self.log_test("POST /api/start-test", False, 
                            "Missing or incorrect 'sex' in response")
                return False
                
            # Store session_id for subsequent tests
            self.session_id = data["session_id"]
            
            # Verify session_id is UUID format
            if len(self.session_id) != 36 or self.session_id.count('-') != 4:
                self.log_test("POST /api/start-test", False, 
                            f"Session ID doesn't appear to be UUID format: {self.session_id}")
                return False
                
            self.log_test("POST /api/start-test", True, 
                        f"Created session: {self.session_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("POST /api/start-test", False, "", str(e))
            return False
        except Exception as e:
            self.log_test("POST /api/start-test", False, "", str(e))
            return False

    def test_save_response(self):
        """Test POST /api/save-response endpoint with different response types"""
        if not self.session_id:
            self.log_test("POST /api/save-response", False, 
                        "No session_id available from start-test")
            return False
            
        test_cases = [
            {"question_number": 1, "response": ["A"], "description": "Single option A"},
            {"question_number": 2, "response": ["B"], "description": "Single option B"},
            {"question_number": 3, "response": ["A", "B"], "description": "Both options"},
            {"question_number": 4, "response": [], "description": "Empty response"},
            {"question_number": 5, "response": ["A"], "description": "Another single option"}
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                payload = {
                    "session_id": self.session_id,
                    "question_number": test_case["question_number"],
                    "response": test_case["response"]
                }
                
                response = requests.post(f"{BASE_URL}/save-response", 
                                       json=payload, timeout=10)
                
                if response.status_code != 200:
                    self.log_test(f"POST /api/save-response ({test_case['description']})", 
                                False, f"Status code: {response.status_code}", response.text)
                    all_passed = False
                    continue
                    
                data = response.json()
                
                if not data.get("success"):
                    self.log_test(f"POST /api/save-response ({test_case['description']})", 
                                False, "Response success=False")
                    all_passed = False
                    continue
                    
                self.log_test(f"POST /api/save-response ({test_case['description']})", 
                            True, f"Saved response for question {test_case['question_number']}")
                            
            except requests.exceptions.RequestException as e:
                self.log_test(f"POST /api/save-response ({test_case['description']})", 
                            False, "", str(e))
                all_passed = False
            except Exception as e:
                self.log_test(f"POST /api/save-response ({test_case['description']})", 
                            False, "", str(e))
                all_passed = False
                
        return all_passed

    def test_get_test_session(self):
        """Test GET /api/test-session/{session_id} endpoint"""
        if not self.session_id:
            self.log_test("GET /api/test-session/{session_id}", False, 
                        "No session_id available")
            return False
            
        try:
            response = requests.get(f"{BASE_URL}/test-session/{self.session_id}", 
                                  timeout=10)
            
            if response.status_code != 200:
                self.log_test("GET /api/test-session/{session_id}", False, 
                            f"Status code: {response.status_code}", response.text)
                return False
                
            data = response.json()
            
            # Verify session structure
            required_fields = ["id", "sex", "responses", "created_at", "completed"]
            for field in required_fields:
                if field not in data:
                    self.log_test("GET /api/test-session/{session_id}", False, 
                                f"Missing field '{field}' in session")
                    return False
                    
            # Verify responses were saved
            responses = data["responses"]
            if len(responses) != 5:  # We saved 5 responses in previous test
                self.log_test("GET /api/test-session/{session_id}", False, 
                            f"Expected 5 responses, got {len(responses)}")
                return False
                
            # Verify response structure
            for response_item in responses:
                if "question_number" not in response_item or "response" not in response_item:
                    self.log_test("GET /api/test-session/{session_id}", False, 
                                "Invalid response structure")
                    return False
                    
            self.log_test("GET /api/test-session/{session_id}", True, 
                        f"Retrieved session with {len(responses)} responses")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("GET /api/test-session/{session_id}", False, "", str(e))
            return False
        except Exception as e:
            self.log_test("GET /api/test-session/{session_id}", False, "", str(e))
            return False

    def test_complete_test(self):
        """Test POST /api/complete-test endpoint"""
        if not self.session_id:
            self.log_test("POST /api/complete-test", False, 
                        "No session_id available")
            return False
            
        try:
            payload = {"session_id": self.session_id}
            response = requests.post(f"{BASE_URL}/complete-test", 
                                   json=payload, timeout=10)
            
            if response.status_code != 200:
                self.log_test("POST /api/complete-test", False, 
                            f"Status code: {response.status_code}", response.text)
                return False
                
            data = response.json()
            
            if not data.get("success"):
                self.log_test("POST /api/complete-test", False, 
                            "Response success=False")
                return False
                
            # Verify test is marked as completed
            session_response = requests.get(f"{BASE_URL}/test-session/{self.session_id}", 
                                          timeout=10)
            if session_response.status_code == 200:
                session_data = session_response.json()
                if not session_data.get("completed"):
                    self.log_test("POST /api/complete-test", False, 
                                "Test not marked as completed in database")
                    return False
                    
                if "completed_at" not in session_data:
                    self.log_test("POST /api/complete-test", False, 
                                "Missing completed_at timestamp")
                    return False
                    
            self.log_test("POST /api/complete-test", True, 
                        "Test marked as completed successfully")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("POST /api/complete-test", False, "", str(e))
            return False
        except Exception as e:
            self.log_test("POST /api/complete-test", False, "", str(e))
            return False

    def test_get_all_sessions(self):
        """Test GET /api/all-sessions endpoint"""
        try:
            response = requests.get(f"{BASE_URL}/all-sessions", timeout=10)
            
            if response.status_code != 200:
                self.log_test("GET /api/all-sessions", False, 
                            f"Status code: {response.status_code}", response.text)
                return False
                
            data = response.json()
            
            if "sessions" not in data:
                self.log_test("GET /api/all-sessions", False, 
                            "Missing 'sessions' field in response")
                return False
                
            sessions = data["sessions"]
            
            # Should have at least our test session
            if len(sessions) == 0:
                self.log_test("GET /api/all-sessions", False, 
                            "No sessions returned")
                return False
                
            # Find our test session
            our_session = None
            for session in sessions:
                if session.get("id") == self.session_id:
                    our_session = session
                    break
                    
            if not our_session:
                self.log_test("GET /api/all-sessions", False, 
                            "Our test session not found in all sessions")
                return False
                
            self.log_test("GET /api/all-sessions", True, 
                        f"Retrieved {len(sessions)} sessions including our test session")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("GET /api/all-sessions", False, "", str(e))
            return False
        except Exception as e:
            self.log_test("GET /api/all-sessions", False, "", str(e))
            return False

    def test_error_cases(self):
        """Test error handling scenarios"""
        all_passed = True
        
        # Test invalid session_id
        try:
            payload = {"session_id": "invalid-uuid"}
            response = requests.post(f"{BASE_URL}/save-response", 
                                   json={"session_id": "invalid-uuid", 
                                        "question_number": 1, "response": ["A"]}, 
                                   timeout=10)
            
            if response.status_code == 404:
                self.log_test("Error handling - Invalid session_id", True, 
                            "Correctly returned 404 for invalid session")
            else:
                self.log_test("Error handling - Invalid session_id", False, 
                            f"Expected 404, got {response.status_code}")
                all_passed = False
                
        except Exception as e:
            self.log_test("Error handling - Invalid session_id", False, "", str(e))
            all_passed = False
            
        # Test non-existent session for get
        try:
            response = requests.get(f"{BASE_URL}/test-session/non-existent-uuid", 
                                  timeout=10)
            
            if response.status_code == 404:
                self.log_test("Error handling - Non-existent session", True, 
                            "Correctly returned 404 for non-existent session")
            else:
                self.log_test("Error handling - Non-existent session", False, 
                            f"Expected 404, got {response.status_code}")
                all_passed = False
                
        except Exception as e:
            self.log_test("Error handling - Non-existent session", False, "", str(e))
            all_passed = False
            
        return all_passed

    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("CASM-83 R2014 Backend API Test Suite")
        print("=" * 60)
        print(f"Testing against: {BASE_URL}")
        print()
        
        # Run tests in order
        tests = [
            self.test_get_questions,
            self.test_start_test,
            self.test_save_response,
            self.test_get_test_session,
            self.test_complete_test,
            self.test_get_all_sessions,
            self.test_error_cases
        ]
        
        passed = 0
        total = 0
        
        for test_func in tests:
            if test_func():
                passed += 1
            total += 1
            
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            return True
        else:
            print(f"\n⚠️  {total - passed} TESTS FAILED")
            return False

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)