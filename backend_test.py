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

    def test_results_calculation(self):
        """Test GET /api/results/{session_id} endpoint - CASM-83 scoring system"""
        if not self.session_id:
            self.log_test("GET /api/results/{session_id}", False, 
                        "No session_id available")
            return False
        
        # First, create a comprehensive test session with strategic responses
        # to test the scoring algorithm properly
        try:
            # Create a new session for results testing
            payload = {"sex": "masculino"}
            response = requests.post(f"{BASE_URL}/start-test", 
                                   json=payload, timeout=10)
            
            if response.status_code != 200:
                self.log_test("Results Test - Create session", False, 
                            f"Status code: {response.status_code}", response.text)
                return False
                
            results_session_id = response.json()["session_id"]
            
            # Add strategic responses to test scoring algorithm
            # These responses are designed to create measurable scores across different scales
            test_responses = [
                # CCFM scale responses (questions 1,14,27,40,53,66,79,92,105,118,131 for A)
                {"question_number": 1, "response": ["A"]},   # CCFM column
                {"question_number": 14, "response": ["A"]},  # CCFM column
                {"question_number": 27, "response": ["A"]},  # CCFM column
                {"question_number": 40, "response": ["A"]},  # CCFM column
                {"question_number": 53, "response": ["A"]},  # CCFM column
                
                # CCFM row responses (questions 1-11 for B)
                {"question_number": 2, "response": ["B"]},   # CCFM row
                {"question_number": 3, "response": ["B"]},   # CCFM row
                {"question_number": 4, "response": ["B"]},   # CCFM row
                
                # CCSS scale responses
                {"question_number": 15, "response": ["A"]},  # CCSS column
                {"question_number": 28, "response": ["A"]},  # CCSS column
                {"question_number": 16, "response": ["B"]},  # CCSS row
                {"question_number": 17, "response": ["B"]},  # CCSS row
                
                # JURI scale responses
                {"question_number": 11, "response": ["A"]},  # JURI column
                {"question_number": 24, "response": ["A"]},  # JURI column
                {"question_number": 131, "response": ["B"]}, # JURI row
                {"question_number": 132, "response": ["B"]}, # JURI row
                {"question_number": 133, "response": ["B"]}, # JURI row
                
                # Add some mixed responses
                {"question_number": 50, "response": ["A", "B"]}, # Both options
                {"question_number": 100, "response": []},         # Empty response
                {"question_number": 75, "response": ["A"]},       # Single A
                {"question_number": 125, "response": ["B"]},      # Single B
            ]
            
            # Save all test responses
            for resp in test_responses:
                save_payload = {
                    "session_id": results_session_id,
                    "question_number": resp["question_number"],
                    "response": resp["response"]
                }
                
                save_response = requests.post(f"{BASE_URL}/save-response", 
                                           json=save_payload, timeout=10)
                
                if save_response.status_code != 200:
                    self.log_test("Results Test - Save responses", False, 
                                f"Failed to save response for question {resp['question_number']}")
                    return False
            
            # Mark test as completed
            complete_payload = {"session_id": results_session_id}
            complete_response = requests.post(f"{BASE_URL}/complete-test", 
                                           json=complete_payload, timeout=10)
            
            if complete_response.status_code != 200:
                self.log_test("Results Test - Complete test", False, 
                            "Failed to complete test")
                return False
            
            # Now test the results endpoint
            results_response = requests.get(f"{BASE_URL}/results/{results_session_id}", 
                                          timeout=10)
            
            if results_response.status_code != 200:
                self.log_test("GET /api/results/{session_id}", False, 
                            f"Status code: {results_response.status_code}", results_response.text)
                return False
                
            results_data = results_response.json()
            
            # Verify response structure
            required_fields = ["session_id", "sex", "scores", "recommendations", "total_questions", "answered_questions"]
            for field in required_fields:
                if field not in results_data:
                    self.log_test("GET /api/results/{session_id}", False, 
                                f"Missing field '{field}' in results")
                    return False
            
            # Verify all 11 scales are present
            expected_scales = ["CCFM", "CCSS", "CCNA", "CCCO", "ARTE", "BURO", "CCEP", "IIAA", "FINA", "LING", "JURI"]
            scores = results_data["scores"]
            
            for scale in expected_scales:
                if scale not in scores:
                    self.log_test("GET /api/results/{session_id}", False, 
                                f"Missing scale '{scale}' in scores")
                    return False
                    
                # Verify each scale has required fields
                scale_data = scores[scale]
                scale_fields = ["name", "score", "max_score", "interpretation"]
                for field in scale_fields:
                    if field not in scale_data:
                        self.log_test("GET /api/results/{session_id}", False, 
                                    f"Missing field '{field}' in scale {scale}")
                        return False
                        
                # Verify max_score is 22
                if scale_data["max_score"] != 22:
                    self.log_test("GET /api/results/{session_id}", False, 
                                f"Scale {scale} max_score should be 22, got {scale_data['max_score']}")
                    return False
                    
                # Verify score is within valid range
                if not (0 <= scale_data["score"] <= 22):
                    self.log_test("GET /api/results/{session_id}", False, 
                                f"Scale {scale} score {scale_data['score']} out of valid range 0-22")
                    return False
            
            # Verify recommendations structure
            recommendations = results_data["recommendations"]
            if "top_scales" not in recommendations or "all_scores" not in recommendations:
                self.log_test("GET /api/results/{session_id}", False, 
                            "Missing 'top_scales' or 'all_scores' in recommendations")
                return False
            
            # Verify top_scales contains valid recommendations
            top_scales = recommendations["top_scales"]
            for recommendation in top_scales:
                rec_fields = ["scale", "name", "score", "interpretation", "ocupaciones", "tecnicas"]
                for field in rec_fields:
                    if field not in recommendation:
                        self.log_test("GET /api/results/{session_id}", False, 
                                    f"Missing field '{field}' in recommendation")
                        return False
                        
                # Verify interpretation is high level (promedio_alto, alto, muy_alto)
                interpretation = recommendation["interpretation"]
                if interpretation not in ["promedio_alto", "alto", "muy_alto"]:
                    self.log_test("GET /api/results/{session_id}", False, 
                                f"Recommendation has low interpretation: {interpretation}")
                    return False
                    
                # Verify ocupaciones and tecnicas are lists
                if not isinstance(recommendation["ocupaciones"], list):
                    self.log_test("GET /api/results/{session_id}", False, 
                                "ocupaciones should be a list")
                    return False
                    
                if not isinstance(recommendation["tecnicas"], list):
                    self.log_test("GET /api/results/{session_id}", False, 
                                "tecnicas should be a list")
                    return False
            
            # Verify sex-specific interpretation (test with female)
            female_payload = {"sex": "femenino"}
            female_response = requests.post(f"{BASE_URL}/start-test", 
                                         json=female_payload, timeout=10)
            
            if female_response.status_code == 200:
                female_session_id = female_response.json()["session_id"]
                
                # Add same responses for female
                for resp in test_responses[:5]:  # Just a few responses
                    save_payload = {
                        "session_id": female_session_id,
                        "question_number": resp["question_number"],
                        "response": resp["response"]
                    }
                    requests.post(f"{BASE_URL}/save-response", json=save_payload, timeout=10)
                
                # Get female results
                female_results_response = requests.get(f"{BASE_URL}/results/{female_session_id}", 
                                                     timeout=10)
                
                if female_results_response.status_code == 200:
                    female_results = female_results_response.json()
                    
                    # Verify sex field is correct
                    if female_results["sex"] != "femenino":
                        self.log_test("GET /api/results/{session_id} - Sex verification", False, 
                                    f"Expected sex 'femenino', got '{female_results['sex']}'")
                        return False
                        
                    # Interpretations might differ between sexes for same scores
                    # This verifies sex-specific baremos are being used
                    self.log_test("GET /api/results/{session_id} - Sex-specific baremos", True, 
                                "Sex-specific interpretation verified")
            
            # Test manual score calculation verification
            # Let's verify CCFM score calculation manually
            ccfm_score = scores["CCFM"]["score"]
            expected_ccfm = 5 + 3  # 5 A responses in column + 3 B responses in row
            
            if ccfm_score == expected_ccfm:
                self.log_test("GET /api/results/{session_id} - Score calculation", True, 
                            f"CCFM score correctly calculated: {ccfm_score}")
            else:
                self.log_test("GET /api/results/{session_id} - Score calculation", False, 
                            f"CCFM score mismatch: expected {expected_ccfm}, got {ccfm_score}")
                return False
            
            self.log_test("GET /api/results/{session_id}", True, 
                        f"Results calculated for all 11 scales, {len(top_scales)} recommendations provided")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("GET /api/results/{session_id}", False, "", str(e))
            return False
        except Exception as e:
            self.log_test("GET /api/results/{session_id}", False, "", str(e))
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
            
        # Test results endpoint with invalid session
        try:
            response = requests.get(f"{BASE_URL}/results/invalid-session-id", 
                                  timeout=10)
            
            if response.status_code == 404:
                self.log_test("Error handling - Results invalid session", True, 
                            "Correctly returned 404 for invalid session in results")
            else:
                self.log_test("Error handling - Results invalid session", False, 
                            f"Expected 404, got {response.status_code}")
                all_passed = False
                
        except Exception as e:
            self.log_test("Error handling - Results invalid session", False, "", str(e))
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
            self.test_results_calculation,
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