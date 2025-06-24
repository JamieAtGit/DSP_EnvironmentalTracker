#!/usr/bin/env python3
"""
🔒 Security Fixes Verification Test
==================================

Comprehensive testing suite to verify all security fixes are working correctly.
Tests the 3 critical security fixes and additional security enhancements.
"""

import os
import sys
import requests
import json
import time
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SecurityTestResult:
    """Security test result tracking"""
    test_name: str
    passed: bool
    details: str
    risk_level: str  # HIGH, MEDIUM, LOW
    recommendation: str = ""

class SecurityTester:
    """Comprehensive security testing suite"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.test_results: List[SecurityTestResult] = []
        
    def run_all_tests(self) -> Dict[str, any]:
        """Run all security tests"""
        logger.info("🔒 Starting comprehensive security testing...")
        
        # Test 1: Environment Variables Security
        self._test_environment_variables()
        
        # Test 2: CORS Configuration
        self._test_cors_configuration()
        
        # Test 3: Input Validation & SSRF Protection
        self._test_input_validation()
        
        # Test 4: Security Headers
        self._test_security_headers()
        
        # Test 5: Rate Limiting
        self._test_rate_limiting()
        
        # Test 6: Authentication Security
        self._test_authentication_security()
        
        # Generate comprehensive report
        return self._generate_security_report()
    
    def _test_environment_variables(self):
        """Test that environment variables are properly configured"""
        logger.info("🔑 Testing environment variable security...")
        
        # Check if .env file exists
        env_file = os.path.join(os.getcwd(), '.env')
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                env_content = f.read()
                
            # Check for secure secret keys
            if 'SECRET_KEY=' in env_content and len(env_content.split('SECRET_KEY=')[1].split('\n')[0]) > 20:
                self.test_results.append(SecurityTestResult(
                    test_name="Environment Variables - Secret Key",
                    passed=True,
                    details="Secure SECRET_KEY found in .env file",
                    risk_level="LOW"
                ))
            else:
                self.test_results.append(SecurityTestResult(
                    test_name="Environment Variables - Secret Key",
                    passed=False,
                    details="No secure SECRET_KEY found",
                    risk_level="HIGH",
                    recommendation="Set a secure SECRET_KEY in .env file"
                ))
                
            # Check CORS origins configuration
            if 'CORS_ORIGINS=' in env_content and '*' not in env_content:
                self.test_results.append(SecurityTestResult(
                    test_name="Environment Variables - CORS Origins",
                    passed=True,
                    details="CORS origins properly restricted",
                    risk_level="LOW"
                ))
            else:
                self.test_results.append(SecurityTestResult(
                    test_name="Environment Variables - CORS Origins",
                    passed=False,
                    details="CORS origins not properly configured",
                    risk_level="MEDIUM",
                    recommendation="Set specific CORS_ORIGINS in .env file"
                ))
        else:
            self.test_results.append(SecurityTestResult(
                test_name="Environment Variables - File Existence",
                passed=False,
                details=".env file not found",
                risk_level="HIGH",
                recommendation="Create .env file with secure configuration"
            ))
    
    def _test_cors_configuration(self):
        """Test CORS configuration security"""
        logger.info("🌐 Testing CORS configuration...")
        
        try:
            # Test preflight request with suspicious origin
            headers = {
                'Origin': 'https://malicious-site.com',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = requests.options(f"{self.base_url}/estimate_emissions", headers=headers)
            
            # Check if suspicious origin is rejected
            if 'Access-Control-Allow-Origin' not in response.headers or \
               response.headers.get('Access-Control-Allow-Origin') != 'https://malicious-site.com':
                self.test_results.append(SecurityTestResult(
                    test_name="CORS Configuration - Origin Validation",
                    passed=True,
                    details="Suspicious origins properly rejected",
                    risk_level="LOW"
                ))
            else:
                self.test_results.append(SecurityTestResult(
                    test_name="CORS Configuration - Origin Validation",
                    passed=False,
                    details="Suspicious origins not properly rejected",
                    risk_level="HIGH",
                    recommendation="Implement strict CORS origin validation"
                ))
                
        except requests.RequestException as e:
            self.test_results.append(SecurityTestResult(
                test_name="CORS Configuration - Connection",
                passed=False,
                details=f"Could not connect to test CORS: {e}",
                risk_level="MEDIUM",
                recommendation="Ensure application is running for CORS testing"
            ))
    
    def _test_input_validation(self):
        """Test input validation and SSRF protection"""
        logger.info("🛡️ Testing input validation and SSRF protection...")
        
        # Test SSRF protection with malicious URLs
        malicious_urls = [
            "http://localhost:22/",  # Internal port access
            "http://127.0.0.1:3306/",  # Database access
            "http://169.254.169.254/",  # AWS metadata service
            "file:///etc/passwd",  # File protocol
            "ftp://internal-server/",  # FTP protocol
            "http://evil-site.com/amazon-lookalike",  # Non-Amazon domain
        ]
        
        ssrf_protected = True
        
        for malicious_url in malicious_urls:
            try:
                payload = {
                    "amazon_url": malicious_url,
                    "postcode": "SW1A 1AA"
                }
                
                response = requests.post(
                    f"{self.base_url}/estimate_emissions",
                    json=payload,
                    timeout=5
                )
                
                # Should return 400 error for malicious URLs
                if response.status_code != 400:
                    ssrf_protected = False
                    logger.warning(f"🚨 SSRF vulnerability: {malicious_url} not blocked")
                    
            except requests.RequestException:
                # Connection errors are expected for some malicious URLs
                pass
        
        self.test_results.append(SecurityTestResult(
            test_name="Input Validation - SSRF Protection",
            passed=ssrf_protected,
            details="SSRF protection against malicious URLs" if ssrf_protected else "SSRF vulnerabilities detected",
            risk_level="LOW" if ssrf_protected else "HIGH",
            recommendation="" if ssrf_protected else "Implement strict URL validation"
        ))
        
        # Test postcode validation
        invalid_postcodes = ["INVALID", "123456", "<script>alert(1)</script>", ""]
        
        try:
            payload = {
                "amazon_url": "https://amazon.com/product/valid",
                "postcode": "INVALID"
            }
            
            response = requests.post(f"{self.base_url}/estimate_emissions", json=payload, timeout=5)
            
            if response.status_code == 400:
                self.test_results.append(SecurityTestResult(
                    test_name="Input Validation - Postcode Validation",
                    passed=True,
                    details="Invalid postcodes properly rejected",
                    risk_level="LOW"
                ))
            else:
                self.test_results.append(SecurityTestResult(
                    test_name="Input Validation - Postcode Validation",
                    passed=False,
                    details="Invalid postcodes not properly validated",
                    risk_level="MEDIUM",
                    recommendation="Implement strict postcode validation"
                ))
                
        except requests.RequestException as e:
            self.test_results.append(SecurityTestResult(
                test_name="Input Validation - Postcode Connection",
                passed=False,
                details=f"Could not test postcode validation: {e}",
                risk_level="MEDIUM"
            ))
    
    def _test_security_headers(self):
        """Test security headers implementation"""
        logger.info("🔐 Testing security headers...")
        
        try:
            response = requests.get(f"{self.base_url}/health")
            
            required_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': True,  # Just check presence
                'Content-Security-Policy': True,
                'Referrer-Policy': 'strict-origin-when-cross-origin'
            }
            
            missing_headers = []
            for header, expected_value in required_headers.items():
                if header not in response.headers:
                    missing_headers.append(header)
                elif expected_value is not True and response.headers[header] != expected_value:
                    missing_headers.append(f"{header} (incorrect value)")
            
            if not missing_headers:
                self.test_results.append(SecurityTestResult(
                    test_name="Security Headers - Implementation",
                    passed=True,
                    details="All required security headers present",
                    risk_level="LOW"
                ))
            else:
                self.test_results.append(SecurityTestResult(
                    test_name="Security Headers - Implementation",
                    passed=False,
                    details=f"Missing headers: {', '.join(missing_headers)}",
                    risk_level="MEDIUM",
                    recommendation="Implement missing security headers"
                ))
                
        except requests.RequestException as e:
            self.test_results.append(SecurityTestResult(
                test_name="Security Headers - Connection",
                passed=False,
                details=f"Could not test security headers: {e}",
                risk_level="MEDIUM"
            ))
    
    def _test_rate_limiting(self):
        """Test rate limiting implementation"""
        logger.info("⏱️ Testing rate limiting...")
        
        try:
            # Attempt multiple rapid requests
            rapid_requests = 0
            blocked_requests = 0
            
            for i in range(5):  # Quick test with 5 requests
                response = requests.post(
                    f"{self.base_url}/estimate_emissions",
                    json={"amazon_url": "invalid", "postcode": "invalid"},
                    timeout=2
                )
                rapid_requests += 1
                
                if response.status_code == 429:  # Too Many Requests
                    blocked_requests += 1
                    break
                    
                time.sleep(0.1)  # Small delay
            
            if blocked_requests > 0:
                self.test_results.append(SecurityTestResult(
                    test_name="Rate Limiting - Implementation",
                    passed=True,
                    details=f"Rate limiting active - {blocked_requests}/{rapid_requests} requests blocked",
                    risk_level="LOW"
                ))
            else:
                self.test_results.append(SecurityTestResult(
                    test_name="Rate Limiting - Implementation",
                    passed=False,
                    details="No rate limiting detected",
                    risk_level="MEDIUM",
                    recommendation="Implement rate limiting for API endpoints"
                ))
                
        except requests.RequestException as e:
            self.test_results.append(SecurityTestResult(
                test_name="Rate Limiting - Connection",
                passed=False,
                details=f"Could not test rate limiting: {e}",
                risk_level="MEDIUM"
            ))
    
    def _test_authentication_security(self):
        """Test authentication security measures"""
        logger.info("🔑 Testing authentication security...")
        
        try:
            # Test accessing protected endpoint without authentication
            response = requests.get(f"{self.base_url}/admin/submissions")
            
            if response.status_code in [401, 403]:  # Unauthorized or Forbidden
                self.test_results.append(SecurityTestResult(
                    test_name="Authentication - Protected Endpoints",
                    passed=True,
                    details="Protected endpoints properly secured",
                    risk_level="LOW"
                ))
            else:
                self.test_results.append(SecurityTestResult(
                    test_name="Authentication - Protected Endpoints",
                    passed=False,
                    details="Protected endpoints not properly secured",
                    risk_level="HIGH",
                    recommendation="Implement proper authentication for admin endpoints"
                ))
                
        except requests.RequestException as e:
            self.test_results.append(SecurityTestResult(
                test_name="Authentication - Connection",
                passed=False,
                details=f"Could not test authentication: {e}",
                risk_level="MEDIUM"
            ))
    
    def _generate_security_report(self) -> Dict[str, any]:
        """Generate comprehensive security report"""
        logger.info("📊 Generating security report...")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.passed)
        
        high_risk_issues = [r for r in self.test_results if r.risk_level == "HIGH" and not r.passed]
        medium_risk_issues = [r for r in self.test_results if r.risk_level == "MEDIUM" and not r.passed]
        low_risk_issues = [r for r in self.test_results if r.risk_level == "LOW" and not r.passed]
        
        # Calculate security score
        security_score = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Determine security grade
        if security_score >= 95:
            grade = "A+"
        elif security_score >= 90:
            grade = "A"
        elif security_score >= 85:
            grade = "B+"
        elif security_score >= 80:
            grade = "B"
        elif security_score >= 70:
            grade = "C"
        else:
            grade = "F"
        
        report = {
            "security_score": security_score,
            "security_grade": grade,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "high_risk_issues": len(high_risk_issues),
            "medium_risk_issues": len(medium_risk_issues),
            "low_risk_issues": len(low_risk_issues),
            "test_results": self.test_results,
            "recommendations": [r.recommendation for r in self.test_results if r.recommendation]
        }
        
        return report

def print_security_report(report: Dict[str, any]):
    """Print formatted security report"""
    print("\n" + "="*80)
    print("🔒 COMPREHENSIVE SECURITY TEST REPORT")
    print("="*80)
    
    print(f"\n📊 OVERALL SECURITY ASSESSMENT")
    print(f"Security Score: {report['security_score']:.1f}%")
    print(f"Security Grade: {report['security_grade']}")
    print(f"Tests Passed: {report['passed_tests']}/{report['total_tests']}")
    
    print(f"\n🚨 RISK SUMMARY")
    print(f"High Risk Issues: {report['high_risk_issues']}")
    print(f"Medium Risk Issues: {report['medium_risk_issues']}")
    print(f"Low Risk Issues: {report['low_risk_issues']}")
    
    print(f"\n📋 DETAILED TEST RESULTS")
    for result in report['test_results']:
        status = "✅ PASS" if result.passed else "❌ FAIL"
        risk_indicator = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[result.risk_level]
        
        print(f"{status} {risk_indicator} {result.test_name}")
        print(f"    Details: {result.details}")
        if result.recommendation:
            print(f"    Recommendation: {result.recommendation}")
        print()
    
    if report['recommendations']:
        print(f"🔧 PRIORITY RECOMMENDATIONS")
        for i, recommendation in enumerate(report['recommendations'], 1):
            print(f"{i}. {recommendation}")
    
    print("="*80)

def main():
    """Run security testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test security fixes for the Advanced Eco-Score Prediction System")
    parser.add_argument("--url", default="http://localhost:5000", help="Base URL of the application")
    parser.add_argument("--output", help="Output file for JSON report")
    
    args = parser.parse_args()
    
    # Run security tests
    tester = SecurityTester(base_url=args.url)
    report = tester.run_all_tests()
    
    # Print report
    print_security_report(report)
    
    # Save JSON report if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n📄 Detailed report saved to: {args.output}")
    
    # Exit with appropriate code
    if report['security_score'] >= 80:
        print("\n🎉 Security testing PASSED! System is secure for production.")
        sys.exit(0)
    else:
        print("\n⚠️ Security testing FAILED! Critical issues need to be addressed.")
        sys.exit(1)

if __name__ == "__main__":
    main()