#!/usr/bin/env python3
"""
Debug the CASM-83 scoring system to understand the calculation
"""

import requests
import json

BASE_URL = "https://evalpsych-app.preview.emergentagent.com/api"

# Copy the scale mapping from the backend
SCALE_MAPPING = {
    "CCFM": {
        "name": "Ciencias Físicas Matemáticas",
        "column": [1, 14, 27, 40, 53, 66, 79, 92, 105, 118, 131],  # Opción A
        "row": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]  # Opción B
    },
    "CCSS": {
        "name": "Ciencias Sociales",
        "column": [2, 15, 28, 41, 54, 67, 80, 93, 106, 119, 132],
        "row": [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    },
    "CCNA": {
        "name": "Ciencias Naturales",
        "column": [3, 16, 29, 42, 55, 68, 81, 94, 107, 120, 133],
        "row": [27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]
    },
    "CCCO": {
        "name": "Ciencias de la Comunicación",
        "column": [4, 17, 30, 43, 56, 69, 82, 95, 108, 121, 134],
        "row": [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
    },
    "ARTE": {
        "name": "Artes",
        "column": [5, 18, 31, 44, 57, 70, 83, 96, 109, 122, 135],
        "row": [53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63]
    },
    "BURO": {
        "name": "Burocracia",
        "column": [6, 19, 32, 45, 58, 71, 84, 97, 110, 123, 136],
        "row": [66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76]
    },
    "CCEP": {
        "name": "Ciencias Económicas Políticas",
        "column": [7, 20, 33, 46, 59, 72, 85, 98, 111, 124, 137],
        "row": [79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89]
    },
    "IIAA": {
        "name": "Institutos Armados",
        "column": [8, 21, 34, 47, 60, 73, 86, 99, 112, 125, 138],
        "row": [92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102]
    },
    "FINA": {
        "name": "Finanzas",
        "column": [9, 22, 35, 48, 61, 74, 87, 100, 113, 126, 139],
        "row": [105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115]
    },
    "LING": {
        "name": "Lingüística",
        "column": [10, 23, 36, 49, 62, 75, 88, 101, 114, 127, 140],
        "row": [118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128]
    },
    "JURI": {
        "name": "Jurisprudencia",
        "column": [11, 24, 37, 50, 63, 76, 89, 102, 115, 128, 141],
        "row": [131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141]
    }
}

def debug_scoring():
    """Debug the scoring system"""
    
    print("🔍 DEBUGGING CASM-83 SCORING SYSTEM")
    print("="*50)
    
    # Create session
    session_response = requests.post(f"{BASE_URL}/start-test", 
                                   json={"sex": "masculino"}, timeout=10)
    session_id = session_response.json()["session_id"]
    print(f"Session created: {session_id}")
    
    # Let's focus on CCFM and create very specific responses
    print("\n📊 CCFM Scale Analysis:")
    print(f"Column questions (need A): {SCALE_MAPPING['CCFM']['column']}")
    print(f"Row questions (need B): {SCALE_MAPPING['CCFM']['row']}")
    
    # Notice the overlap! Question 1 is in both column and row for CCFM
    # This means if we answer A to question 1, it counts for CCFM column
    # But if we answer B to question 1, it counts for CCFM row
    # We can't get both!
    
    print("\n⚠️  OVERLAP DETECTED:")
    print("Question 1 is in both CCFM column and CCFM row!")
    print("This means we can only get 1 point from question 1, not 2")
    
    # Let's create strategic responses avoiding overlaps
    responses = []
    
    # CCFM column responses (A) - skip question 1 since it overlaps
    ccfm_column_no_overlap = [14, 27, 40, 53, 66, 79, 92, 105, 118, 131]  # removed 1
    for q in ccfm_column_no_overlap[:8]:  # Take 8
        responses.append({"question_number": q, "response": ["A"]})
    
    # CCFM row responses (B) - include question 1 and others that don't overlap
    ccfm_row_no_overlap = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]  # all are fine
    for q in ccfm_row_no_overlap[:3]:  # Take 3
        responses.append({"question_number": q, "response": ["B"]})
    
    print(f"\n📝 Saving {len(responses)} strategic responses...")
    print("Expected CCFM score: 8 (column A) + 3 (row B) = 11")
    
    # Save responses
    for resp in responses:
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
    
    # Complete test
    requests.post(f"{BASE_URL}/complete-test", 
                 json={"session_id": session_id}, timeout=10)
    
    # Get results
    results_response = requests.get(f"{BASE_URL}/results/{session_id}", timeout=10)
    results = results_response.json()
    
    ccfm_score = results["scores"]["CCFM"]["score"]
    print(f"\n✅ Actual CCFM score: {ccfm_score}")
    print(f"Expected CCFM score: 11")
    
    if ccfm_score == 11:
        print("✅ Score calculation is correct!")
    else:
        print("❌ Score calculation mismatch")
        
        # Let's debug by checking what responses were actually saved
        session_response = requests.get(f"{BASE_URL}/test-session/{session_id}", timeout=10)
        session_data = session_response.json()
        
        print(f"\n🔍 Saved responses: {len(session_data['responses'])}")
        for resp in session_data['responses']:
            q_num = resp['question_number']
            response = resp['response']
            
            # Check if this question affects CCFM
            in_ccfm_column = q_num in SCALE_MAPPING['CCFM']['column']
            in_ccfm_row = q_num in SCALE_MAPPING['CCFM']['row']
            
            if in_ccfm_column or in_ccfm_row:
                points = 0
                if in_ccfm_column and 'A' in response:
                    points += 1
                if in_ccfm_row and 'B' in response:
                    points += 1
                    
                print(f"Q{q_num}: {response} -> CCFM points: {points} (col: {in_ccfm_column}, row: {in_ccfm_row})")
    
    return True

if __name__ == "__main__":
    debug_scoring()