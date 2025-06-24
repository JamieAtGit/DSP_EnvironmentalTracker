#!/usr/bin/env python3
"""
⚡ Intelligent Caching System for ML Predictions
==============================================

Theoretical Foundation:
- Cache Replacement Algorithms: LRU, LFU, FIFO analysis
- Hash Tables: O(1) average case lookup complexity
- Locality of Reference: Temporal and spatial locality principles
- Cache Coherence: Consistency models for distributed caching

Architecture:
- Multi-level caching (L1: Memory, L2: Redis, L3: Disk)
- Intelligent cache warming based on usage patterns
- Automatic cache invalidation for model updates
- Performance monitoring and optimization
"""

import redis
import hashlib
import pickle
import json
import time
import numpy as np
import pandas as pd
from functools import wraps, lru_cache
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
import logging
from dataclasses import dataclass, asdict
from collections import OrderedDict, defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aioredis
from datetime import datetime, timedelta
import psutil
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CacheStats:
    """Cache performance statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_requests: int = 0
    avg_response_time: float = 0.0
    cache_size: int = 0
    memory_usage_mb: float = 0.0
    hit_rate: float = 0.0

@dataclass
class CacheEntry:
    """Individual cache entry with metadata"""
    key: str
    value: Any
    timestamp: float
    access_count: int
    last_access: float
    size_bytes: int
    ttl: Optional[float] = None
    tags: Optional[List[str]] = None

class LRUCache:
    """
    Thread-safe LRU Cache implementation
    
    Theory: Least Recently Used replacement policy
    Complexity: O(1) for get/put operations using HashMap + DoublyLinkedList
    """
    
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = threading.RLock()
        self.stats = CacheStats()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache with LRU update"""
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                value = self.cache.pop(key)
                self.cache[key] = value
                self.stats.hits += 1
                return value.value if hasattr(value, 'value') else value
            
            self.stats.misses += 1
            return None
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Put item in cache with automatic eviction"""
        with self.lock:
            current_time = time.time()
            
            # Check if key already exists
            if key in self.cache:
                self.cache.pop(key)
            elif len(self.cache) >= self.capacity:
                # Evict least recently used item
                oldest_key = next(iter(self.cache))
                self.cache.pop(oldest_key)
                self.stats.evictions += 1
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=current_time,
                access_count=0,
                last_access=current_time,
                size_bytes=len(pickle.dumps(value)),
                ttl=ttl
            )
            
            self.cache[key] = entry
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.stats = CacheStats()

class IntelligentCacheSystem:
    """
    Multi-level intelligent caching system for ML predictions
    
    Features:
    1. L1 Cache: In-memory LRU cache for ultra-fast access
    2. L2 Cache: Redis for distributed caching
    3. L3 Cache: Disk-based persistence for large datasets
    4. Intelligent cache warming based on usage patterns
    5. Automatic invalidation on model updates
    6. Performance monitoring and optimization
    """
    
    def __init__(self, 
                 redis_url: str = "redis://localhost:6379",
                 l1_capacity: int = 1000,
                 l2_ttl: int = 3600,
                 enable_l3_cache: bool = True,
                 cache_dir: str = "./cache"):
        """
        Initialize multi-level cache system
        
        Args:
            redis_url: Redis connection URL
            l1_capacity: L1 cache capacity (in-memory)
            l2_ttl: L2 cache TTL in seconds
            enable_l3_cache: Enable disk-based L3 cache
            cache_dir: Directory for L3 cache files
        """
        
        # L1 Cache: In-memory LRU
        self.l1_cache = LRUCache(capacity=l1_capacity)
        
        # L2 Cache: Redis
        try:
            self.redis_client = redis.Redis.from_url(redis_url, decode_responses=False)
            self.redis_client.ping()  # Test connection
            self.redis_available = True
            logger.info("Redis L2 cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. L2 cache disabled.")
            self.redis_client = None
            self.redis_available = False
        
        # L3 Cache: Disk-based
        self.enable_l3_cache = enable_l3_cache
        self.cache_dir = cache_dir
        if enable_l3_cache:
            os.makedirs(cache_dir, exist_ok=True)
        
        # Configuration
        self.l2_ttl = l2_ttl
        
        # Performance monitoring
        self.performance_stats = {
            'l1': CacheStats(),
            'l2': CacheStats(),
            'l3': CacheStats(),
            'overall': CacheStats()
        }
        
        # Cache warming patterns
        self.access_patterns = defaultdict(int)
        self.warming_enabled = True
        
        # Model version tracking for cache invalidation
        self.model_version = None
        
        logger.info("Intelligent Cache System initialized")
    
    def _generate_cache_key(self, data: Any, prefix: str = "pred") -> str:
        """
        Generate deterministic cache key from input data
        
        Args:
            data: Input data (dict, array, etc.)
            prefix: Key prefix for namespace separation
            
        Returns:
            Hexadecimal hash string
        """
        # Serialize data to string
        if isinstance(data, dict):
            # Sort dict for deterministic hashing
            data_str = json.dumps(data, sort_keys=True)
        elif isinstance(data, np.ndarray):
            data_str = np.array2string(data, precision=6)
        else:
            data_str = str(data)
        
        # Add model version to key for automatic invalidation
        if self.model_version:
            data_str += f"_v{self.model_version}"
        
        # Generate hash
        hash_obj = hashlib.sha256(data_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()[:16]}"
    
    def _get_from_l1(self, key: str) -> Tuple[bool, Any]:
        """Get from L1 cache"""
        start_time = time.time()
        value = self.l1_cache.get(key)
        response_time = time.time() - start_time
        
        self.performance_stats['l1'].total_requests += 1
        if value is not None:
            self.performance_stats['l1'].hits += 1
            return True, value
        else:
            self.performance_stats['l1'].misses += 1
            return False, None
    
    def _put_to_l1(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Put to L1 cache"""
        self.l1_cache.put(key, value, ttl)
    
    def _get_from_l2(self, key: str) -> Tuple[bool, Any]:
        """Get from L2 (Redis) cache"""
        if not self.redis_available:
            return False, None
        
        start_time = time.time()
        try:
            cached_data = self.redis_client.get(key)
            response_time = time.time() - start_time
            
            self.performance_stats['l2'].total_requests += 1
            
            if cached_data:
                value = pickle.loads(cached_data)
                self.performance_stats['l2'].hits += 1
                
                # Promote to L1 cache
                self._put_to_l1(key, value)
                
                return True, value
            else:
                self.performance_stats['l2'].misses += 1
                return False, None
                
        except Exception as e:
            logger.warning(f"L2 cache get error: {e}")
            self.performance_stats['l2'].misses += 1
            return False, None
    
    def _put_to_l2(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Put to L2 (Redis) cache"""
        if not self.redis_available:
            return
        
        try:
            serialized_value = pickle.dumps(value)
            ttl = ttl or self.l2_ttl
            self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.warning(f"L2 cache put error: {e}")
    
    def _get_from_l3(self, key: str) -> Tuple[bool, Any]:
        """Get from L3 (disk) cache"""
        if not self.enable_l3_cache:
            return False, None
        
        start_time = time.time()
        filepath = os.path.join(self.cache_dir, f"{key}.pkl")
        
        try:
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    value = pickle.load(f)
                
                response_time = time.time() - start_time
                self.performance_stats['l3'].hits += 1
                
                # Promote to higher levels
                self._put_to_l2(key, value)
                self._put_to_l1(key, value)
                
                return True, value
            else:
                self.performance_stats['l3'].misses += 1
                return False, None
                
        except Exception as e:
            logger.warning(f"L3 cache get error: {e}")
            self.performance_stats['l3'].misses += 1
            return False, None
    
    def _put_to_l3(self, key: str, value: Any) -> None:
        """Put to L3 (disk) cache"""
        if not self.enable_l3_cache:
            return
        
        try:
            filepath = os.path.join(self.cache_dir, f"{key}.pkl")
            with open(filepath, 'wb') as f:
                pickle.dump(value, f)
        except Exception as e:
            logger.warning(f"L3 cache put error: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Multi-level cache get with automatic promotion
        
        Cache hierarchy: L1 (memory) -> L2 (Redis) -> L3 (disk)
        """
        overall_start = time.time()
        
        # Try L1 cache first (fastest)
        hit, value = self._get_from_l1(key)
        if hit:
            self._update_access_pattern(key)
            self._update_overall_stats(True, time.time() - overall_start)
            return value
        
        # Try L2 cache (Redis)
        hit, value = self._get_from_l2(key)
        if hit:
            self._update_access_pattern(key)
            self._update_overall_stats(True, time.time() - overall_start)
            return value
        
        # Try L3 cache (disk)
        hit, value = self._get_from_l3(key)
        if hit:
            self._update_access_pattern(key)
            self._update_overall_stats(True, time.time() - overall_start)
            return value
        
        # Cache miss across all levels
        self._update_overall_stats(False, time.time() - overall_start)
        return None
    
    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Multi-level cache put
        
        Stores in all available cache levels for maximum availability
        """
        # Store in all levels simultaneously
        self._put_to_l1(key, value, ttl)
        self._put_to_l2(key, value, ttl)
        self._put_to_l3(key, value)
        
        logger.debug(f"Cached value for key: {key}")
    
    def cached_prediction(self, ttl: Optional[int] = None, 
                         key_prefix: str = "pred"):
        """
        Decorator for caching ML predictions
        
        Args:
            ttl: Time to live in seconds
            key_prefix: Cache key prefix
            
        Usage:
            @cache.cached_prediction(ttl=1800)
            def predict_eco_score(features):
                return model.predict(features)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key from function arguments
                cache_data = {
                    'args': args,
                    'kwargs': kwargs,
                    'func_name': func.__name__
                }
                cache_key = self._generate_cache_key(cache_data, key_prefix)
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Cache miss - compute result
                start_time = time.time()
                result = func(*args, **kwargs)
                computation_time = time.time() - start_time
                
                # Store in cache
                self.put(cache_key, result, ttl)
                
                logger.debug(f"Computed and cached {func.__name__} in {computation_time:.3f}s")
                return result
            
            return wrapper
        return decorator
    
    def _update_access_pattern(self, key: str) -> None:
        """Update access patterns for intelligent cache warming"""
        if self.warming_enabled:
            self.access_patterns[key] += 1
    
    def _update_overall_stats(self, hit: bool, response_time: float) -> None:
        """Update overall performance statistics"""
        stats = self.performance_stats['overall']
        stats.total_requests += 1
        
        if hit:
            stats.hits += 1
        else:
            stats.misses += 1
        
        # Update moving average response time
        if stats.total_requests == 1:
            stats.avg_response_time = response_time
        else:
            alpha = 0.1  # Exponential moving average factor
            stats.avg_response_time = (1 - alpha) * stats.avg_response_time + alpha * response_time
        
        # Update hit rate
        stats.hit_rate = stats.hits / stats.total_requests
    
    def warm_cache(self, warm_data: List[Tuple[str, Any]], 
                   batch_size: int = 100) -> None:
        """
        Intelligent cache warming based on usage patterns
        
        Args:
            warm_data: List of (key, value) pairs to warm
            batch_size: Batch size for parallel warming
        """
        logger.info(f"Warming cache with {len(warm_data)} entries")
        
        # Sort by access frequency (most accessed first)
        sorted_data = sorted(
            warm_data,
            key=lambda x: self.access_patterns.get(x[0], 0),
            reverse=True
        )
        
        # Warm cache in batches
        for i in range(0, len(sorted_data), batch_size):
            batch = sorted_data[i:i + batch_size]
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [
                    executor.submit(self.put, key, value)
                    for key, value in batch
                ]
                
                # Wait for batch completion
                for future in futures:
                    future.result()
            
            logger.debug(f"Warmed batch {i//batch_size + 1}/{(len(sorted_data)-1)//batch_size + 1}")
        
        logger.info("Cache warming completed")
    
    def invalidate_model_cache(self, new_model_version: str) -> None:
        """
        Invalidate cache when model is updated
        
        Args:
            new_model_version: New model version identifier
        """
        logger.info(f"Invalidating cache for model version update: {new_model_version}")
        
        # Update model version for future cache keys
        old_version = self.model_version
        self.model_version = new_model_version
        
        # Clear L1 cache
        self.l1_cache.clear()
        
        # Clear L2 cache (Redis) - pattern-based deletion
        if self.redis_available:
            try:
                # Delete keys with old model version
                if old_version:
                    pattern = f"*_v{old_version}"
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"L2 cache invalidation error: {e}")
        
        # Clear L3 cache files
        if self.enable_l3_cache:
            try:
                for filename in os.listdir(self.cache_dir):
                    if old_version and f"_v{old_version}" in filename:
                        filepath = os.path.join(self.cache_dir, filename)
                        os.remove(filepath)
            except Exception as e:
                logger.warning(f"L3 cache invalidation error: {e}")
        
        logger.info("Cache invalidation completed")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache performance statistics"""
        # Calculate memory usage
        memory_info = psutil.Process().memory_info()
        memory_usage_mb = memory_info.rss / 1024 / 1024
        
        # Update cache sizes
        self.performance_stats['l1'].cache_size = len(self.l1_cache.cache)
        
        if self.redis_available:
            try:
                self.performance_stats['l2'].cache_size = self.redis_client.dbsize()
            except:
                pass
        
        if self.enable_l3_cache:
            try:
                cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.pkl')]
                self.performance_stats['l3'].cache_size = len(cache_files)
            except:
                pass
        
        # Calculate hit rates
        for level_stats in self.performance_stats.values():
            if level_stats.total_requests > 0:
                level_stats.hit_rate = level_stats.hits / level_stats.total_requests
        
        return {
            'performance_stats': {
                level: asdict(stats) for level, stats in self.performance_stats.items()
            },
            'memory_usage_mb': memory_usage_mb,
            'access_patterns': dict(self.access_patterns),
            'model_version': self.model_version,
            'redis_available': self.redis_available,
            'l3_enabled': self.enable_l3_cache
        }
    
    def optimize_cache(self) -> Dict[str, Any]:
        """
        Automatic cache optimization based on performance metrics
        
        Returns:
            Optimization report
        """
        logger.info("Running cache optimization...")
        
        stats = self.get_performance_stats()
        optimizations = []
        
        # Check hit rates and suggest optimizations
        overall_hit_rate = stats['performance_stats']['overall']['hit_rate']
        
        if overall_hit_rate < 0.5:
            optimizations.append("Low hit rate detected. Consider increasing cache size or TTL.")
        
        # Check L1 cache utilization
        l1_hit_rate = stats['performance_stats']['l1']['hit_rate']
        if l1_hit_rate < 0.3:
            optimizations.append("L1 cache underutilized. Consider cache warming strategies.")
        
        # Check memory usage
        if stats['memory_usage_mb'] > 1000:  # 1GB threshold
            optimizations.append("High memory usage. Consider reducing L1 cache size.")
        
        # Identify hot keys for cache warming
        hot_keys = sorted(
            self.access_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]  # Top 20 most accessed keys
        
        optimization_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_hit_rate': overall_hit_rate,
            'memory_usage_mb': stats['memory_usage_mb'],
            'optimizations': optimizations,
            'hot_keys': hot_keys,
            'performance_stats': stats['performance_stats']
        }
        
        logger.info(f"Cache optimization completed. Hit rate: {overall_hit_rate:.2%}")
        
        return optimization_report
    
    def clear_all_caches(self) -> None:
        """Clear all cache levels"""
        logger.info("Clearing all cache levels...")
        
        # Clear L1
        self.l1_cache.clear()
        
        # Clear L2
        if self.redis_available:
            try:
                self.redis_client.flushdb()
            except Exception as e:
                logger.warning(f"L2 cache clear error: {e}")
        
        # Clear L3
        if self.enable_l3_cache:
            try:
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.pkl'):
                        filepath = os.path.join(self.cache_dir, filename)
                        os.remove(filepath)
            except Exception as e:
                logger.warning(f"L3 cache clear error: {e}")
        
        # Reset statistics
        self.performance_stats = {
            'l1': CacheStats(),
            'l2': CacheStats(), 
            'l3': CacheStats(),
            'overall': CacheStats()
        }
        self.access_patterns.clear()
        
        logger.info("All caches cleared")

def main():
    """Example usage and testing"""
    # Initialize cache system
    cache = IntelligentCacheSystem(
        redis_url="redis://localhost:6379",
        l1_capacity=500,
        l2_ttl=1800,  # 30 minutes
        enable_l3_cache=True
    )
    
    # Example: Cache ML predictions
    @cache.cached_prediction(ttl=3600)  # 1 hour cache
    def predict_eco_score(features):
        # Simulate ML computation
        time.sleep(0.1)  # Simulate model inference time
        return {"prediction": "A+", "confidence": 0.95}
    
    # Test the caching system
    print("Testing cache performance...")
    
    test_features = {"material": "plastic", "weight": 0.5, "transport": "ship"}
    
    # First call - cache miss
    start_time = time.time()
    result1 = predict_eco_score(test_features)
    time1 = time.time() - start_time
    print(f"First call (cache miss): {time1:.3f}s")
    
    # Second call - cache hit
    start_time = time.time()
    result2 = predict_eco_score(test_features)
    time2 = time.time() - start_time
    print(f"Second call (cache hit): {time2:.3f}s")
    
    # Performance statistics
    stats = cache.get_performance_stats()
    print(f"Overall hit rate: {stats['performance_stats']['overall']['hit_rate']:.2%}")
    
    # Optimization report
    optimization_report = cache.optimize_cache()
    print("Optimization suggestions:", optimization_report['optimizations'])

if __name__ == "__main__":
    main()