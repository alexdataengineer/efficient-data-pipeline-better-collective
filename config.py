"""
Configuration settings for the Efficient Data Pipeline
Centralizes all configurable parameters for easy modification
"""

import os
from pathlib import Path

class PipelineConfig:
    """Configuration class for the data pipeline"""
    
    # File paths
    CSV_PATH = "/Users/alexsandersilveira/Downloads/itineraries.csv"
    OUTPUT_DIR = "output"
    VISUALIZATIONS_DIR = "visualizations"
    REPORT_FILE = "analysis_report.txt"
    
    # Memory efficiency settings
    CHUNK_SIZE = 10000  # Number of rows to process at once
    MAX_VISUALIZATION_SAMPLES = 10000  # Limit samples for charts
    MAX_CATEGORIES_PLOT = 10  # Maximum categories to show in plots
    
    # Analysis settings
    SAMPLE_ROWS = 5  # Number of rows to show in sample
    MAX_NUMERIC_COLUMNS_VISUALIZE = 3  # Limit numeric columns for charts
    MAX_CATEGORICAL_COLUMNS_VISUALIZE = 3  # Limit categorical columns for charts
    
    # Visualization settings
    FIGURE_SIZE = (10, 6)
    DPI = 300
    CHART_STYLE = 'default'
    COLOR_PALETTE = "husl"
    
    # Logging settings
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    
    # Memory monitoring
    ENABLE_MEMORY_MONITORING = True
    MEMORY_WARNING_THRESHOLD_MB = 3000  # Warning at 3GB
    
    # Performance settings
    ENABLE_PROGRESS_BAR = True
    ENABLE_DETAILED_LOGGING = True
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        errors = []
        
        # Check if CSV file exists
        if not os.path.exists(cls.CSV_PATH):
            errors.append(f"CSV file not found: {cls.CSV_PATH}")
        
        # Validate chunk size
        if cls.CHUNK_SIZE <= 0:
            errors.append("CHUNK_SIZE must be positive")
        
        # Validate sample limits
        if cls.MAX_VISUALIZATION_SAMPLES <= 0:
            errors.append("MAX_VISUALIZATION_SAMPLES must be positive")
        
        return errors
    
    @classmethod
    def create_directories(cls):
        """Create necessary output directories"""
        directories = [cls.OUTPUT_DIR, cls.VISUALIZATIONS_DIR]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    @classmethod
    def get_file_info(cls):
        """Get information about the CSV file"""
        if os.path.exists(cls.CSV_PATH):
            file_size_mb = os.path.getsize(cls.CSV_PATH) / (1024 * 1024)
            return {
                'exists': True,
                'size_mb': file_size_mb,
                'path': cls.CSV_PATH
            }
        else:
            return {
                'exists': False,
                'size_mb': 0,
                'path': cls.CSV_PATH
            }
    
    @classmethod
    def estimate_memory_usage(cls, file_size_mb):
        """Estimate memory usage based on file size"""
        # Rough estimate: 2x file size for processing
        estimated_mb = file_size_mb * 2
        
        # Add buffer for overhead
        estimated_mb += 500  # 500MB buffer
        
        return estimated_mb
    
    @classmethod
    def get_memory_efficiency_tips(cls):
        """Get memory efficiency recommendations"""
        return [
            "Use chunked processing to avoid loading entire file",
            "Delete processed chunks immediately",
            "Limit visualization samples to prevent memory overflow",
            "Use appropriate data types (int8, float32, etc.)",
            "Monitor memory usage during processing",
            "Consider using Dask for very large files"
        ] 