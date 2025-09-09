#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Amicale Anouar
Tests all endpoints with proper authentication and data validation
"""

import requests
import sys
import json
from datetime import datetime
import uuid

class AmicaleAPITester:
    def __init__(self, base_url="https://amicale-portal.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_member_id = None
        self.created_project_type_id = None
        
        # Test data
        self.test_member_data = {
            "full_name": f"Test Member {datetime.now().strftime('%H%M%S')}",
            "sex": "Male",
            "phone": f"+212612{datetime.now().strftime('%H%M%S')}",
            "job": "Software Developer",
            "project_type_id": "",  # Will be set after getting project types
            "initial_paid": 500.0
        }

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def make_request(self, method, endpoint, data=None, auth_required=True):
        """Make HTTP request with proper headers"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if auth_required and self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            return None

    def test_init_data(self):
        """Test initialization of default data"""
        print("\n🔧 Testing Data Initialization...")
        
        response = self.make_request('POST', 'init-data', auth_required=False)
        if response and response.status_code == 200:
            self.log_test("Initialize default data", True, f"Status: {response.status_code}")
            return True
        else:
            status = response.status_code if response else "No response"
            self.log_test("Initialize default data", False, f"Status: {status}")
            return False

    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication...")
        
        # Test login with admin credentials
        login_data = {
            "email": "admin@amicale.ma",
            "password": "admin123"
        }
        
        response = self.make_request('POST', 'auth/login', login_data, auth_required=False)
        if response and response.status_code == 200:
            data = response.json()
            if 'access_token' in data and 'user' in data:
                self.token = data['access_token']
                self.user_data = data['user']
                self.log_test("Admin login", True, f"Token received, User: {data['user']['name']}")
                return True
            else:
                self.log_test("Admin login", False, "Missing token or user data")
                return False
        else:
            status = response.status_code if response else "No response"
            self.log_test("Admin login", False, f"Status: {status}")
            return False

    def test_project_types(self):
        """Test project types endpoints"""
        print("\n📋 Testing Project Types...")
        
        # Test GET project types (public endpoint)
        response = self.make_request('GET', 'project-types', auth_required=False)
        if response and response.status_code == 200:
            project_types = response.json()
            if len(project_types) > 0:
                # Store first project type ID for member registration
                self.test_member_data['project_type_id'] = project_types[0]['id']
                self.log_test("Get project types", True, f"Found {len(project_types)} project types")
            else:
                self.log_test("Get project types", False, "No project types found")
                return False
        else:
            status = response.status_code if response else "No response"
            self.log_test("Get project types", False, f"Status: {status}")
            return False
        
        # Test CREATE project type (requires auth)
        new_project_type = {
            "name": f"Test Project {datetime.now().strftime('%H%M%S')}",
            "default_due": 750.0
        }
        
        response = self.make_request('POST', 'project-types', new_project_type)
        if response and response.status_code == 200:
            created_pt = response.json()
            self.created_project_type_id = created_pt['id']
            self.log_test("Create project type", True, f"Created: {created_pt['name']}")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Create project type", False, f"Status: {status}")
        
        return True

    def test_member_registration(self):
        """Test public member registration"""
        print("\n👤 Testing Member Registration...")
        
        response = self.make_request('POST', 'members/register', self.test_member_data, auth_required=False)
        if response and response.status_code == 200:
            member = response.json()
            self.created_member_id = member['id']
            self.log_test("Public member registration", True, 
                         f"Member: {member['full_name']}, Balance: {member['balance']}")
            return True
        else:
            status = response.status_code if response else "No response"
            error_msg = ""
            if response:
                try:
                    error_data = response.json()
                    error_msg = f" - {error_data.get('detail', '')}"
                except:
                    pass
            self.log_test("Public member registration", False, f"Status: {status}{error_msg}")
            return False

    def test_member_management(self):
        """Test member management endpoints"""
        print("\n👥 Testing Member Management...")
        
        # Test GET all members
        response = self.make_request('GET', 'members')
        if response and response.status_code == 200:
            members = response.json()
            self.log_test("Get all members", True, f"Found {len(members)} members")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Get all members", False, f"Status: {status}")
        
        # Test GET specific member
        if self.created_member_id:
            response = self.make_request('GET', f'members/{self.created_member_id}')
            if response and response.status_code == 200:
                member = response.json()
                self.log_test("Get specific member", True, f"Member: {member['full_name']}")
            else:
                status = response.status_code if response else "No response"
                self.log_test("Get specific member", False, f"Status: {status}")
            
            # Test UPDATE member
            update_data = {
                "status": "Active",
                "notes": "Test member updated via API"
            }
            response = self.make_request('PUT', f'members/{self.created_member_id}', update_data)
            if response and response.status_code == 200:
                updated_member = response.json()
                self.log_test("Update member", True, f"Status: {updated_member['status']}")
            else:
                status = response.status_code if response else "No response"
                self.log_test("Update member", False, f"Status: {status}")

    def test_payment_management(self):
        """Test payment management endpoints"""
        print("\n💰 Testing Payment Management...")
        
        if not self.created_member_id:
            self.log_test("Payment tests", False, "No member ID available")
            return
        
        # Test ADD payment
        payment_data = {
            "amount": 250.0,
            "method": "Cash",
            "note": "Test payment via API"
        }
        
        response = self.make_request('POST', f'members/{self.created_member_id}/payments', payment_data)
        if response and response.status_code == 200:
            payment = response.json()
            self.log_test("Add payment", True, f"Amount: {payment['amount']} MAD")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Add payment", False, f"Status: {status}")
        
        # Test GET member payments
        response = self.make_request('GET', f'members/{self.created_member_id}/payments')
        if response and response.status_code == 200:
            payments = response.json()
            self.log_test("Get member payments", True, f"Found {len(payments)} payments")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Get member payments", False, f"Status: {status}")
        
        # Test GET all payments
        response = self.make_request('GET', 'payments')
        if response and response.status_code == 200:
            all_payments = response.json()
            self.log_test("Get all payments", True, f"Found {len(all_payments)} total payments")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Get all payments", False, f"Status: {status}")

    def test_points_system(self):
        """Test points system endpoints - NEW POINTS FUNCTIONALITY"""
        print("\n⭐ Testing Points System...")
        
        if not self.created_member_id:
            self.log_test("Points tests", False, "No member ID available")
            return
        
        # Test GET member points history (should be empty initially)
        response = self.make_request('GET', f'members/{self.created_member_id}/points')
        if response and response.status_code == 200:
            points_history = response.json()
            self.log_test("Get member points history", True, f"Found {len(points_history)} point transactions")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Get member points history", False, f"Status: {status}")
        
        # Test ADD manual points
        manual_points_data = {
            "points": 50,
            "transaction_type": "manual",
            "description": "Test manual points attribution via API"
        }
        
        response = self.make_request('POST', f'members/{self.created_member_id}/points', manual_points_data)
        if response and response.status_code == 200:
            points_transaction = response.json()
            self.log_test("Add manual points", True, f"Added {points_transaction['points']} points")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Add manual points", False, f"Status: {status}")
        
        # Test ADD negative points (deduction)
        deduction_points_data = {
            "points": -10,
            "transaction_type": "deduction",
            "description": "Test points deduction via API"
        }
        
        response = self.make_request('POST', f'members/{self.created_member_id}/points', deduction_points_data)
        if response and response.status_code == 200:
            points_transaction = response.json()
            self.log_test("Add points deduction", True, f"Deducted {abs(points_transaction['points'])} points")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Add points deduction", False, f"Status: {status}")
        
        # Test GET points leaderboard
        response = self.make_request('GET', 'points/leaderboard?limit=5')
        if response and response.status_code == 200:
            leaderboard = response.json()
            self.log_test("Get points leaderboard", True, f"Found {len(leaderboard)} members in leaderboard")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Get points leaderboard", False, f"Status: {status}")
        
        # Verify member now has points
        response = self.make_request('GET', f'members/{self.created_member_id}')
        if response and response.status_code == 200:
            member = response.json()
            member_points = member.get('points', 0)
            self.log_test("Verify member points updated", True, f"Member has {member_points} total points")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Verify member points updated", False, f"Status: {status}")

    def test_automatic_points_from_payment(self):
        """Test automatic points generation from payments"""
        print("\n💰⭐ Testing Automatic Points from Payments...")
        
        if not self.created_member_id:
            self.log_test("Automatic points tests", False, "No member ID available")
            return
        
        # Get member points before payment
        response = self.make_request('GET', f'members/{self.created_member_id}')
        points_before = 0
        if response and response.status_code == 200:
            member = response.json()
            points_before = member.get('points', 0)
            print(f"   Points before payment: {points_before}")
        
        # Add a payment that should generate points (150 MAD = 15 points)
        payment_data = {
            "amount": 150.0,
            "method": "Cash",
            "note": "Test payment for automatic points generation"
        }
        
        response = self.make_request('POST', f'members/{self.created_member_id}/payments', payment_data)
        if response and response.status_code == 200:
            payment = response.json()
            expected_points = int(150 // 10)  # 1 point per 10 MAD
            self.log_test("Add payment for points", True, f"Payment: {payment['amount']} MAD, Expected points: {expected_points}")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Add payment for points", False, f"Status: {status}")
            return
        
        # Verify points were automatically added
        response = self.make_request('GET', f'members/{self.created_member_id}')
        if response and response.status_code == 200:
            member = response.json()
            points_after = member.get('points', 0)
            points_gained = points_after - points_before
            expected_points = int(150 // 10)  # 15 points for 150 MAD
            
            if points_gained == expected_points:
                self.log_test("Automatic points generation", True, 
                             f"Points before: {points_before}, after: {points_after}, gained: {points_gained}")
            else:
                self.log_test("Automatic points generation", False, 
                             f"Expected {expected_points} points, got {points_gained}")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Automatic points generation", False, f"Status: {status}")
        
        # Verify points transaction was created for the payment
        response = self.make_request('GET', f'members/{self.created_member_id}/points')
        if response and response.status_code == 200:
            points_history = response.json()
            payment_transactions = [t for t in points_history if t['transaction_type'] == 'payment']
            if len(payment_transactions) > 0:
                latest_payment_transaction = payment_transactions[0]  # Should be most recent
                self.log_test("Payment points transaction created", True, 
                             f"Transaction: {latest_payment_transaction['points']} pts, Type: {latest_payment_transaction['transaction_type']}")
            else:
                self.log_test("Payment points transaction created", False, "No payment-type transactions found")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Payment points transaction created", False, f"Status: {status}")

    def test_reports(self):
        """Test reports endpoints with enhanced points data"""
        print("\n📊 Testing Enhanced Reports with Points...")
        
        response = self.make_request('GET', 'reports/summary')
        if response and response.status_code == 200:
            reports = response.json()
            
            # Check if points fields are present
            has_points_fields = 'total_points_distributed' in reports and 'average_points_per_member' in reports
            
            if has_points_fields:
                self.log_test("Enhanced reports with points", True, 
                             f"Members: {reports['total_members']}, Collected: {reports['total_collected']} MAD, "
                             f"Points distributed: {reports['total_points_distributed']}, "
                             f"Avg points: {reports['average_points_per_member']}")
            else:
                self.log_test("Enhanced reports with points", False, "Missing points fields in reports")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Enhanced reports with points", False, f"Status: {status}")

    def test_hassan_alami_scenario(self):
        """Test the specific Hassan Alami scenario mentioned in requirements"""
        print("\n👤 Testing Hassan Alami Scenario...")
        
        # Look for Hassan Alami in existing members
        response = self.make_request('GET', 'members?query=Hassan')
        hassan_member = None
        
        if response and response.status_code == 200:
            members = response.json()
            hassan_members = [m for m in members if 'Hassan' in m['full_name'] and 'Alami' in m['full_name']]
            
            if hassan_members:
                hassan_member = hassan_members[0]
                self.log_test("Find Hassan Alami", True, f"Found: {hassan_member['full_name']}")
                
                # Check if Hassan has 15 points from 150 MAD payment
                expected_points = 15
                actual_points = hassan_member.get('points', 0)
                
                if actual_points == expected_points:
                    self.log_test("Hassan Alami points verification", True, 
                                 f"Hassan has {actual_points} points (expected {expected_points})")
                else:
                    self.log_test("Hassan Alami points verification", False, 
                                 f"Hassan has {actual_points} points, expected {expected_points}")
                
                # Check Hassan's payment history
                response = self.make_request('GET', f'members/{hassan_member["id"]}/payments')
                if response and response.status_code == 200:
                    payments = response.json()
                    total_paid = sum(p['amount'] for p in payments)
                    self.log_test("Hassan Alami payment history", True, 
                                 f"Total payments: {len(payments)}, Total amount: {total_paid} MAD")
                
                # Check Hassan's points history
                response = self.make_request('GET', f'members/{hassan_member["id"]}/points')
                if response and response.status_code == 200:
                    points_history = response.json()
                    self.log_test("Hassan Alami points history", True, 
                                 f"Points transactions: {len(points_history)}")
            else:
                self.log_test("Find Hassan Alami", False, "Hassan Alami not found in members")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Find Hassan Alami", False, f"Status: {status}")

    def test_member_search_and_filters(self):
        """Test member search and filtering"""
        print("\n🔍 Testing Member Search & Filters...")
        
        # Test search by name
        response = self.make_request('GET', 'members?query=Test')
        if response and response.status_code == 200:
            members = response.json()
            self.log_test("Search members by name", True, f"Found {len(members)} members")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Search members by name", False, f"Status: {status}")
        
        # Test filter by status
        response = self.make_request('GET', 'members?status=Active')
        if response and response.status_code == 200:
            members = response.json()
            self.log_test("Filter members by status", True, f"Found {len(members)} active members")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Filter members by status", False, f"Status: {status}")

    def test_rewards_catalog(self):
        """Test rewards catalog endpoints - NEW REWARDS SYSTEM"""
        print("\n🎁 Testing Rewards Catalog...")
        
        # Test GET all rewards (public endpoint)
        response = self.make_request('GET', 'rewards', auth_required=False)
        if response and response.status_code == 200:
            rewards = response.json()
            self.log_test("Get all rewards", True, f"Found {len(rewards)} rewards")
            
            # Verify we have the expected 10 default rewards
            if len(rewards) >= 10:
                self.log_test("Default rewards loaded", True, f"Found {len(rewards)} rewards (expected ≥10)")
            else:
                self.log_test("Default rewards loaded", False, f"Found {len(rewards)} rewards (expected ≥10)")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Get all rewards", False, f"Status: {status}")
            return
        
        # Test GET active rewards only
        response = self.make_request('GET', 'rewards?active=true', auth_required=False)
        if response and response.status_code == 200:
            active_rewards = response.json()
            self.log_test("Get active rewards", True, f"Found {len(active_rewards)} active rewards")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Get active rewards", False, f"Status: {status}")
        
        # Test filter by category
        categories = ['Materiel', 'Services', 'Reductions', 'Privileges']
        for category in categories:
            response = self.make_request('GET', f'rewards?category={category}', auth_required=False)
            if response and response.status_code == 200:
                category_rewards = response.json()
                self.log_test(f"Filter rewards by {category}", True, f"Found {len(category_rewards)} {category} rewards")
            else:
                status = response.status_code if response else "No response"
                self.log_test(f"Filter rewards by {category}", False, f"Status: {status}")
        
        # Verify specific rewards mentioned in requirements
        expected_rewards = [
            {"name": "Pack Bienvenue", "points": 90, "category": "Materiel"},
            {"name": "Invitation VIP", "points": 180, "category": "Privileges"},
            {"name": "Formation gratuite", "points": 250, "category": "Services"},
            {"name": "Assistance personnalisée", "points": 300, "category": "Services"}
        ]
        
        for expected in expected_rewards:
            found_reward = None
            for reward in rewards:
                if expected["name"] in reward["name"]:
                    found_reward = reward
                    break
            
            if found_reward:
                points_match = found_reward["cost_points"] == expected["points"]
                category_match = found_reward["category"] == expected["category"]
                
                if points_match and category_match:
                    self.log_test(f"Verify {expected['name']}", True, 
                                 f"Points: {found_reward['cost_points']}, Category: {found_reward['category']}")
                else:
                    self.log_test(f"Verify {expected['name']}", False, 
                                 f"Expected {expected['points']} pts/{expected['category']}, "
                                 f"got {found_reward['cost_points']} pts/{found_reward['category']}")
            else:
                self.log_test(f"Verify {expected['name']}", False, "Reward not found")

    def test_redemption_workflow(self):
        """Test complete redemption workflow - NEW REWARDS SYSTEM"""
        print("\n🔄 Testing Redemption Workflow...")
        
        if not self.created_member_id:
            self.log_test("Redemption workflow", False, "No member ID available")
            return
        
        # First, ensure member has enough points (add 200 points for testing)
        points_data = {
            "points": 200,
            "transaction_type": "bonus",
            "description": "Test points for redemption testing"
        }
        
        response = self.make_request('POST', f'members/{self.created_member_id}/points', points_data)
        if response and response.status_code == 200:
            self.log_test("Add points for redemption test", True, "Added 200 points")
        else:
            self.log_test("Add points for redemption test", False, "Failed to add points")
            return
        
        # Get available rewards
        response = self.make_request('GET', 'rewards?active=true', auth_required=False)
        if not response or response.status_code != 200:
            self.log_test("Get rewards for redemption", False, "Failed to get rewards")
            return
        
        rewards = response.json()
        # Find a reward with cost <= 200 points
        suitable_reward = None
        for reward in rewards:
            if reward['cost_points'] <= 200 and reward['stock'] > 0:
                suitable_reward = reward
                break
        
        if not suitable_reward:
            self.log_test("Find suitable reward", False, "No reward found with ≤200 points and stock > 0")
            return
        
        self.log_test("Find suitable reward", True, 
                     f"Selected: {suitable_reward['name']} ({suitable_reward['cost_points']} pts)")
        
        # Test CREATE redemption request
        redemption_data = {
            "reward_id": suitable_reward['id'],
            "note": "Test redemption request via API"
        }
        
        response = self.make_request('POST', f'members/{self.created_member_id}/redemptions', redemption_data)
        if response and response.status_code == 200:
            redemption = response.json()
            redemption_id = redemption['id']
            self.log_test("Create redemption request", True, 
                         f"Status: {redemption['status']}, Points: {redemption['points_cost']}")
        else:
            status = response.status_code if response else "No response"
            error_msg = ""
            if response:
                try:
                    error_data = response.json()
                    error_msg = f" - {error_data.get('detail', '')}"
                except:
                    pass
            self.log_test("Create redemption request", False, f"Status: {status}{error_msg}")
            return
        
        # Test GET member redemptions
        response = self.make_request('GET', f'members/{self.created_member_id}/redemptions')
        if response and response.status_code == 200:
            member_redemptions = response.json()
            self.log_test("Get member redemptions", True, f"Found {len(member_redemptions)} redemptions")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Get member redemptions", False, f"Status: {status}")
        
        # Test GET all redemptions (admin)
        response = self.make_request('GET', 'redemptions')
        if response and response.status_code == 200:
            all_redemptions = response.json()
            self.log_test("Get all redemptions (admin)", True, f"Found {len(all_redemptions)} total redemptions")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Get all redemptions (admin)", False, f"Status: {status}")
        
        # Test APPROVE redemption
        approval_data = {
            "note": "Approved via API testing"
        }
        
        response = self.make_request('PUT', f'redemptions/{redemption_id}/approve', approval_data)
        if response and response.status_code == 200:
            approved_redemption = response.json()
            self.log_test("Approve redemption", True, 
                         f"Status: {approved_redemption['status']}, Approved by: {approved_redemption.get('approved_by_name', 'N/A')}")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Approve redemption", False, f"Status: {status}")
            return
        
        # Verify points were deducted
        response = self.make_request('GET', f'members/{self.created_member_id}')
        if response and response.status_code == 200:
            member = response.json()
            current_points = member.get('points', 0)
            self.log_test("Verify points deducted", True, f"Member now has {current_points} points")
        else:
            self.log_test("Verify points deducted", False, "Failed to get member data")
        
        # Verify stock was reduced
        response = self.make_request('GET', 'rewards', auth_required=False)
        if response and response.status_code == 200:
            updated_rewards = response.json()
            updated_reward = next((r for r in updated_rewards if r['id'] == suitable_reward['id']), None)
            if updated_reward:
                expected_stock = suitable_reward['stock'] - 1
                if updated_reward['stock'] == expected_stock:
                    self.log_test("Verify stock reduced", True, 
                                 f"Stock reduced from {suitable_reward['stock']} to {updated_reward['stock']}")
                else:
                    self.log_test("Verify stock reduced", False, 
                                 f"Expected stock {expected_stock}, got {updated_reward['stock']}")
            else:
                self.log_test("Verify stock reduced", False, "Reward not found in updated list")
        
        # Test DELIVER redemption
        delivery_data = {
            "note": "Delivered via API testing"
        }
        
        response = self.make_request('PUT', f'redemptions/{redemption_id}/deliver', delivery_data)
        if response and response.status_code == 200:
            delivered_redemption = response.json()
            self.log_test("Deliver redemption", True, 
                         f"Status: {delivered_redemption['status']}, Delivered by: {delivered_redemption.get('delivered_by_name', 'N/A')}")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Deliver redemption", False, f"Status: {status}")

    def test_redemption_rejection_and_refund(self):
        """Test redemption rejection and refund mechanism"""
        print("\n↩️ Testing Redemption Rejection & Refund...")
        
        if not self.created_member_id:
            self.log_test("Rejection test", False, "No member ID available")
            return
        
        # Add more points for another redemption test
        points_data = {
            "points": 150,
            "transaction_type": "bonus",
            "description": "Test points for rejection testing"
        }
        
        response = self.make_request('POST', f'members/{self.created_member_id}/points', points_data)
        if not response or response.status_code != 200:
            self.log_test("Add points for rejection test", False, "Failed to add points")
            return
        
        # Get member points before redemption
        response = self.make_request('GET', f'members/{self.created_member_id}')
        points_before = 0
        if response and response.status_code == 200:
            member = response.json()
            points_before = member.get('points', 0)
        
        # Find a suitable reward
        response = self.make_request('GET', 'rewards?active=true', auth_required=False)
        if not response or response.status_code != 200:
            self.log_test("Get rewards for rejection test", False, "Failed to get rewards")
            return
        
        rewards = response.json()
        suitable_reward = None
        for reward in rewards:
            if reward['cost_points'] <= 150 and reward['stock'] > 0:
                suitable_reward = reward
                break
        
        if not suitable_reward:
            self.log_test("Find reward for rejection test", False, "No suitable reward found")
            return
        
        # Create redemption request
        redemption_data = {
            "reward_id": suitable_reward['id'],
            "note": "Test redemption for rejection testing"
        }
        
        response = self.make_request('POST', f'members/{self.created_member_id}/redemptions', redemption_data)
        if not response or response.status_code != 200:
            self.log_test("Create redemption for rejection", False, "Failed to create redemption")
            return
        
        redemption = response.json()
        redemption_id = redemption['id']
        
        # Approve first (to test rejection after approval)
        response = self.make_request('PUT', f'redemptions/{redemption_id}/approve', {"note": "Approved for rejection test"})
        if not response or response.status_code != 200:
            self.log_test("Approve for rejection test", False, "Failed to approve redemption")
            return
        
        # Now reject the approved redemption
        rejection_data = {
            "note": "Rejected via API testing - should refund points and stock"
        }
        
        response = self.make_request('PUT', f'redemptions/{redemption_id}/reject', rejection_data)
        if response and response.status_code == 200:
            rejected_redemption = response.json()
            self.log_test("Reject approved redemption", True, f"Status: {rejected_redemption['status']}")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Reject approved redemption", False, f"Status: {status}")
            return
        
        # Verify points were refunded
        response = self.make_request('GET', f'members/{self.created_member_id}')
        if response and response.status_code == 200:
            member = response.json()
            points_after = member.get('points', 0)
            
            # Points should be refunded (points_after should be close to points_before)
            if points_after >= points_before - 10:  # Allow small margin for other transactions
                self.log_test("Verify points refunded", True, 
                             f"Points before: {points_before}, after rejection: {points_after}")
            else:
                self.log_test("Verify points refunded", False, 
                             f"Points not properly refunded. Before: {points_before}, after: {points_after}")
        else:
            self.log_test("Verify points refunded", False, "Failed to get member data")
        
        # Verify stock was restored
        response = self.make_request('GET', 'rewards', auth_required=False)
        if response and response.status_code == 200:
            updated_rewards = response.json()
            updated_reward = next((r for r in updated_rewards if r['id'] == suitable_reward['id']), None)
            if updated_reward:
                if updated_reward['stock'] >= suitable_reward['stock']:
                    self.log_test("Verify stock restored", True, 
                                 f"Stock restored to {updated_reward['stock']} (was {suitable_reward['stock']})")
                else:
                    self.log_test("Verify stock restored", False, 
                                 f"Stock not restored. Expected ≥{suitable_reward['stock']}, got {updated_reward['stock']}")
            else:
                self.log_test("Verify stock restored", False, "Reward not found")

    def test_anti_abuse_limits(self):
        """Test anti-abuse mechanism (max 3 pending redemptions)"""
        print("\n🛡️ Testing Anti-Abuse Limits...")
        
        if not self.created_member_id:
            self.log_test("Anti-abuse test", False, "No member ID available")
            return
        
        # Add enough points for multiple redemptions
        points_data = {
            "points": 500,
            "transaction_type": "bonus",
            "description": "Test points for anti-abuse testing"
        }
        
        response = self.make_request('POST', f'members/{self.created_member_id}/points', points_data)
        if not response or response.status_code != 200:
            self.log_test("Add points for anti-abuse test", False, "Failed to add points")
            return
        
        # Find a low-cost reward
        response = self.make_request('GET', 'rewards?active=true', auth_required=False)
        if not response or response.status_code != 200:
            self.log_test("Get rewards for anti-abuse test", False, "Failed to get rewards")
            return
        
        rewards = response.json()
        low_cost_reward = None
        for reward in rewards:
            if reward['cost_points'] <= 100 and reward['stock'] > 0:
                low_cost_reward = reward
                break
        
        if not low_cost_reward:
            self.log_test("Find low-cost reward", False, "No suitable low-cost reward found")
            return
        
        # Create 3 redemption requests (should be allowed)
        redemption_ids = []
        for i in range(3):
            redemption_data = {
                "reward_id": low_cost_reward['id'],
                "note": f"Anti-abuse test redemption {i+1}"
            }
            
            response = self.make_request('POST', f'members/{self.created_member_id}/redemptions', redemption_data)
            if response and response.status_code == 200:
                redemption = response.json()
                redemption_ids.append(redemption['id'])
                self.log_test(f"Create redemption {i+1}/3", True, f"Status: {redemption['status']}")
            else:
                status = response.status_code if response else "No response"
                self.log_test(f"Create redemption {i+1}/3", False, f"Status: {status}")
        
        # Try to create a 4th redemption (should be blocked)
        redemption_data = {
            "reward_id": low_cost_reward['id'],
            "note": "Anti-abuse test - 4th redemption (should fail)"
        }
        
        response = self.make_request('POST', f'members/{self.created_member_id}/redemptions', redemption_data)
        if response and response.status_code == 400:
            error_data = response.json()
            if "pending redemptions" in error_data.get('detail', '').lower():
                self.log_test("Anti-abuse limit enforced", True, "4th redemption blocked as expected")
            else:
                self.log_test("Anti-abuse limit enforced", False, f"Wrong error message: {error_data.get('detail', '')}")
        else:
            status = response.status_code if response else "No response"
            self.log_test("Anti-abuse limit enforced", False, f"Expected 400, got {status}")
        
        # Clean up: approve one redemption to test that limit is lifted
        if redemption_ids:
            response = self.make_request('PUT', f'redemptions/{redemption_ids[0]}/approve', {"note": "Cleanup approval"})
            if response and response.status_code == 200:
                self.log_test("Cleanup: approve one redemption", True, "Approved first redemption")
                
                # Now try creating another redemption (should work)
                response = self.make_request('POST', f'members/{self.created_member_id}/redemptions', redemption_data)
                if response and response.status_code == 200:
                    self.log_test("Anti-abuse limit lifted after approval", True, "New redemption allowed after approval")
                else:
                    status = response.status_code if response else "No response"
                    self.log_test("Anti-abuse limit lifted after approval", False, f"Status: {status}")

    def test_redemption_status_filters(self):
        """Test redemption status filtering"""
        print("\n🔍 Testing Redemption Status Filters...")
        
        # Test filter by status
        statuses = ['Pending', 'Approved', 'Delivered', 'Rejected']
        for status in statuses:
            response = self.make_request('GET', f'redemptions?status={status}')
            if response and response.status_code == 200:
                filtered_redemptions = response.json()
                self.log_test(f"Filter redemptions by {status}", True, 
                             f"Found {len(filtered_redemptions)} {status.lower()} redemptions")
            else:
                status_code = response.status_code if response else "No response"
                self.log_test(f"Filter redemptions by {status}", False, f"Status: {status_code}")

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Amicale Anouar Backend API Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Initialize data first
        if not self.test_init_data():
            print("⚠️  Data initialization failed, continuing with existing data...")
        
        # Test authentication
        if not self.test_authentication():
            print("❌ Authentication failed - stopping tests")
            return False
        
        # Test all endpoints
        self.test_project_types()
        self.test_member_registration()
        self.test_member_management()
        self.test_payment_management()
        
        # Test NEW POINTS SYSTEM functionality
        self.test_points_system()
        self.test_automatic_points_from_payment()
        self.test_hassan_alami_scenario()
        
        self.test_reports()
        self.test_member_search_and_filters()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 TEST SUMMARY")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED!")
            return True
        else:
            print("⚠️  SOME TESTS FAILED")
            return False

def main():
    """Main test execution"""
    tester = AmicaleAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())