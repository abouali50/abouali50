#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class RegamBlockchainAPITester:
    def __init__(self, base_url="https://swift-regam.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status=200, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append(f"{name}: {str(e)}")
            return False, {}

    def test_system_info(self):
        """Test system info endpoint"""
        success, response = self.run_test(
            "System Info",
            "GET",
            "system/info"
        )
        if success:
            print(f"   Blockchain: {response.get('blockchain_name', 'N/A')}")
            print(f"   Mode: {response.get('mode', 'N/A')}")
        return success

    def test_blocks_list(self):
        """Test blocks list endpoint"""
        success, response = self.run_test(
            "Blocks List",
            "GET",
            "blocks",
            params={"limit": 5}
        )
        if success and 'blocks' in response:
            print(f"   Retrieved {len(response['blocks'])} blocks")
            if response['blocks']:
                block = response['blocks'][0]
                print(f"   Latest block height: {block.get('height', 'N/A')}")
        return success, response

    def test_block_detail(self, block_height=None):
        """Test individual block endpoint"""
        if not block_height:
            block_height = "1000000"  # Default test height
        
        success, response = self.run_test(
            f"Block Detail (#{block_height})",
            "GET",
            f"blocks/{block_height}"
        )
        if success and 'block' in response:
            print(f"   Block transactions: {len(response.get('transactions', []))}")
        return success

    def test_transaction_detail(self):
        """Test transaction detail endpoint"""
        test_hash = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        success, response = self.run_test(
            "Transaction Detail",
            "GET",
            f"tx/{test_hash}"
        )
        if success:
            print(f"   Transaction status: {response.get('status', 'N/A')}")
        return success

    def test_address_info(self):
        """Test address info endpoint"""
        test_address = "regam1abcdef1234567890abcdef1234567890abcdef"
        success, response = self.run_test(
            "Address Info",
            "GET",
            f"address/{test_address}"
        )
        if success and 'address' in response:
            print(f"   Address balance: {response['address'].get('balance', 'N/A')}")
            print(f"   Recent transactions: {len(response.get('recent_transactions', []))}")
        return success

    def test_validators(self):
        """Test validators endpoint"""
        success, response = self.run_test(
            "Validators List",
            "GET",
            "validators"
        )
        if success and 'validators' in response:
            print(f"   Total validators: {len(response['validators'])}")
            if response['validators']:
                validator = response['validators'][0]
                print(f"   Sample validator status: {validator.get('status', 'N/A')}")
        return success

    def test_search(self):
        """Test search endpoint"""
        test_queries = [
            ("123456", "block height"),
            ("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef", "transaction hash"),
            ("regam1abcdef1234567890abcdef1234567890abcdef", "address")
        ]
        
        all_passed = True
        for query, query_type in test_queries:
            success, response = self.run_test(
                f"Search ({query_type})",
                "GET",
                "search",
                params={"q": query}
            )
            if success and 'results' in response:
                print(f"   Search results: {len(response['results'])}")
            all_passed = all_passed and success
        
        return all_passed

    def test_wallet_balance(self):
        """Test wallet balance endpoint"""
        test_address = "regam1abcdef1234567890abcdef1234567890abcdef"
        success, response = self.run_test(
            "Wallet Balance",
            "GET",
            f"wallet/{test_address}/balance"
        )
        if success:
            print(f"   Balance: {response.get('balance', 'N/A')}")
            print(f"   Staked: {response.get('staked_balance', 'N/A')}")
        return success

    def test_wallet_transactions(self):
        """Test wallet transactions endpoint"""
        test_address = "regam1abcdef1234567890abcdef1234567890abcdef"
        success, response = self.run_test(
            "Wallet Transactions",
            "GET",
            f"wallet/{test_address}/transactions",
            params={"limit": 5}
        )
        if success and 'transactions' in response:
            print(f"   Wallet transactions: {len(response['transactions'])}")
        return success

    def test_fee_estimation(self):
        """Test fee estimation endpoint"""
        fee_data = {
            "from_address": "regam1abcdef1234567890abcdef1234567890abcdef",
            "to_address": "regam1fedcba0987654321fedcba0987654321fedcba",
            "amount": 10.5
        }
        success, response = self.run_test(
            "Fee Estimation",
            "POST",
            "wallet/estimateFee",
            data=fee_data
        )
        if success:
            print(f"   Estimated fee: {response.get('total_fee', 'N/A')}")
        return success

    def test_send_transaction(self):
        """Test send transaction endpoint"""
        send_data = {
            "from_address": "regam1abcdef1234567890abcdef1234567890abcdef",
            "to_address": "regam1fedcba0987654321fedcba0987654321fedcba",
            "amount": 10.5,
            "fee_estimate": 0.0001
        }
        success, response = self.run_test(
            "Send Transaction",
            "POST",
            "wallet/send",
            data=send_data
        )
        if success:
            print(f"   Transaction hash: {response.get('tx_hash', 'N/A')}")
            print(f"   Status: {response.get('status', 'N/A')}")
        return success

    def test_metrics_endpoints(self):
        """Test metrics endpoints"""
        endpoints = [
            ("metrics/tps", {"window": "5m"}),
            ("metrics/energy", {"window": "1h"})
        ]
        
        all_passed = True
        for endpoint, params in endpoints:
            success, response = self.run_test(
                f"Metrics - {endpoint}",
                "GET",
                endpoint,
                params=params
            )
            if success and 'data' in response:
                print(f"   Data points: {len(response['data'])}")
            all_passed = all_passed and success
        
        return all_passed

    def test_multi_wallet(self):
        """Test multi-wallet endpoint"""
        addresses = "regam1abc123,regam1def456,regam1ghi789"
        success, response = self.run_test(
            "Multi-Wallet Info",
            "GET",
            "wallet/multi",
            params={"addresses": addresses}
        )
        if success and 'wallets' in response:
            print(f"   Wallets retrieved: {len(response['wallets'])}")
        return success

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Regam Blockchain API Tests")
        print("=" * 50)
        
        # Test all endpoints
        test_results = []
        
        test_results.append(self.test_system_info())
        
        # Get a block height for detailed testing
        blocks_success, blocks_data = self.test_blocks_list()
        test_results.append(blocks_success)
        
        if blocks_success and blocks_data.get('blocks'):
            block_height = blocks_data['blocks'][0]['height']
            test_results.append(self.test_block_detail(block_height))
        else:
            test_results.append(self.test_block_detail())
        
        test_results.append(self.test_transaction_detail())
        test_results.append(self.test_address_info())
        test_results.append(self.test_validators())
        test_results.append(self.test_search())
        test_results.append(self.test_wallet_balance())
        test_results.append(self.test_wallet_transactions())
        test_results.append(self.test_fee_estimation())
        test_results.append(self.test_send_transaction())
        test_results.append(self.test_metrics_endpoints())
        test_results.append(self.test_multi_wallet())
        
        # Print results
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS")
        print("=" * 50)
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for failure in self.failed_tests:
                print(f"   - {failure}")
        else:
            print("\n🎉 ALL TESTS PASSED!")
        
        return self.tests_passed == self.tests_run

def main():
    tester = RegamBlockchainAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())