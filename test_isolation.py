
import os
import sys
import shutil

# Add src to path
sys.path.insert(0, os.path.abspath("src"))

from database.case_manager import CaseManager

def test_case_isolation():
    print("Testing Case Isolation...")
    
    # Use a temporary test data directory
    test_data_dir = "test_data_isolation"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    os.makedirs(test_data_dir)
    
    cm = CaseManager(test_data_dir)
    
    # User 1 creates a case
    print("User 1 creating case 'Case A'...")
    cm.create_case("Case A", "001", "User 1 Case", "Officer 1", user_id="user1")
    
    # User 2 creates a case
    print("User 2 creating case 'Case B'...")
    cm.create_case("Case B", "002", "User 2 Case", "Officer 2", user_id="user2")
    
    # Verify User 1 sees only Case A
    print("Verifying User 1 view...")
    cases_u1 = cm.get_all_cases(user_id="user1")
    print(f"User 1 cases: {[c[1] for c in cases_u1]}")
    assert len(cases_u1) == 1
    assert cases_u1[0][1] == "Case A"
    
    # Verify User 2 sees only Case B
    print("Verifying User 2 view...")
    cases_u2 = cm.get_all_cases(user_id="user2")
    print(f"User 2 cases: {[c[1] for c in cases_u2]}")
    assert len(cases_u2) == 1
    assert cases_u2[0][1] == "Case B"
    
    # Verify Admin (None) sees both
    print("Verifying Admin view (None)...")
    cases_all = cm.get_all_cases(user_id=None)
    print(f"All cases: {[c[1] for c in cases_all]}")
    assert len(cases_all) == 2
    
    print("\nSUCCESS: Case isolation logic verified!")
    
    # Cleanup
    shutil.rmtree(test_data_dir)

if __name__ == "__main__":
    test_case_isolation()
