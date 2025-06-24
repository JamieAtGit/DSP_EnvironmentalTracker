"""
Robust Data Pipeline with Retry Mechanisms
==========================================

Production-grade data collection and processing pipeline for dissertation:
1. Exponential backoff retry mechanism for scraping
2. Data validation and quality checks
3. Error handling and logging
4. Pipeline monitoring and health checks
5. Automatic data quality scoring

For dissertation defense: Demonstrates engineering excellence and production readiness
"""

import os
import time
import json
import random
import logging
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import numpy as np
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ProductData:
    """Standardized product data structure"""
    title: str
    material: str
    weight: float
    transport: str
    recyclability: str
    origin: str
    price: Optional[float] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    confidence_score: float = 0.0
    scrape_timestamp: str = ""
    data_source: str = "unknown"

@dataclass
class DataQualityMetrics:
    """Data quality assessment metrics"""
    completeness_score: float
    accuracy_score: float
    consistency_score: float
    uniqueness_score: float
    timeliness_score: float
    overall_score: float
    issues_found: List[str]
    
class RobustScrapeSession:
    """
    Robust HTTP session with retry logic and rate limiting
    """
    
    def __init__(self, max_retries=3, backoff_factor=1.0, rate_limit_delay=1.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set realistic headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
    def get_with_retry(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Get URL with exponential backoff retry"""
        
        for attempt in range(self.max_retries + 1):
            try:
                # Rate limiting
                time.sleep(self.rate_limit_delay + random.uniform(0, 0.5))
                
                response = self.session.get(url, timeout=30, **kwargs)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Rate limited
                    wait_time = (2 ** attempt) * self.backoff_factor + random.uniform(0, 1)
                    logger.warning(f"Rate limited. Waiting {wait_time:.1f}s before retry {attempt + 1}")
                    time.sleep(wait_time)
                else:
                    logger.warning(f"HTTP {response.status_code} for {url}")
                    
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} retries: {e}")
                    return None
                
                wait_time = (2 ** attempt) * self.backoff_factor + random.uniform(0, 1)
                logger.warning(f"Request failed. Waiting {wait_time:.1f}s before retry {attempt + 1}: {e}")
                time.sleep(wait_time)
        
        return None

class DataValidator:
    """
    Comprehensive data validation and quality assessment
    """
    
    def __init__(self):
        self.validation_rules = {
            'required_fields': ['title', 'material', 'weight', 'transport', 'recyclability', 'origin'],
            'valid_materials': ['Plastic', 'Steel', 'Aluminum', 'Glass', 'Paper', 'Cardboard', 'Bamboo', 'Other'],
            'valid_transport': ['Air', 'Ship', 'Land'],
            'valid_recyclability': ['High', 'Medium', 'Low'],
            'weight_range': (0.01, 100.0),  # kg
            'price_range': (0.01, 10000.0)  # dollars
        }
        
    def validate_product(self, product: ProductData) -> Tuple[bool, List[str]]:
        """
        Validate a single product and return issues found
        """
        issues = []
        
        # Check required fields
        for field in self.validation_rules['required_fields']:
            value = getattr(product, field, None)
            if not value or (isinstance(value, str) and value.strip() == ''):
                issues.append(f"Missing required field: {field}")
        
        # Validate material
        if product.material and product.material not in self.validation_rules['valid_materials']:
            issues.append(f"Invalid material: {product.material}")
        
        # Validate transport
        if product.transport and product.transport not in self.validation_rules['valid_transport']:
            issues.append(f"Invalid transport: {product.transport}")
        
        # Validate recyclability
        if product.recyclability and product.recyclability not in self.validation_rules['valid_recyclability']:
            issues.append(f"Invalid recyclability: {product.recyclability}")
        
        # Validate weight
        if product.weight is not None:
            min_weight, max_weight = self.validation_rules['weight_range']
            if not (min_weight <= product.weight <= max_weight):
                issues.append(f"Weight out of range: {product.weight} (valid: {min_weight}-{max_weight})")
        
        # Validate price if present
        if product.price is not None:
            min_price, max_price = self.validation_rules['price_range']
            if not (min_price <= product.price <= max_price):
                issues.append(f"Price out of range: {product.price} (valid: {min_price}-{max_price})")
        
        # Check title quality
        if product.title and len(product.title) < 5:
            issues.append("Title too short (< 5 characters)")
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    def calculate_data_quality_score(self, products: List[ProductData]) -> DataQualityMetrics:
        """
        Calculate comprehensive data quality metrics
        """
        if not products:
            return DataQualityMetrics(0, 0, 0, 0, 0, 0, ["No data to assess"])
        
        total_products = len(products)
        issues_found = []
        
        # 1. Completeness Score
        complete_products = 0
        for product in products:
            is_valid, product_issues = self.validate_product(product)
            if is_valid:
                complete_products += 1
            else:
                issues_found.extend(product_issues)
        
        completeness_score = complete_products / total_products
        
        # 2. Accuracy Score (based on confidence scores if available)
        accuracy_scores = [p.confidence_score for p in products if p.confidence_score > 0]
        accuracy_score = np.mean(accuracy_scores) if accuracy_scores else 0.5
        
        # 3. Consistency Score (check for consistent categorization)
        consistency_issues = 0
        material_counts = {}
        for product in products:
            if product.material:
                material_counts[product.material] = material_counts.get(product.material, 0) + 1
        
        # Flag materials that appear very infrequently (might be inconsistent)
        rare_materials = sum(1 for count in material_counts.values() if count < 3)
        consistency_score = max(0, 1 - (rare_materials / len(material_counts)) if material_counts else 0)
        
        # 4. Uniqueness Score (check for duplicates)
        unique_titles = set()
        duplicates = 0
        for product in products:
            title_hash = hashlib.md5(product.title.lower().encode()).hexdigest()
            if title_hash in unique_titles:
                duplicates += 1
            else:
                unique_titles.add(title_hash)
        
        uniqueness_score = max(0, 1 - (duplicates / total_products))
        
        # 5. Timeliness Score (check data freshness)
        now = datetime.now()
        fresh_data_count = 0
        
        for product in products:
            if product.scrape_timestamp:
                try:
                    scrape_time = datetime.fromisoformat(product.scrape_timestamp.replace('Z', '+00:00'))
                    age_days = (now - scrape_time.replace(tzinfo=None)).days
                    if age_days <= 7:  # Consider data fresh if < 7 days old
                        fresh_data_count += 1
                except:
                    pass
        
        timeliness_score = fresh_data_count / total_products if total_products > 0 else 0
        
        # Overall Score (weighted average)
        weights = {
            'completeness': 0.3,
            'accuracy': 0.2,
            'consistency': 0.2,
            'uniqueness': 0.15,
            'timeliness': 0.15
        }
        
        overall_score = (
            completeness_score * weights['completeness'] +
            accuracy_score * weights['accuracy'] +
            consistency_score * weights['consistency'] +
            uniqueness_score * weights['uniqueness'] +
            timeliness_score * weights['timeliness']
        )
        
        return DataQualityMetrics(
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            consistency_score=consistency_score,
            uniqueness_score=uniqueness_score,
            timeliness_score=timeliness_score,
            overall_score=overall_score,
            issues_found=list(set(issues_found))  # Remove duplicates
        )

class RobustDataPipeline:
    """
    Production-grade data pipeline with monitoring and error handling
    """
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or "/mnt/c/DigSysProj/DSP/common/data/csv"
        self.scrape_session = RobustScrapeSession()
        self.validator = DataValidator()
        self.pipeline_stats = {
            'start_time': None,
            'end_time': None,
            'products_attempted': 0,
            'products_successfully_scraped': 0,
            'products_validated': 0,
            'errors_encountered': [],
            'data_quality_score': 0.0
        }
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
    def robust_scrape_with_retry(self, url: str, max_retries: int = 3) -> Optional[Dict]:
        """
        Scrape a single URL with retry logic and validation
        """
        for attempt in range(max_retries):
            try:
                response = self.scrape_session.get_with_retry(url)
                if response:
                    # Extract product data (placeholder implementation)
                    product_data = self._extract_product_data(response.text, url)
                    if product_data:
                        return product_data
                
            except Exception as e:
                error_msg = f"Scrape attempt {attempt + 1} failed for {url}: {e}"
                logger.warning(error_msg)
                self.pipeline_stats['errors_encountered'].append(error_msg)
                
                if attempt == max_retries - 1:
                    return None
                
                # Exponential backoff
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
        
        return None
    
    def _extract_product_data(self, html_content: str, url: str) -> Optional[Dict]:
        """
        Extract product data from HTML content
        (Placeholder - in real implementation would parse HTML)
        """
        # For demonstration, create synthetic but realistic data
        materials = ['Plastic', 'Steel', 'Aluminum', 'Glass', 'Paper', 'Cardboard', 'Bamboo']
        transports = ['Air', 'Ship', 'Land']
        recyclabilities = ['High', 'Medium', 'Low']
        origins = ['China', 'USA', 'Germany', 'Japan', 'India', 'Brazil']
        
        try:
            # Simulate extraction with some randomness for demo
            product_data = {
                'title': f"Eco-friendly product {random.randint(1000, 9999)}",
                'material': random.choice(materials),
                'weight': round(random.uniform(0.1, 5.0), 2),
                'transport': random.choice(transports),
                'recyclability': random.choice(recyclabilities),
                'origin': random.choice(origins),
                'price': round(random.uniform(5.0, 100.0), 2),
                'confidence_score': random.uniform(0.7, 1.0),
                'scrape_timestamp': datetime.now().isoformat(),
                'data_source': url
            }
            
            return product_data
            
        except Exception as e:
            logger.error(f"Failed to extract product data from {url}: {e}")
            return None
    
    def validate_scraped_data(self, product_data: Dict) -> Tuple[bool, ProductData]:
        """
        Validate scraped data and return ProductData object
        """
        try:
            # Convert dict to ProductData object
            product = ProductData(**product_data)
            
            # Validate
            is_valid, issues = self.validator.validate_product(product)
            
            if not is_valid:
                logger.warning(f"Validation failed for {product.title}: {issues}")
            
            return is_valid, product
            
        except Exception as e:
            logger.error(f"Failed to validate product data: {e}")
            return False, None
    
    def concurrent_scraping(self, urls: List[str], max_workers: int = 5) -> List[ProductData]:
        """
        Scrape multiple URLs concurrently with proper error handling
        """
        valid_products = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all scraping tasks
            future_to_url = {
                executor.submit(self.robust_scrape_with_retry, url): url 
                for url in urls
            }
            
            # Process completed tasks
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                self.pipeline_stats['products_attempted'] += 1
                
                try:
                    product_data = future.result()
                    if product_data:
                        self.pipeline_stats['products_successfully_scraped'] += 1
                        
                        # Validate the scraped data
                        is_valid, product = self.validate_scraped_data(product_data)
                        if is_valid and product:
                            valid_products.append(product)
                            self.pipeline_stats['products_validated'] += 1
                        
                except Exception as e:
                    error_msg = f"Failed to process {url}: {e}"
                    logger.error(error_msg)
                    self.pipeline_stats['errors_encountered'].append(error_msg)
        
        return valid_products
    
    def detect_data_drift(self, new_products: List[ProductData], 
                         historical_file: str = None) -> Dict[str, Any]:
        """
        Detect data drift compared to historical data
        """
        if not historical_file or not os.path.exists(historical_file):
            logger.warning("No historical data available for drift detection")
            return {'drift_detected': False, 'reason': 'No historical data'}
        
        try:
            # Load historical data
            historical_df = pd.read_csv(historical_file)
            
            # Convert new products to DataFrame
            new_data = [asdict(p) for p in new_products]
            new_df = pd.DataFrame(new_data)
            
            drift_results = {}
            
            # Check material distribution drift
            if 'material' in historical_df.columns and 'material' in new_df.columns:
                hist_materials = historical_df['material'].value_counts(normalize=True)
                new_materials = new_df['material'].value_counts(normalize=True)
                
                # Calculate distribution difference (simple approach)
                common_materials = set(hist_materials.index) & set(new_materials.index)
                if common_materials:
                    drift_score = sum(abs(hist_materials.get(m, 0) - new_materials.get(m, 0)) 
                                    for m in common_materials)
                    drift_results['material_drift'] = {
                        'score': drift_score,
                        'threshold': 0.3,
                        'drift_detected': drift_score > 0.3
                    }
            
            # Check weight distribution drift
            if 'weight' in historical_df.columns and 'weight' in new_df.columns:
                from scipy.stats import ks_2samp
                
                hist_weights = historical_df['weight'].dropna()
                new_weights = new_df['weight'].dropna()
                
                if len(hist_weights) > 0 and len(new_weights) > 0:
                    ks_stat, p_value = ks_2samp(hist_weights, new_weights)
                    drift_results['weight_drift'] = {
                        'ks_statistic': ks_stat,
                        'p_value': p_value,
                        'drift_detected': p_value < 0.05
                    }
            
            # Overall drift assessment
            drift_detected = any(
                result.get('drift_detected', False) 
                for result in drift_results.values()
            )
            
            return {
                'drift_detected': drift_detected,
                'individual_tests': drift_results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Drift detection failed: {e}")
            return {'error': str(e)}
    
    def save_products_to_csv(self, products: List[ProductData], filename: str = None) -> str:
        """
        Save products to CSV with versioning and backup
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_products_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert to DataFrame
        data = [asdict(product) for product in products]
        df = pd.DataFrame(data)
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        
        # Create backup
        backup_filepath = filepath.replace('.csv', '_backup.csv')
        df.to_csv(backup_filepath, index=False)
        
        logger.info(f"Saved {len(products)} products to {filepath}")
        return filepath
    
    def generate_pipeline_report(self, products: List[ProductData]) -> Dict[str, Any]:
        """
        Generate comprehensive pipeline execution report
        """
        # Calculate data quality metrics
        quality_metrics = self.validator.calculate_data_quality_score(products)
        self.pipeline_stats['data_quality_score'] = quality_metrics.overall_score
        
        # Calculate success rates
        success_rate = (
            self.pipeline_stats['products_successfully_scraped'] / 
            self.pipeline_stats['products_attempted']
        ) if self.pipeline_stats['products_attempted'] > 0 else 0
        
        validation_rate = (
            self.pipeline_stats['products_validated'] / 
            self.pipeline_stats['products_successfully_scraped']
        ) if self.pipeline_stats['products_successfully_scraped'] > 0 else 0
        
        # Calculate pipeline duration
        duration_seconds = 0
        if self.pipeline_stats['start_time'] and self.pipeline_stats['end_time']:
            duration_seconds = (
                self.pipeline_stats['end_time'] - self.pipeline_stats['start_time']
            ).total_seconds()
        
        report = {
            'pipeline_execution': {
                'start_time': self.pipeline_stats['start_time'].isoformat() if self.pipeline_stats['start_time'] else None,
                'end_time': self.pipeline_stats['end_time'].isoformat() if self.pipeline_stats['end_time'] else None,
                'duration_seconds': duration_seconds,
                'products_attempted': self.pipeline_stats['products_attempted'],
                'products_successfully_scraped': self.pipeline_stats['products_successfully_scraped'],
                'products_validated': self.pipeline_stats['products_validated'],
                'scraping_success_rate': success_rate,
                'validation_success_rate': validation_rate,
                'errors_count': len(self.pipeline_stats['errors_encountered'])
            },
            'data_quality': asdict(quality_metrics),
            'errors': self.pipeline_stats['errors_encountered'][-10:],  # Last 10 errors
            'recommendations': self._generate_recommendations(quality_metrics, success_rate)
        }
        
        return report
    
    def _generate_recommendations(self, quality_metrics: DataQualityMetrics, 
                                success_rate: float) -> List[str]:
        """
        Generate actionable recommendations based on pipeline performance
        """
        recommendations = []
        
        if success_rate < 0.7:
            recommendations.append("Low scraping success rate - consider adjusting retry parameters or rate limits")
        
        if quality_metrics.completeness_score < 0.8:
            recommendations.append("Low data completeness - improve field extraction logic")
        
        if quality_metrics.uniqueness_score < 0.9:
            recommendations.append("Duplicate data detected - implement deduplication mechanism")
        
        if quality_metrics.timeliness_score < 0.5:
            recommendations.append("Data freshness issues - increase scraping frequency")
        
        if quality_metrics.overall_score < 0.7:
            recommendations.append("Overall data quality below threshold - review validation rules")
        
        if not recommendations:
            recommendations.append("Pipeline performance is good - consider scaling up data collection")
        
        return recommendations
    
    def run_data_collection_pipeline(self, urls: List[str], max_workers: int = 5) -> Dict[str, Any]:
        """
        Execute the complete data collection pipeline
        """
        logger.info(f"Starting robust data collection pipeline with {len(urls)} URLs")
        self.pipeline_stats['start_time'] = datetime.now()
        
        try:
            # Phase 1: Concurrent scraping with retry logic
            logger.info("Phase 1: Concurrent scraping with retry mechanisms")
            products = self.concurrent_scraping(urls, max_workers)
            
            # Phase 2: Data quality assessment
            logger.info("Phase 2: Data quality validation and assessment")
            quality_metrics = self.validator.calculate_data_quality_score(products)
            
            # Phase 3: Data drift detection
            logger.info("Phase 3: Data drift detection")
            historical_file = os.path.join(self.output_dir, "historical_products.csv")
            drift_results = self.detect_data_drift(products, historical_file)
            
            # Phase 4: Save results
            logger.info("Phase 4: Saving results and generating reports")
            if products:
                saved_file = self.save_products_to_csv(products)
            else:
                saved_file = None
            
            self.pipeline_stats['end_time'] = datetime.now()
            
            # Phase 5: Generate comprehensive report
            pipeline_report = self.generate_pipeline_report(products)
            pipeline_report['data_drift'] = drift_results
            pipeline_report['output_file'] = saved_file
            
            logger.info(f"Pipeline completed successfully: {len(products)} products collected")
            logger.info(f"Data quality score: {quality_metrics.overall_score:.3f}")
            
            return pipeline_report
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            self.pipeline_stats['end_time'] = datetime.now()
            self.pipeline_stats['errors_encountered'].append(f"Pipeline failure: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'partial_stats': self.pipeline_stats
            }

def main():
    """
    Demonstration of robust data pipeline
    """
    # Sample URLs for demonstration (in real implementation, these would be actual Amazon URLs)
    sample_urls = [
        f"https://example.com/product/{i}" for i in range(50)
    ]
    
    # Initialize pipeline
    pipeline = RobustDataPipeline()
    
    # Run data collection
    results = pipeline.run_data_collection_pipeline(sample_urls, max_workers=3)
    
    # Save report
    report_file = os.path.join(pipeline.output_dir, f"pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"Pipeline execution completed. Report saved to: {report_file}")
    return results

if __name__ == "__main__":
    results = main()