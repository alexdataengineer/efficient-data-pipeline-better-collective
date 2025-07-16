#!/usr/bin/env python3
"""
Test script for the Efficient Data Pipeline
Tests basic functionality without external dependencies
"""

import os
import sys
from pathlib import Path

def test_file_existence():
    """Test if the CSV file exists"""
    csv_path = "/Users/alexsandersilveira/Downloads/itineraries.csv"
    
    if os.path.exists(csv_path):
        file_size = os.path.getsize(csv_path) / (1024 * 1024)  # MB
        print(f"✓ CSV file found: {csv_path}")
        print(f"  File size: {file_size:.1f} MB")
        return True
    else:
        print(f"✗ CSV file not found: {csv_path}")
        print("Please ensure the file exists at the specified path")
        return False

def test_dependencies():
    """Test if required dependencies are available"""
    required_packages = [
        'pandas',
        'numpy', 
        'matplotlib',
        'seaborn',
        'chardet',
        'dask'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is available")
        except ImportError:
            print(f"✗ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True

def test_directory_structure():
    """Test if required directories can be created"""
    test_dirs = ['visualizations', 'output']
    
    for dir_name in test_dirs:
        try:
            Path(dir_name).mkdir(exist_ok=True)
            print(f"✓ Directory '{dir_name}' is accessible")
        except Exception as e:
            print(f"✗ Cannot create directory '{dir_name}': {e}")
            return False
    
    return True

def simulate_pipeline_structure():
    """Simulate the pipeline structure without running the full analysis"""
    print("\n" + "="*60)
    print("PIPELINE STRUCTURE SIMULATION")
    print("="*60)
    
    pipeline_steps = [
        "1. File property detection (encoding, separator)",
        "2. File structure analysis (rows, columns, size)",
        "3. Sample data extraction",
        "4. Null value analysis (chunked processing)",
        "5. Descriptive statistics calculation (streaming)",
        "6. Visualization generation (memory-limited)",
        "7. Summary report generation"
    ]
    
    for step in pipeline_steps:
        print(f"✓ {step}")
    
    print("\nMemory efficiency features:")
    memory_features = [
        "- Chunked processing (10,000 rows per chunk)",
        "- Explicit memory management (chunk deletion)",
        "- Limited sampling for visualizations",
        "- Streaming statistics calculation",
        "- Efficient data type usage"
    ]
    
    for feature in memory_features:
        print(f"  {feature}")

def main():
    """Run all tests"""
    print("EFFICIENT DATA PIPELINE - TEST SUITE")
    print("="*50)
    
    tests = [
        ("File existence", test_file_existence),
        ("Dependencies", test_dependencies),
        ("Directory structure", test_directory_structure)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        if not test_func():
            all_passed = False
    
    if all_passed:
        print("\n✓ All basic tests passed!")
        simulate_pipeline_structure()
        print("\nReady to run: python data_pipeline.py")
    else:
        print("\n✗ Some tests failed. Please fix issues before running the pipeline.")
        sys.exit(1)

if __name__ == "__main__":
    main() 