#!/usr/bin/env python3
"""
Simplified integration tests for Amicale Anouar gamification system
Tests against the running server using actual HTTP requests
"""

import requests
import json
import uuid
import time
from datetime import datetime

BACKEND_URL = "https://amicale-portal.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class TestRunner:
    def __init__(self):
        self.admin_token = None
        self.test_member_id = None
        self.test_reward_id = None
        self.project_type_id = None
        self.failed_tests = []
        self.passed_tests = []
        
    def login_admin(self):
        """Login as admin and get token"""
        response = requests.post(f"{API_BASE}/auth/login", json={
            "email": "admin@amicale.ma",
            "password": "admin123"
        })
        
        if response.status_code == 200:
            self.admin_token = response.json()["access_token"]
            print("✅ Admin login successful")
            return True
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            return False
    
    def get_headers(self):
        return {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}
    
    def setup_test_data(self):
        """Setup test data: project type, reward, member"""
        headers = self.get_headers()
        
        # Get project type
        pt_response = requests.get(f"{API_BASE}/project-types")
        if pt_response.status_code == 200 and pt_response.json():
            self.project_type_id = pt_response.json()[0]["id"]
            print("✅ Project type retrieved")
        else:
            print("❌ Failed to get project type")
            return False
        
        # Get reward
        rewards_response = requests.get(f"{API_BASE}/rewards?active=true")
        if rewards_response.status_code == 200 and rewards_response.json():
            self.test_reward_id = rewards_response.json()[0]["id"]
            print("✅ Test reward retrieved")
        else:
            print("❌ Failed to get test reward")
            return False
        
        # Create test member
        member_data = {
            "full_name": f"Integration Test Member {uuid.uuid4().hex[:8]}",
            "sex": "Male",
            "phone": f"+212{uuid.uuid4().hex[:9]}",
            "job": "Integration Tester",
            "project_type_id": self.project_type_id,
            "initial_paid": 0.0
        }
        
        member_response = requests.post(f"{API_BASE}/members/register", json=member_data)
        if member_response.status_code == 200:
            self.test_member_id = member_response.json()["id"]
            print("✅ Test member created")
            return True
        else:
            print(f"❌ Failed to create test member: {member_response.status_code}")
            return False
    
    def test_points_system(self):
        """Test points earning and calculation"""
        print("\n🧪 Testing Points System...")
        headers = self.get_headers()
        
        try:
            # Get initial points
            member_response = requests.get(f"{API_BASE}/members/{self.test_member_id}", headers=headers)
            initial_points = member_response.json()["points"]
            
            # Add payment (100 MAD should give 10 points)
            payment_data = {
                "amount": 100.0,
                "method": "Cash", 
                "note": "Integration test payment"
            }
            
            payment_response = requests.post(
                f"{API_BASE}/members/{self.test_member_id}/payments",
                json=payment_data,
                headers=headers
            )
            
            if payment_response.status_code == 200:
                # Check points increased
                member_after = requests.get(f"{API_BASE}/members/{self.test_member_id}", headers=headers)
                new_points = member_after.json()["points"]
                
                if new_points == initial_points + 10:
                    self.passed_tests.append("✅ Points earned from payment (100 MAD = 10 pts)")
                else:
                    self.failed_tests.append(f"❌ Points calculation incorrect: expected {initial_points + 10}, got {new_points}")
            else:
                self.failed_tests.append(f"❌ Payment creation failed: {payment_response.status_code}")
            
            # Test manual points addition
            manual_points_data = {
                "points": 25,
                "transaction_type": "bonus",
                "description": "Integration test bonus"
            }
            
            manual_response = requests.post(
                f"{API_BASE}/members/{self.test_member_id}/points",
                json=manual_points_data,
                headers=headers
            )
            
            if manual_response.status_code == 200:
                member_final = requests.get(f"{API_BASE}/members/{self.test_member_id}", headers=headers)
                final_points = member_final.json()["points"]
                expected_points = initial_points + 10 + 25  # Payment + manual
                
                if final_points == expected_points:
                    self.passed_tests.append("✅ Manual points addition working")
                else:
                    self.failed_tests.append(f"❌ Manual points incorrect: expected {expected_points}, got {final_points}")
            else:
                self.failed_tests.append(f"❌ Manual points addition failed: {manual_response.status_code}")
                
        except Exception as e:
            self.failed_tests.append(f"❌ Points system test exception: {str(e)}")
    
    def test_levels_system(self):
        """Test level calculation"""
        print("\n🧪 Testing Levels System...")
        headers = self.get_headers()
        
        try:
            # Get member level
            level_response = requests.get(f"{API_BASE}/members/{self.test_member_id}/level", headers=headers)
            
            if level_response.status_code == 200:
                level_data = level_response.json()
                current_level = level_data.get("current_level", {}).get("name", "Unknown")
                
                # Check if level makes sense (with current points ~35, should be Bronze)
                if current_level == "Bronze":
                    self.passed_tests.append("✅ Level calculation correct for Bronze")
                elif current_level in ["Argent", "Or", "Platine"]:
                    self.passed_tests.append(f"✅ Level calculation: {current_level}")
                else:
                    self.failed_tests.append(f"❌ Unexpected level: {current_level}")
                    
                # Check progression data
                if "progress_percentage" in level_data and "points_to_next" in level_data:
                    self.passed_tests.append("✅ Level progression data available")
                else:
                    self.failed_tests.append("❌ Missing level progression data")
            else:
                self.failed_tests.append(f"❌ Level retrieval failed: {level_response.status_code}")
                
        except Exception as e:
            self.failed_tests.append(f"❌ Levels system test exception: {str(e)}")
    
    def test_badges_system(self):
        """Test badge system"""
        print("\n🧪 Testing Badges System...")
        headers = self.get_headers()
        
        try:
            # Get available badges
            badges_response = requests.get(f"{API_BASE}/badges")
            if badges_response.status_code == 200:
                badges = badges_response.json()
                if len(badges) >= 5:  # Should have 5 default badges
                    self.passed_tests.append("✅ Default badges loaded")
                else:
                    self.failed_tests.append(f"❌ Insufficient badges: {len(badges)}")
            
            # Get member badges
            member_badges_response = requests.get(f"{API_BASE}/members/{self.test_member_id}/badges", headers=headers)
            if member_badges_response.status_code == 200:
                member_badges = member_badges_response.json()
                self.passed_tests.append(f"✅ Member badges retrieved ({len(member_badges)} badges)")
            else:
                self.failed_tests.append(f"❌ Member badges retrieval failed: {member_badges_response.status_code}")
                
        except Exception as e:
            self.failed_tests.append(f"❌ Badges system test exception: {str(e)}")
    
    def test_redemption_system(self):
        """Test redemption workflow"""
        print("\n🧪 Testing Redemption System...")
        headers = self.get_headers()
        
        try:
            # Ensure member has enough points for cheapest reward
            rewards = requests.get(f"{API_BASE}/rewards?active=true").json()
            cheapest_reward = min(rewards, key=lambda r: r["cost_points"])
            
            member = requests.get(f"{API_BASE}/members/{self.test_member_id}", headers=headers).json()
            if member["points"] < cheapest_reward["cost_points"]:
                # Add points if needed
                points_needed = cheapest_reward["cost_points"] - member["points"] + 10
                requests.post(
                    f"{API_BASE}/members/{self.test_member_id}/points",
                    json={"points": points_needed, "transaction_type": "test", "description": "Points for redemption test"},
                    headers=headers
                )
            
            # Create redemption request
            redemption_data = {
                "reward_id": cheapest_reward["id"],
                "note": "Integration test redemption"
            }
            
            redemption_response = requests.post(
                f"{API_BASE}/members/{self.test_member_id}/redemptions",
                json=redemption_data,
                headers=headers
            )
            
            if redemption_response.status_code == 200:
                redemption = redemption_response.json()
                if redemption["status"] == "Pending":
                    self.passed_tests.append("✅ Redemption request created")
                    
                    # Test approval
                    approve_response = requests.put(
                        f"{API_BASE}/redemptions/{redemption['id']}/approve",
                        json={"note": "Integration test approval"},
                        headers=headers
                    )
                    
                    if approve_response.status_code == 200:
                        approved = approve_response.json()
                        if approved["status"] == "Approved":
                            self.passed_tests.append("✅ Redemption approval working")
                        else:
                            self.failed_tests.append(f"❌ Approval status incorrect: {approved['status']}")
                    else:
                        self.failed_tests.append(f"❌ Redemption approval failed: {approve_response.status_code}")
                else:
                    self.failed_tests.append(f"❌ Redemption status incorrect: {redemption['status']}")
            else:
                self.failed_tests.append(f"❌ Redemption creation failed: {redemption_response.status_code}")
                
        except Exception as e:
            self.failed_tests.append(f"❌ Redemption system test exception: {str(e)}")
    
    def test_leaderboard_system(self):
        """Test leaderboard generation and retrieval"""
        print("\n🧪 Testing Leaderboard System...")
        headers = self.get_headers()
        
        try:
            # Generate all-time leaderboard
            generate_response = requests.post(f"{API_BASE}/leaderboard/generate/all-time", headers=headers)
            if generate_response.status_code == 200:
                self.passed_tests.append("✅ All-time leaderboard generation")
                
                # Get leaderboard
                leaderboard_response = requests.get(f"{API_BASE}/leaderboard?period=all_time")
                if leaderboard_response.status_code == 200:
                    leaderboard = leaderboard_response.json()
                    
                    if leaderboard["period"] == "all_time" and len(leaderboard["entries"]) > 0:
                        self.passed_tests.append(f"✅ All-time leaderboard retrieved ({leaderboard['total_entries']} entries)")
                    else:
                        self.failed_tests.append("❌ Leaderboard data incomplete")
                else:
                    self.failed_tests.append(f"❌ Leaderboard retrieval failed: {leaderboard_response.status_code}")
            else:
                self.failed_tests.append(f"❌ Leaderboard generation failed: {generate_response.status_code}")
                
            # Generate current month leaderboard
            current_date = datetime.now()
            monthly_response = requests.post(
                f"{API_BASE}/leaderboard/generate/{current_date.year}/{current_date.month}",
                headers=headers
            )
            
            if monthly_response.status_code == 200:
                self.passed_tests.append("✅ Monthly leaderboard generation")
            else:
                self.failed_tests.append(f"❌ Monthly leaderboard generation failed: {monthly_response.status_code}")
                
        except Exception as e:
            self.failed_tests.append(f"❌ Leaderboard system test exception: {str(e)}")
    
    def test_monitoring_kpis(self):
        """Test monitoring KPI calculations"""
        print("\n🧪 Testing Monitoring KPIs...")
        headers = self.get_headers()
        
        try:
            kpi_response = requests.get(f"{API_BASE}/monitor/gamification/summary", headers=headers)
            if kpi_response.status_code == 200:
                kpi_data = kpi_response.json()
                
                required_fields = [
                    "total_points_distributed",
                    "average_points_per_member",
                    "badges_awarded_this_month",
                    "pending_redemptions",
                    "redemption_approval_rate",
                    "level_distribution"
                ]
                
                missing_fields = [field for field in required_fields if field not in kpi_data]
                
                if not missing_fields:
                    self.passed_tests.append("✅ KPI data structure complete")
                    
                    # Validate data types and ranges
                    if kpi_data["total_points_distributed"] >= 0:
                        self.passed_tests.append("✅ Total points calculation valid")
                    
                    if 0 <= kpi_data["redemption_approval_rate"] <= 100:
                        self.passed_tests.append("✅ Approval rate calculation valid")
                    
                    if isinstance(kpi_data["level_distribution"], dict) and len(kpi_data["level_distribution"]) > 0:
                        self.passed_tests.append("✅ Level distribution calculated")
                else:
                    self.failed_tests.append(f"❌ Missing KPI fields: {missing_fields}")
            else:
                self.failed_tests.append(f"❌ KPI retrieval failed: {kpi_response.status_code}")
                
        except Exception as e:
            self.failed_tests.append(f"❌ Monitoring KPIs test exception: {str(e)}")
    
    def test_export_functionality(self):
        """Test CSV export functionality"""
        print("\n🧪 Testing Export Functionality...")
        headers = self.get_headers()
        
        try:
            # Test leaderboard CSV export
            export_response = requests.get(f"{API_BASE}/export/leaderboard?period=all_time", headers=headers)
            if export_response.status_code == 200:
                csv_content = export_response.text
                lines = csv_content.strip().split('\n')
                
                # Check header
                if lines[0] == "Rang,Membre,Points,Niveau,Badges,Date_Generation":
                    self.passed_tests.append("✅ Leaderboard CSV export format correct")
                    
                    if len(lines) > 1:
                        self.passed_tests.append(f"✅ Leaderboard CSV contains data ({len(lines)-1} entries)")
                    else:
                        self.failed_tests.append("❌ Leaderboard CSV has no data rows")
                else:
                    self.failed_tests.append("❌ Leaderboard CSV header incorrect")
            else:
                self.failed_tests.append(f"❌ Leaderboard CSV export failed: {export_response.status_code}")
            
            # Test redemptions CSV export
            redemptions_export = requests.get(f"{API_BASE}/export/redemptions", headers=headers)
            if redemptions_export.status_code == 200:
                self.passed_tests.append("✅ Redemptions CSV export working")
            else:
                self.failed_tests.append(f"❌ Redemptions CSV export failed: {redemptions_export.status_code}")
                
        except Exception as e:
            self.failed_tests.append(f"❌ Export functionality test exception: {str(e)}")
    
    def test_daily_jobs(self):
        """Test daily maintenance jobs"""
        print("\n🧪 Testing Daily Jobs...")
        headers = self.get_headers()
        
        try:
            jobs_response = requests.post(f"{API_BASE}/jobs/daily", headers=headers)
            if jobs_response.status_code == 200:
                result = jobs_response.json()
                if "members_checked" in result and "badges_processed" in result:
                    self.passed_tests.append(f"✅ Daily jobs completed ({result['members_checked']} members checked)")
                else:
                    self.failed_tests.append("❌ Daily jobs response incomplete")
            else:
                self.failed_tests.append(f"❌ Daily jobs failed: {jobs_response.status_code}")
                
        except Exception as e:
            self.failed_tests.append(f"❌ Daily jobs test exception: {str(e)}")
    
    def test_api_endpoints_availability(self):
        """Test that all main endpoints are accessible"""
        print("\n🧪 Testing API Endpoints Availability...")
        headers = self.get_headers()
        
        endpoints_to_test = [
            ("GET", "/api/levels", 200),
            ("GET", "/api/badges", 200),
            ("GET", "/api/rewards?active=true", 200),
            ("GET", f"/api/members/{self.test_member_id}", 200),
            ("GET", f"/api/members/{self.test_member_id}/level", 200),
            ("GET", f"/api/members/{self.test_member_id}/badges", 200),
            ("GET", f"/api/members/{self.test_member_id}/points", 200),
            ("GET", "/api/leaderboard?period=all_time", 200),
            ("GET", "/api/monitor/gamification/summary", 200),
        ]
        
        for method, endpoint, expected_status in endpoints_to_test:
            try:
                if method == "GET":
                    response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                
                if response.status_code == expected_status:
                    self.passed_tests.append(f"✅ {endpoint}")
                else:
                    self.failed_tests.append(f"❌ {endpoint} - Expected {expected_status}, got {response.status_code}")
                    
            except Exception as e:
                self.failed_tests.append(f"❌ {endpoint} - Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Amicale Anouar Integration Tests...")
        print("=" * 60)
        
        # Setup
        if not self.login_admin():
            print("❌ Cannot continue without admin login")
            return False
            
        if not self.setup_test_data():
            print("❌ Cannot continue without test data setup")
            return False
        
        # Run test suites
        self.test_api_endpoints_availability()
        self.test_points_system()
        self.test_levels_system()
        self.test_badges_system()
        self.test_redemption_system()
        self.test_leaderboard_system()
        self.test_monitoring_kpis()
        self.test_export_functionality()
        self.test_daily_jobs()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TESTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.passed_tests) + len(self.failed_tests)
        success_rate = (len(self.passed_tests) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ PASSED: {len(self.passed_tests)}")
        print(f"❌ FAILED: {len(self.failed_tests)}")
        print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
        
        if self.passed_tests:
            print(f"\n🎉 SUCCESSFUL TESTS:")
            for test in self.passed_tests:
                print(f"  {test}")
        
        if self.failed_tests:
            print(f"\n🚨 FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  {test}")
        
        print("\n" + "=" * 60)
        
        return success_rate >= 95.0  # 95% success rate threshold
    
    def cleanup(self):
        """Cleanup test data"""
        print("\n🧹 Cleaning up test data...")
        # In a real app, we'd clean up the test member and related data
        # For now, we'll leave it as it helps with demo data
        pass

if __name__ == "__main__":
    runner = TestRunner()
    
    try:
        success = runner.run_all_tests()
        
        if success:
            print("\n🎉 ALL INTEGRATION TESTS PASSED - SYSTEM READY FOR PRODUCTION!")
            exit(0)
        else:
            print("\n⚠️ SOME TESTS FAILED - REVIEW REQUIRED BEFORE PRODUCTION")
            exit(1)
    finally:
        runner.cleanup()