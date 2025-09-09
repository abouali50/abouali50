"""
Comprehensive test suite for Amicale Anouar gamification system
Tests: Points, Redemptions, Levels, Badges, Leaderboards, Jobs
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from server import app, db, notification_manager
from datetime import datetime, timezone, timedelta
import uuid
import json

# Test client setup
client = TestClient(app)

class TestData:
    """Test data container"""
    def __init__(self):
        self.admin_token = None
        self.member_id = None
        self.reward_id = None
        self.project_type_id = None
        self.badge_id = None
        self.reset()
    
    def reset(self):
        self.admin_token = None
        self.member_id = None
        self.reward_id = None
        self.project_type_id = None
        self.badge_id = None

# Global test data
test_data = TestData()

@pytest.fixture(scope="module")
def setup_test_data():
    """Setup test data: admin login, project type, reward, member"""
    global test_data
    
    # Admin login
    login_response = client.post("/api/auth/login", json={
        "email": "admin@amicale.ma",
        "password": "admin123"
    })
    assert login_response.status_code == 200
    test_data.admin_token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {test_data.admin_token}"}
    
    # Get project type
    project_types = client.get("/api/project-types").json()
    assert len(project_types) > 0
    test_data.project_type_id = project_types[0]["id"]
    
    # Get reward
    rewards = client.get("/api/rewards?active=true").json()
    assert len(rewards) > 0
    test_data.reward_id = rewards[0]["id"]
    
    # Get badge
    badges = client.get("/api/badges").json()
    assert len(badges) > 0
    test_data.badge_id = badges[0]["id"]
    
    # Create test member
    member_data = {
        "full_name": "Test Member Automated",
        "sex": "Male",
        "phone": f"+212{uuid.uuid4().hex[:8]}",
        "job": "Tester",
        "project_type_id": test_data.project_type_id,
        "initial_paid": 100.0
    }
    
    member_response = client.post("/api/members/register", json=member_data)
    assert member_response.status_code == 200
    test_data.member_id = member_response.json()["id"]
    
    return test_data

class TestPointsSystem:
    """Test points transactions and calculations"""
    
    def test_points_added_on_payment(self, setup_test_data):
        """Test that payments automatically generate points"""
        headers = {"Authorization": f"Bearer {test_data.admin_token}"}
        
        # Get initial points
        member_before = client.get(f"/api/members/{test_data.member_id}", headers=headers).json()
        initial_points = member_before["points"]
        
        # Add payment (150 MAD = 15 points)
        payment_data = {
            "amount": 150.0,
            "method": "Cash",
            "note": "Test payment for points"
        }
        
        payment_response = client.post(
            f"/api/members/{test_data.member_id}/payments", 
            json=payment_data, 
            headers=headers
        )
        assert payment_response.status_code == 200
        
        # Check points increased
        member_after = client.get(f"/api/members/{test_data.member_id}", headers=headers).json()
        expected_points = initial_points + 15  # 150 MAD / 10 = 15 points
        assert member_after["points"] == expected_points
    
    def test_manual_points_addition(self, setup_test_data):
        """Test manual points addition by admin"""
        headers = {"Authorization": f"Bearer {test_data.admin_token}"}
        
        # Get initial points
        member_before = client.get(f"/api/members/{test_data.member_id}", headers=headers).json()
        initial_points = member_before["points"]
        
        # Add manual points
        points_data = {
            "points": 25,
            "transaction_type": "bonus",
            "description": "Test bonus points"
        }
        
        points_response = client.post(
            f"/api/members/{test_data.member_id}/points",
            json=points_data,
            headers=headers
        )
        assert points_response.status_code == 200
        
        # Check points increased
        member_after = client.get(f"/api/members/{test_data.member_id}", headers=headers).json()
        assert member_after["points"] == initial_points + 25
    
    def test_points_calculation_accuracy(self, setup_test_data):
        """Test points calculation from payment amounts"""
        test_cases = [
            (100.0, 10),  # 100 MAD = 10 points
            (155.0, 15),  # 155 MAD = 15 points (floor division)
            (9.0, 0),     # 9 MAD = 0 points
            (999.0, 99),  # 999 MAD = 99 points
        ]
        
        headers = {"Authorization": f"Bearer {test_data.admin_token}"}
        
        for amount, expected_points in test_cases:
            # Get initial points
            member_before = client.get(f"/api/members/{test_data.member_id}", headers=headers).json()
            initial_points = member_before["points"]
            
            # Add payment
            payment_data = {
                "amount": amount,
                "method": "Cash",
                "note": f"Test payment {amount} MAD"
            }
            
            client.post(f"/api/members/{test_data.member_id}/payments", json=payment_data, headers=headers)
            
            # Check points
            member_after = client.get(f"/api/members/{test_data.member_id}", headers=headers).json()
            actual_points_gained = member_after["points"] - initial_points
            assert actual_points_gained == expected_points, f"Amount {amount} should give {expected_points} points, got {actual_points_gained}"

class TestRedemptionSystem:
    """Test redemption workflow: request -> approve -> deliver"""
    
    def test_redemption_full_workflow(self, setup_test_data):
        """Test complete redemption workflow"""
        headers = {"Authorization": f"Bearer {test_data.admin_token}"}
        
        # Ensure member has enough points (get reward cost first)
        rewards = client.get("/api/rewards?active=true").json()
        test_reward = min(rewards, key=lambda r: r["cost_points"])  # Get cheapest reward
        required_points = test_reward["cost_points"]
        
        # Add points if needed
        member = client.get(f"/api/members/{test_data.member_id}", headers=headers).json()
        if member["points"] < required_points:
            points_needed = required_points - member["points"]
            client.post(
                f"/api/members/{test_data.member_id}/points",
                json={"points": points_needed, "transaction_type": "bonus", "description": "Test setup"},
                headers=headers
            )
        
        # Get points before redemption request
        member_before = client.get(f"/api/members/{test_data.member_id}", headers=headers).json()
        points_before = member_before["points"]
        
        # Create redemption request
        redemption_data = {
            "reward_id": test_reward["id"],
            "note": "Test redemption request"
        }
        
        redemption_response = client.post(
            f"/api/members/{test_data.member_id}/redemptions",
            json=redemption_data,
            headers=headers
        )
        assert redemption_response.status_code == 200
        redemption = redemption_response.json()
        assert redemption["status"] == "Pending"
        
        # Approve redemption
        approve_response = client.put(
            f"/api/redemptions/{redemption['id']}/approve",
            json={"note": "Approved for testing"},
            headers=headers
        )
        assert approve_response.status_code == 200
        approved_redemption = approve_response.json()
        assert approved_redemption["status"] == "Approved"
        
        # Check points were deducted
        member_after_approve = client.get(f"/api/members/{test_data.member_id}", headers=headers).json()
        points_after_approve = member_after_approve["points"]
        assert points_after_approve == points_before - required_points
        
        # Deliver redemption
        deliver_response = client.put(
            f"/api/redemptions/{redemption['id']}/deliver",
            json={"note": "Delivered for testing"},
            headers=headers
        )
        assert deliver_response.status_code == 200
        delivered_redemption = deliver_response.json()
        assert delivered_redemption["status"] == "Delivered"
    
    def test_redemption_rejection_refunds_points(self, setup_test_data):
        """Test that rejecting approved redemptions refunds points"""
        headers = {"Authorization": f"Bearer {test_data.admin_token}"}
        
        # Setup: ensure member has points and create/approve redemption
        rewards = client.get("/api/rewards?active=true").json()
        test_reward = min(rewards, key=lambda r: r["cost_points"])
        required_points = test_reward["cost_points"]
        
        # Add sufficient points
        client.post(
            f"/api/members/{test_data.member_id}/points",
            json={"points": required_points + 10, "transaction_type": "bonus", "description": "Test setup"},
            headers=headers
        )
        
        # Create and approve redemption
        redemption_response = client.post(
            f"/api/members/{test_data.member_id}/redemptions",
            json={"reward_id": test_reward["id"], "note": "Test rejection"},
            headers=headers
        )
        redemption = redemption_response.json()
        
        client.put(f"/api/redemptions/{redemption['id']}/approve", json={}, headers=headers)
        
        # Get points after approval (should be deducted)
        member_after_approve = client.get(f"/api/members/{test_data.member_id}", headers=headers).json()
        points_after_approve = member_after_approve["points"]
        
        # Reject the approved redemption
        reject_response = client.put(
            f"/api/redemptions/{redemption['id']}/reject",
            json={"note": "Rejected for testing"},
            headers=headers
        )
        assert reject_response.status_code == 200
        
        # Check points were refunded
        member_after_reject = client.get(f"/api/members/{test_data.member_id}", headers=headers).json()
        points_after_reject = member_after_reject["points"]
        assert points_after_reject == points_after_approve + required_points
    
    def test_insufficient_points_blocks_redemption(self, setup_test_data):
        """Test that redemption fails if member has insufficient points"""
        headers = {"Authorization": f"Bearer {test_data.admin_token}"}
        
        # Find most expensive reward
        rewards = client.get("/api/rewards?active=true").json()
        expensive_reward = max(rewards, key=lambda r: r["cost_points"])
        
        # Ensure member has fewer points than required
        member = client.get(f"/api/members/{test_data.member_id}", headers=headers).json()
        if member["points"] >= expensive_reward["cost_points"]:
            # Deduct points to make it insufficient
            points_to_deduct = member["points"] - expensive_reward["cost_points"] + 1
            client.post(
                f"/api/members/{test_data.member_id}/points",
                json={"points": -points_to_deduct, "transaction_type": "deduction", "description": "Test setup"},
                headers=headers
            )
        
        # Try to create redemption - should fail
        redemption_response = client.post(
            f"/api/members/{test_data.member_id}/redemptions",
            json={"reward_id": expensive_reward["id"], "note": "Should fail"},
            headers=headers
        )
        assert redemption_response.status_code == 400
        assert "not enough points" in redemption_response.json()["detail"].lower()

class TestLevelsAndBadges:
    """Test level calculation and badge awarding"""
    
    def test_level_calculation_based_on_earned_points(self, setup_test_data):
        """Test that levels are calculated correctly based on total earned points"""
        headers = {"Authorization": f"Bearer {test_data.admin_token}"}
        
        # Test different point thresholds
        test_cases = [
            (0, "Bronze"),
            (25, "Bronze"),
            (50, "Bronze"),
            (51, "Argent"),
            (100, "Argent"),
            (200, "Argent"),
            (201, "Or"),
            (400, "Or"),
            (500, "Platine"),
            (1000, "Platine"),
        ]
        
        for target_points, expected_level in test_cases:
            # Create new test member for clean slate
            member_data = {
                "full_name": f"Level Test {target_points} pts",
                "sex": "Female",
                "phone": f"+212{uuid.uuid4().hex[:8]}",
                "job": "Level Tester",
                "project_type_id": test_data.project_type_id,
                "initial_paid": 0.0
            }
            
            member_response = client.post("/api/members/register", json=member_data)
            test_member_id = member_response.json()["id"]
            
            # Add exact points needed
            if target_points > 0:
                client.post(
                    f"/api/members/{test_member_id}/points",
                    json={"points": target_points, "transaction_type": "bonus", "description": f"Test {target_points} points"},
                    headers=headers
                )
            
            # Check level
            level_response = client.get(f"/api/members/{test_member_id}/level", headers=headers)
            assert level_response.status_code == 200
            level_data = level_response.json()
            
            actual_level = level_data["current_level"]["name"]
            assert actual_level == expected_level, f"Points {target_points} should be {expected_level}, got {actual_level}"
    
    def test_badge_awarding_system(self, setup_test_data):
        """Test manual badge awarding"""
        headers = {"Authorization": f"Bearer {test_data.admin_token}"}
        
        # Get available badges
        badges = client.get("/api/badges").json()
        test_badge = badges[0]
        
        # Get initial badges count
        member_badges_before = client.get(f"/api/members/{test_data.member_id}/badges", headers=headers).json()
        initial_count = len(member_badges_before)
        
        # Award badge
        award_response = client.post(
            f"/api/members/{test_data.member_id}/badges/{test_badge['code']}",
            headers=headers
        )
        
        if award_response.status_code == 200:
            # Check badge was awarded
            member_badges_after = client.get(f"/api/members/{test_data.member_id}/badges", headers=headers).json()
            assert len(member_badges_after) == initial_count + 1
            
            # Check specific badge is present
            badge_codes = [b["badge_code"] for b in member_badges_after]
            assert test_badge["code"] in badge_codes
        else:
            # Badge already awarded - that's also valid
            assert award_response.status_code == 400
            assert "already awarded" in award_response.json()["detail"].lower()
    
    def test_level_progression_calculation(self, setup_test_data):
        """Test level progression percentage and points to next level"""
        headers = {"Authorization": f"Bearer {test_data.admin_token}"}
        
        # Create member with specific points for progression test
        member_data = {
            "full_name": "Progression Test Member",
            "sex": "Other",
            "phone": f"+212{uuid.uuid4().hex[:8]}",
            "job": "Progression Tester",
            "project_type_id": test_data.project_type_id,
            "initial_paid": 0.0
        }
        
        member_response = client.post("/api/members/register", json=member_data)
        test_member_id = member_response.json()["id"]
        
        # Add 75 points (Bronze to Argent progression: 75/51 = above Argent threshold)
        client.post(
            f"/api/members/{test_member_id}/points",
            json={"points": 75, "transaction_type": "bonus", "description": "Progression test"},
            headers=headers
        )
        
        # Check level and progression
        level_response = client.get(f"/api/members/{test_member_id}/level", headers=headers)
        level_data = level_response.json()
        
        assert level_data["current_level"]["name"] == "Argent"
        assert level_data["next_level"]["name"] == "Or"  # Next level should be Or (201 points)
        
        # Calculate expected progression: (75 - 51) / (201 - 51) = 24/150 = 16%
        expected_progress = round((75 - 51) / (201 - 51) * 100, 1)
        assert abs(level_data["progress_percentage"] - expected_progress) < 0.1
        
        # Points to next level: 201 - 75 = 126
        assert level_data["points_to_next"] == 201 - 75

class TestLeaderboardSystem:
    """Test leaderboard generation and ranking"""
    
    def test_all_time_leaderboard_generation(self, setup_test_data):
        """Test all-time leaderboard generation"""
        headers = {"Authorization": f"Bearer {test_data.admin_token}"}
        
        # Generate all-time leaderboard
        generate_response = client.post("/api/leaderboard/generate/all-time", headers=headers)
        assert generate_response.status_code == 200
        
        # Get leaderboard
        leaderboard_response = client.get("/api/leaderboard?period=all_time")
        assert leaderboard_response.status_code == 200
        leaderboard = leaderboard_response.json()
        
        assert leaderboard["period"] == "all_time"
        assert len(leaderboard["entries"]) > 0
        assert leaderboard["total_entries"] > 0
        
        # Check ranking is correct (descending by points)
        entries = leaderboard["entries"]
        for i in range(len(entries) - 1):
            assert entries[i]["points"] >= entries[i + 1]["points"]
            assert entries[i]["rank"] == i + 1
    
    def test_monthly_leaderboard_generation(self, setup_test_data):
        """Test monthly leaderboard generation"""
        headers = {"Authorization": f"Bearer {test_data.admin_token}"}
        
        current_date = datetime.now()
        year, month = current_date.year, current_date.month
        
        # Generate monthly leaderboard
        generate_response = client.post(f"/api/leaderboard/generate/{year}/{month}", headers=headers)
        assert generate_response.status_code == 200
        
        # Get monthly leaderboard
        period = f"monthly:{year}-{month:02d}"
        leaderboard_response = client.get(f"/api/leaderboard?period={period}")
        assert leaderboard_response.status_code == 200
        leaderboard = leaderboard_response.json()
        
        assert leaderboard["period"] == period
        # Monthly leaderboard might be empty if no activity this month, that's OK
        assert leaderboard["total_entries"] >= 0
    
    def test_leaderboard_idempotency(self, setup_test_data):
        """Test that regenerating leaderboard produces consistent results"""
        headers = {"Authorization": f"Bearer {test_data.admin_token}"}
        
        # Generate all-time leaderboard twice
        client.post("/api/leaderboard/generate/all-time", headers=headers)
        leaderboard1 = client.get("/api/leaderboard?period=all_time").json()
        
        client.post("/api/leaderboard/generate/all-time", headers=headers)
        leaderboard2 = client.get("/api/leaderboard?period=all_time").json()
        
        # Compare entries (excluding generated_at timestamp)
        entries1 = sorted(leaderboard1["entries"], key=lambda x: x["rank"])
        entries2 = sorted(leaderboard2["entries"], key=lambda x: x["rank"])
        
        assert len(entries1) == len(entries2)
        for e1, e2 in zip(entries1, entries2):
            assert e1["rank"] == e2["rank"]
            assert e1["member_id"] == e2["member_id"]
            assert e1["points"] == e2["points"]

class TestJobsAndMaintenance:
    """Test scheduled jobs and maintenance tasks"""
    
    def test_daily_jobs_execution(self, setup_test_data):
        """Test daily maintenance jobs"""
        headers = {"Authorization": f"Bearer {test_data.admin_token}"}
        
        # Run daily jobs
        jobs_response = client.post("/api/jobs/daily", headers=headers)
        assert jobs_response.status_code == 200
        
        result = jobs_response.json()
        assert "members_checked" in result
        assert "badges_processed" in result
        assert result["members_checked"] > 0
    
    def test_gamification_kpi_calculation(self, setup_test_data):
        """Test KPI calculation for monitoring"""
        headers = {"Authorization": f"Bearer {test_data.admin_token}"}
        
        # Get KPI data
        kpi_response = client.get("/api/monitor/gamification/summary", headers=headers)
        assert kpi_response.status_code == 200
        
        kpi_data = kpi_response.json()
        
        # Validate KPI structure
        required_fields = [
            "total_points_distributed",
            "average_points_per_member", 
            "badges_awarded_this_month",
            "pending_redemptions",
            "redemption_approval_rate",
            "level_distribution"
        ]
        
        for field in required_fields:
            assert field in kpi_data
        
        # Validate data types and ranges
        assert isinstance(kpi_data["total_points_distributed"], int)
        assert kpi_data["total_points_distributed"] >= 0
        
        assert isinstance(kpi_data["average_points_per_member"], (int, float))
        assert kpi_data["average_points_per_member"] >= 0
        
        assert isinstance(kpi_data["redemption_approval_rate"], (int, float))
        assert 0 <= kpi_data["redemption_approval_rate"] <= 100
        
        assert isinstance(kpi_data["level_distribution"], dict)

class TestExportsAndCSV:
    """Test CSV export functionality"""
    
    def test_leaderboard_csv_export(self, setup_test_data):
        """Test leaderboard CSV export"""
        headers = {"Authorization": f"Bearer {test_data.admin_token}"}
        
        # Generate leaderboard first
        client.post("/api/leaderboard/generate/all-time", headers=headers)
        
        # Export CSV
        export_response = client.get("/api/export/leaderboard?period=all_time", headers=headers)
        assert export_response.status_code == 200
        
        # Check CSV content
        csv_content = export_response.content.decode('utf-8')
        lines = csv_content.strip().split('\n')
        
        # Check header
        assert lines[0] == "Rang,Membre,Points,Niveau,Badges,Date_Generation"
        
        # Check data rows (should have at least test member)
        assert len(lines) > 1
        
        # Validate CSV format
        for line in lines[1:]:  # Skip header
            fields = line.split(',')
            assert len(fields) == 6  # Should have 6 columns
    
    def test_redemptions_csv_export(self, setup_test_data):
        """Test redemptions CSV export"""
        headers = {"Authorization": f"Bearer {test_data.admin_token}"}
        
        # Export CSV
        export_response = client.get("/api/export/redemptions", headers=headers)
        assert export_response.status_code == 200
        
        # Check response is CSV
        assert export_response.headers["content-type"] == "text/csv; charset=utf-8"
        
        # Check CSV content
        csv_content = export_response.content.decode('utf-8')
        lines = csv_content.strip().split('\n')
        
        # Check header
        expected_header = "Date_Demande,Membre,Récompense,Points_Coût,Statut,Approuvé_Par,Date_Approbation,Note"
        assert lines[0] == expected_header

# Integration tests
class TestIntegrationScenarios:
    """Test complete user scenarios end-to-end"""
    
    def test_complete_member_journey(self, setup_test_data):
        """Test complete member journey: register -> earn points -> redeem -> level up"""
        headers = {"Authorization": f"Bearer {test_data.admin_token}"}
        
        # 1. Register new member
        member_data = {
            "full_name": "Journey Test Member",
            "sex": "Male",
            "phone": f"+212{uuid.uuid4().hex[:8]}",
            "job": "Journey Tester",
            "project_type_id": test_data.project_type_id,
            "initial_paid": 50.0  # 5 points
        }
        
        member_response = client.post("/api/members/register", json=member_data)
        assert member_response.status_code == 200
        journey_member_id = member_response.json()["id"]
        
        # 2. Make payments to earn points
        payments = [100.0, 150.0, 200.0]  # Total: 45 points (100+150+200)/10
        for amount in payments:
            payment_response = client.post(
                f"/api/members/{journey_member_id}/payments",
                json={"amount": amount, "method": "Cash", "note": f"Journey payment {amount}"},
                headers=headers
            )
            assert payment_response.status_code == 200
        
        # 3. Check total points (initial 5 + 45 earned = 50 points)
        member = client.get(f"/api/members/{journey_member_id}", headers=headers).json()
        assert member["points"] == 50  # Should be Bronze level (50 points)
        
        # 4. Check level
        level_data = client.get(f"/api/members/{journey_member_id}/level", headers=headers).json()
        assert level_data["current_level"]["name"] == "Bronze"
        
        # 5. Add more points to reach Argent (need 51+ points)
        client.post(
            f"/api/members/{journey_member_id}/points",
            json={"points": 10, "transaction_type": "bonus", "description": "Level up test"},
            headers=headers
        )
        
        # 6. Check level updated to Argent
        level_data = client.get(f"/api/members/{journey_member_id}/level", headers=headers).json()
        assert level_data["current_level"]["name"] == "Argent"
        
        # 7. Create redemption with sufficient points
        rewards = client.get("/api/rewards?active=true").json()
        affordable_reward = min([r for r in rewards if r["cost_points"] <= 60], key=lambda r: r["cost_points"])
        
        redemption_response = client.post(
            f"/api/members/{journey_member_id}/redemptions",
            json={"reward_id": affordable_reward["id"], "note": "Journey test redemption"},
            headers=headers
        )
        assert redemption_response.status_code == 200
        
        # 8. Approve redemption
        redemption = redemption_response.json()
        approve_response = client.put(
            f"/api/redemptions/{redemption['id']}/approve",
            json={"note": "Journey test approval"},
            headers=headers
        )
        assert approve_response.status_code == 200
        
        # 9. Verify points were deducted but member still has level
        member_final = client.get(f"/api/members/{journey_member_id}", headers=headers).json()
        assert member_final["points"] == 60 - affordable_reward["cost_points"]
        
        # Level should still be based on total earned, not current balance
        level_final = client.get(f"/api/members/{journey_member_id}/level", headers=headers).json()
        assert level_final["current_level"]["name"] == "Argent"  # Based on earned (60 points), not current balance

# Run all tests
def run_all_tests():
    """Run all test classes"""
    print("🧪 Running comprehensive gamification test suite...")
    
    # Run pytest programmatically
    pytest_args = [
        __file__,
        "-v", 
        "--tb=short",
        "--durations=10"
    ]
    
    return pytest.main(pytest_args)

if __name__ == "__main__":
    run_all_tests()