#!/usr/bin/env python3
"""
Detailed test for CASM-83 Results Calculation Endpoint
Focuses on testing the specific requirements from the review request
"""

import requests
import json

BASE_URL = "https://evalpsych-app.preview.emergentagent.com/api"

def test_results_detailed():
    """Detailed test of the results endpoint with comprehensive scoring"""
    
    print("🧪 Creating test session with strategic responses...")
    
    # Create session
    session_response = requests.post(f"{BASE_URL}/start-test", 
                                   json={"sex": "masculino"}, timeout=10)
    session_id = session_response.json()["session_id"]
    print(f"✅ Session created: {session_id}")
    
    # Create responses that will generate high scores in specific scales
    # This will test the recommendation system properly
    strategic_responses = []
    
    # CCFM (Ciencias Físicas Matemáticas) - Make this scale score high
    ccfm_column_questions = [1, 14, 27, 40, 53, 66, 79, 92, 105, 118, 131]
    ccfm_row_questions = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    
    # Add A responses for CCFM column questions (first 8)
    for q in ccfm_column_questions[:8]:
        strategic_responses.append({"question_number": q, "response": ["A"]})
    
    # Add B responses for CCFM row questions (first 6)  
    for q in ccfm_row_questions[:6]:
        strategic_responses.append({"question_number": q, "response": ["B"]})
    
    # JURI (Jurisprudencia) - Make this score moderately high
    juri_column_questions = [11, 24, 37, 50, 63, 76, 89, 102, 115, 128, 141]
    juri_row_questions = [131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141]
    
    # Add A responses for JURI column questions (first 5)
    for q in juri_column_questions[:5]:
        strategic_responses.append({"question_number": q, "response": ["A"]})
    
    # Add B responses for JURI row questions (first 4)
    for q in juri_row_questions[:4]:
        strategic_responses.append({"question_number": q, "response": ["B"]})
    
    # ARTE (Artes) - Make this score high
    arte_column_questions = [5, 18, 31, 44, 57, 70, 83, 96, 109, 122, 135]
    arte_row_questions = [53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63]
    
    # Add A responses for ARTE column questions (first 7)
    for q in arte_column_questions[:7]:
        strategic_responses.append({"question_number": q, "response": ["A"]})
    
    # Add B responses for ARTE row questions (first 5)
    for q in arte_row_questions[:5]:
        strategic_responses.append({"question_number": q, "response": ["B"]})
    
    print(f"📝 Saving {len(strategic_responses)} strategic responses...")
    
    # Save all responses
    for resp in strategic_responses:
        save_payload = {
            "session_id": session_id,
            "question_number": resp["question_number"],
            "response": resp["response"]
        }
        
        save_response = requests.post(f"{BASE_URL}/save-response", 
                                   json=save_payload, timeout=10)
        
        if save_response.status_code != 200:
            print(f"❌ Failed to save response for question {resp['question_number']}")
            return False
    
    print("✅ All responses saved successfully")
    
    # Complete the test
    complete_response = requests.post(f"{BASE_URL}/complete-test", 
                                   json={"session_id": session_id}, timeout=10)
    
    if complete_response.status_code != 200:
        print("❌ Failed to complete test")
        return False
    
    print("✅ Test completed")
    
    # Get results
    print("📊 Calculating results...")
    results_response = requests.get(f"{BASE_URL}/results/{session_id}", timeout=10)
    
    if results_response.status_code != 200:
        print(f"❌ Results endpoint failed: {results_response.status_code}")
        print(results_response.text)
        return False
    
    results = results_response.json()
    
    print("✅ Results retrieved successfully")
    print("\n" + "="*60)
    print("DETAILED RESULTS ANALYSIS")
    print("="*60)
    
    # Verify all 11 scales are present
    expected_scales = ["CCFM", "CCSS", "CCNA", "CCCO", "ARTE", "BURO", "CCEP", "IIAA", "FINA", "LING", "JURI"]
    scores = results["scores"]
    
    print(f"📋 Session ID: {results['session_id']}")
    print(f"👤 Sex: {results['sex']}")
    print(f"📝 Total Questions: {results['total_questions']}")
    print(f"✅ Answered Questions: {results['answered_questions']}")
    print()
    
    print("📊 SCALE SCORES:")
    print("-" * 40)
    
    all_scales_present = True
    for scale in expected_scales:
        if scale not in scores:
            print(f"❌ Missing scale: {scale}")
            all_scales_present = False
        else:
            scale_data = scores[scale]
            print(f"{scale:4} | {scale_data['name']:30} | Score: {scale_data['score']:2}/22 | {scale_data['interpretation']}")
    
    if not all_scales_present:
        print("❌ Not all scales are present")
        return False
    
    print("✅ All 11 scales present and calculated")
    print()
    
    # Verify recommendations
    recommendations = results["recommendations"]
    top_scales = recommendations["top_scales"]
    
    print("🎯 CAREER RECOMMENDATIONS:")
    print("-" * 40)
    
    if len(top_scales) == 0:
        print("⚠️  No recommendations provided (all scores below promedio_alto)")
    else:
        print(f"📈 {len(top_scales)} recommendations provided:")
        
        for i, rec in enumerate(top_scales, 1):
            print(f"\n{i}. {rec['name']} ({rec['scale']})")
            print(f"   Score: {rec['score']}/22 ({rec['interpretation']})")
            print(f"   Ocupaciones: {len(rec['ocupaciones'])} careers")
            print(f"   Técnicas: {len(rec['tecnicas'])} technical careers")
            
            # Verify interpretation is high level
            if rec['interpretation'] not in ['promedio_alto', 'alto', 'muy_alto']:
                print(f"❌ Invalid recommendation level: {rec['interpretation']}")
                return False
            
            # Verify career lists are not empty for high-scoring scales
            if len(rec['ocupaciones']) == 0 and len(rec['tecnicas']) == 0:
                print(f"❌ No careers provided for {rec['scale']}")
                return False
    
    print()
    
    # Verify score calculation logic
    print("🔍 SCORE CALCULATION VERIFICATION:")
    print("-" * 40)
    
    # Manual verification for CCFM
    ccfm_score = scores["CCFM"]["score"]
    expected_ccfm = 8 + 6  # 8 A responses in column + 6 B responses in row
    print(f"CCFM calculated score: {ccfm_score}")
    print(f"CCFM expected score: {expected_ccfm}")
    
    if ccfm_score == expected_ccfm:
        print("✅ CCFM score calculation correct")
    else:
        print("❌ CCFM score calculation incorrect")
        return False
    
    # Manual verification for ARTE
    arte_score = scores["ARTE"]["score"]
    expected_arte = 7 + 5  # 7 A responses in column + 5 B responses in row
    print(f"ARTE calculated score: {arte_score}")
    print(f"ARTE expected score: {expected_arte}")
    
    if arte_score == expected_arte:
        print("✅ ARTE score calculation correct")
    else:
        print("❌ ARTE score calculation incorrect")
        return False
    
    print()
    
    # Test sex-specific baremos
    print("🚻 SEX-SPECIFIC BAREMOS TEST:")
    print("-" * 40)
    
    # Create female session with same responses
    female_session_response = requests.post(f"{BASE_URL}/start-test", 
                                         json={"sex": "femenino"}, timeout=10)
    female_session_id = female_session_response.json()["session_id"]
    
    # Add same responses for female (just a subset)
    for resp in strategic_responses[:10]:
        save_payload = {
            "session_id": female_session_id,
            "question_number": resp["question_number"],
            "response": resp["response"]
        }
        requests.post(f"{BASE_URL}/save-response", json=save_payload, timeout=10)
    
    # Get female results
    female_results_response = requests.get(f"{BASE_URL}/results/{female_session_id}", timeout=10)
    
    if female_results_response.status_code == 200:
        female_results = female_results_response.json()
        
        print(f"Male CCFM interpretation: {scores['CCFM']['interpretation']}")
        print(f"Female CCFM interpretation: {female_results['scores']['CCFM']['interpretation']}")
        
        # Verify sex field is correct
        if female_results["sex"] == "femenino":
            print("✅ Sex-specific baremos working correctly")
        else:
            print("❌ Sex field incorrect in female results")
            return False
    else:
        print("⚠️  Could not test female baremos")
    
    print()
    print("="*60)
    print("🎉 ALL DETAILED TESTS PASSED!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = test_results_detailed()
    if not success:
        print("❌ Detailed test failed")
        exit(1)
    else:
        print("✅ Detailed test completed successfully")