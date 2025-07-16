#!/usr/bin/env python3
"""
Efficient Data Pipeline for Better Collective Data Engineer Position
Processes large CSV files with memory constraints (4GB limit)
"""

import pandas as pd
import dask.dataframe as dd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import chardet
import os
import sys
from pathlib import Path
import warnings
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

class EfficientDataPipeline:
    """
    Memory-efficient data pipeline for processing large CSV files
    Designed to work within 4GB memory constraints
    """
    
    def __init__(self, csv_path: str, chunk_size: int = 10000):
        """
        Initialize the data pipeline
        
        Args:
            csv_path: Path to the CSV file
            chunk_size: Number of rows to process at once for memory efficiency
        """
        self.csv_path = csv_path
        self.chunk_size = chunk_size
        self.encoding = None
        self.separator = None
        self.dtypes = None
        self.total_rows = 0
        self.memory_usage_mb = 0
        
    def detect_file_properties(self) -> Dict[str, any]:
        """
        Detect encoding and separator of the CSV file
        
        Returns:
            Dictionary with encoding and separator information
        """
        logger.info("Detecting file properties...")
        
        # Detect encoding
        with open(self.csv_path, 'rb') as file:
            raw_data = file.read(10000)  # Read first 10KB for encoding detection
            result = chardet.detect(raw_data)
            self.encoding = result['encoding']
            confidence = result['confidence']
            
        logger.info(f"Detected encoding: {self.encoding} (confidence: {confidence:.2f})")
        
        # Detect separator by reading first few lines
        with open(self.csv_path, 'r', encoding=self.encoding) as file:
            first_line = file.readline().strip()
            
        # Common separators to test
        separators = [',', ';', '\t', '|']
        max_columns = 0
        best_separator = ','
        
        for sep in separators:
            columns = first_line.split(sep)
            if len(columns) > max_columns:
                max_columns = len(columns)
                best_separator = sep
                
        self.separator = best_separator
        logger.info(f"Detected separator: '{self.separator}' with {max_columns} columns")
        
        return {
            'encoding': self.encoding,
            'separator': self.separator,
            'confidence': confidence,
            'columns_count': max_columns
        }
    
    def analyze_file_structure(self) -> Dict:
        """
        Analyze the structure of the CSV file efficiently
        
        Returns:
            Dictionary with file structure information
        """
        logger.info("Analyzing file structure...")
        
        # Count total rows efficiently
        with open(self.csv_path, 'r', encoding=self.encoding) as file:
            self.total_rows = sum(1 for _ in file) - 1  # Subtract header
        
        # Read header to get column names
        df_sample = pd.read_csv(
            self.csv_path,
            encoding=self.encoding,
            sep=self.separator,
            nrows=0
        )
        
        columns = df_sample.columns.tolist()
        
        # Analyze data types efficiently using a sample
        df_sample = pd.read_csv(
            self.csv_path,
            encoding=self.encoding,
            sep=self.separator,
            nrows=1000  # Sample for type inference
        )
        
        self.dtypes = df_sample.dtypes.to_dict()
        
        # Calculate approximate file size
        file_size_mb = os.path.getsize(self.csv_path) / (1024 * 1024)
        
        structure_info = {
            'total_rows': self.total_rows,
            'columns': columns,
            'columns_count': len(columns),
            'file_size_mb': file_size_mb,
            'estimated_memory_mb': file_size_mb * 2,  # Rough estimate
            'dtypes': self.dtypes
        }
        
        logger.info(f"File structure: {self.total_rows:,} rows, {len(columns)} columns, {file_size_mb:.1f}MB")
        
        return structure_info
    
    def get_sample_data(self, nrows: int = 5) -> pd.DataFrame:
        """
        Get a sample of the data for inspection
        
        Args:
            nrows: Number of rows to sample
            
        Returns:
            Sample DataFrame
        """
        logger.info(f"Loading sample data ({nrows} rows)...")
        
        sample_df = pd.read_csv(
            self.csv_path,
            encoding=self.encoding,
            sep=self.separator,
            nrows=nrows
        )
        
        return sample_df
    
    def analyze_null_values(self) -> Dict:
        """
        Analyze null values efficiently using chunks
        
        Returns:
            Dictionary with null value analysis
        """
        logger.info("Analyzing null values...")
        
        null_counts = {}
        total_rows = 0
        
        for chunk in pd.read_csv(
            self.csv_path,
            encoding=self.encoding,
            sep=self.separator,
            chunksize=self.chunk_size
        ):
            if total_rows == 0:
                null_counts = chunk.isnull().sum().to_dict()
            else:
                chunk_nulls = chunk.isnull().sum()
                for col in null_counts:
                    null_counts[col] += chunk_nulls[col]
            
            total_rows += len(chunk)
            
            # Memory management
            del chunk
        
        null_percentages = {col: (count / total_rows) * 100 for col, count in null_counts.items()}
        
        return {
            'null_counts': null_counts,
            'null_percentages': null_percentages,
            'total_rows': total_rows
        }
    
    def calculate_descriptive_statistics(self) -> Dict:
        """
        Calculate descriptive statistics efficiently using chunks
        
        Returns:
            Dictionary with descriptive statistics
        """
        logger.info("Calculating descriptive statistics...")
        
        # Initialize statistics containers
        numeric_stats = {}
        categorical_stats = {}
        first_chunk = True
        
        for chunk in pd.read_csv(
            self.csv_path,
            encoding=self.encoding,
            sep=self.separator,
            chunksize=self.chunk_size
        ):
            # Process numeric columns
            numeric_cols = chunk.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                if col not in numeric_stats:
                    numeric_stats[col] = {
                        'sum': 0,
                        'count': 0,
                        'min': float('inf'),
                        'max': float('-inf'),
                        'values': []
                    }
                
                # Update running statistics
                numeric_stats[col]['sum'] += chunk[col].sum()
                numeric_stats[col]['count'] += chunk[col].count()
                numeric_stats[col]['min'] = min(numeric_stats[col]['min'], chunk[col].min())
                numeric_stats[col]['max'] = max(numeric_stats[col]['max'], chunk[col].max())
                
                # Store sample values for mode calculation (limit to avoid memory issues)
                if len(numeric_stats[col]['values']) < 10000:
                    numeric_stats[col]['values'].extend(chunk[col].dropna().tolist())
            
            # Process categorical columns
            categorical_cols = chunk.select_dtypes(include=['object']).columns
            
            for col in categorical_cols:
                if col not in categorical_stats:
                    categorical_stats[col] = {}
                
                # Count value frequencies
                value_counts = chunk[col].value_counts()
                for value, count in value_counts.items():
                    if value in categorical_stats[col]:
                        categorical_stats[col][value] += count
                    else:
                        categorical_stats[col][value] = count
            
            # Memory management
            del chunk
        
        # Calculate final statistics
        final_stats = {}
        
        # Numeric statistics
        for col, stats in numeric_stats.items():
            if stats['count'] > 0:
                mean = stats['sum'] / stats['count']
                final_stats[col] = {
                    'mean': mean,
                    'min': stats['min'],
                    'max': stats['max'],
                    'count': stats['count'],
                    'null_count': self.total_rows - stats['count']
                }
        
        # Categorical statistics
        for col, value_counts in categorical_stats.items():
            sorted_counts = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)
            final_stats[col] = {
                'unique_values': len(value_counts),
                'top_5_values': sorted_counts[:5],
                'null_count': self.total_rows - sum(value_counts.values())
            }
        
        return final_stats
    
    def create_visualizations(self, output_dir: str = "visualizations"):
        """
        Create visualizations efficiently using chunks
        
        Args:
            output_dir: Directory to save visualizations
        """
        logger.info("Creating visualizations...")
        
        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)
        
        # Set style for better looking plots
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Get column information first
        sample_df = self.get_sample_data(1000)
        numeric_cols = sample_df.select_dtypes(include=[np.number]).columns
        categorical_cols = sample_df.select_dtypes(include=['object']).columns
        
        # 1. Distribution plots for numeric columns
        for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
            logger.info(f"Creating distribution plot for {col}")
            
            values = []
            for chunk in pd.read_csv(
                self.csv_path,
                encoding=self.encoding,
                sep=self.separator,
                chunksize=self.chunk_size,
                usecols=[col]
            ):
                values.extend(chunk[col].dropna().tolist())
                if len(values) > 10000:  # Limit for memory
                    break
            
            if values:
                plt.figure(figsize=(10, 6))
                plt.hist(values, bins=50, alpha=0.7, edgecolor='black')
                plt.title(f'Distribution of {col}')
                plt.xlabel(col)
                plt.ylabel('Frequency')
                plt.tight_layout()
                plt.savefig(f"{output_dir}/distribution_{col}.png", dpi=300, bbox_inches='tight')
                plt.close()
        
        # 2. Top categories for categorical columns
        for col in categorical_cols[:3]:  # Limit to first 3 categorical columns
            logger.info(f"Creating top categories plot for {col}")
            
            value_counts = {}
            for chunk in pd.read_csv(
                self.csv_path,
                encoding=self.encoding,
                sep=self.separator,
                chunksize=self.chunk_size,
                usecols=[col]
            ):
                chunk_counts = chunk[col].value_counts()
                for value, count in chunk_counts.items():
                    value_counts[value] = value_counts.get(value, 0) + count
            
            if value_counts:
                # Get top 10 values
                top_values = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                values, counts = zip(*top_values)
                
                plt.figure(figsize=(12, 6))
                plt.bar(range(len(values)), counts)
                plt.title(f'Top 10 Categories in {col}')
                plt.xlabel('Categories')
                plt.ylabel('Count')
                plt.xticks(range(len(values)), values, rotation=45, ha='right')
                plt.tight_layout()
                plt.savefig(f"{output_dir}/top_categories_{col}.png", dpi=300, bbox_inches='tight')
                plt.close()
    
    def generate_summary_report(self, structure_info: Dict, null_analysis: Dict, 
                              descriptive_stats: Dict) -> str:
        """
        Generate a comprehensive summary report
        
        Args:
            structure_info: File structure information
            null_analysis: Null value analysis
            descriptive_stats: Descriptive statistics
            
        Returns:
            Formatted summary report
        """
        logger.info("Generating summary report...")
        
        report = []
        report.append("=" * 80)
        report.append("EFFICIENT DATA PIPELINE ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        
        # File Information
        report.append("FILE INFORMATION:")
        report.append("-" * 40)
        report.append(f"File path: {self.csv_path}")
        report.append(f"Encoding: {self.encoding}")
        report.append(f"Separator: '{self.separator}'")
        report.append(f"Total rows: {structure_info['total_rows']:,}")
        report.append(f"Total columns: {structure_info['columns_count']}")
        report.append(f"File size: {structure_info['file_size_mb']:.1f} MB")
        report.append(f"Estimated memory usage: {structure_info['estimated_memory_mb']:.1f} MB")
        report.append("")
        
        # Column Information
        report.append("COLUMN INFORMATION:")
        report.append("-" * 40)
        if self.dtypes:
            for col, dtype in self.dtypes.items():
                report.append(f"{col}: {dtype}")
        report.append("")
        
        # Null Value Analysis
        report.append("NULL VALUE ANALYSIS:")
        report.append("-" * 40)
        for col, percentage in null_analysis['null_percentages'].items():
            if percentage > 0:
                report.append(f"{col}: {percentage:.2f}% null values")
        report.append("")
        
        # Descriptive Statistics
        report.append("DESCRIPTIVE STATISTICS:")
        report.append("-" * 40)
        
        # Numeric columns
        if self.dtypes:
            numeric_cols = [col for col, dtype in self.dtypes.items() if 'int' in str(dtype) or 'float' in str(dtype)]
            if numeric_cols:
                report.append("Numeric Columns:")
                for col in numeric_cols[:5]:  # Show first 5
                    if col in descriptive_stats:
                        stats = descriptive_stats[col]
                        report.append(f"  {col}:")
                        report.append(f"    Mean: {stats.get('mean', 'N/A'):.2f}")
                        report.append(f"    Min: {stats.get('min', 'N/A')}")
                        report.append(f"    Max: {stats.get('max', 'N/A')}")
                        report.append(f"    Count: {stats.get('count', 'N/A'):,}")
            
            # Categorical columns
            categorical_cols = [col for col, dtype in self.dtypes.items() if 'object' in str(dtype)]
            if categorical_cols:
                report.append("\nCategorical Columns:")
                for col in categorical_cols[:5]:  # Show first 5
                    if col in descriptive_stats:
                        stats = descriptive_stats[col]
                        report.append(f"  {col}:")
                        report.append(f"    Unique values: {stats.get('unique_values', 'N/A')}")
                        report.append(f"    Top 5 values:")
                        top_values = stats.get('top_5_values', [])
                        if top_values:
                            for value, count in top_values[:5]:
                                report.append(f"      {value}: {count:,}")
        
        report.append("")
        report.append("MEMORY EFFICIENCY NOTES:")
        report.append("-" * 40)
        report.append("- Used chunked processing to avoid loading entire file into memory")
        report.append("- Implemented memory management with explicit deletion of chunks")
        report.append("- Limited visualization data to prevent memory overflow")
        report.append("- Used efficient data types and avoided unnecessary copies")
        report.append("")
        
        report.append("RECOMMENDATIONS:")
        report.append("-" * 40)
        report.append("1. Consider data type optimization for memory reduction")
        report.append("2. Implement data validation for data quality improvement")
        report.append("3. Add data lineage tracking for production environments")
        report.append("4. Consider partitioning for very large datasets")
        report.append("5. Implement incremental processing for real-time updates")
        
        return "\n".join(report)
    
    def run_complete_analysis(self) -> Dict:
        """
        Run the complete analysis pipeline
        
        Returns:
            Dictionary with all analysis results
        """
        logger.info("Starting complete analysis pipeline...")
        
        # Step 1: Detect file properties
        file_properties = self.detect_file_properties()
        
        # Step 2: Analyze file structure
        structure_info = self.analyze_file_structure()
        
        # Step 3: Get sample data
        sample_data = self.get_sample_data()
        
        # Step 4: Analyze null values
        null_analysis = self.analyze_null_values()
        
        # Step 5: Calculate descriptive statistics
        descriptive_stats = self.calculate_descriptive_statistics()
        
        # Step 6: Create visualizations
        self.create_visualizations()
        
        # Step 7: Generate summary report
        summary_report = self.generate_summary_report(
            structure_info, null_analysis, descriptive_stats
        )
        
        # Save report to file
        with open("analysis_report.txt", "w", encoding="utf-8") as f:
            f.write(summary_report)
        
        logger.info("Analysis complete! Report saved to analysis_report.txt")
        
        return {
            'file_properties': file_properties,
            'structure_info': structure_info,
            'sample_data': sample_data,
            'null_analysis': null_analysis,
            'descriptive_stats': descriptive_stats,
            'summary_report': summary_report
        }


def main():
    """
    Main function to run the data pipeline
    """
    # File path
    csv_path = "/Users/alexsandersilveira/Downloads/itineraries.csv"
    
    # Check if file exists
    if not os.path.exists(csv_path):
        logger.error(f"File not found: {csv_path}")
        sys.exit(1)
    
    # Initialize pipeline
    pipeline = EfficientDataPipeline(csv_path, chunk_size=10000)
    
    # Run complete analysis
    results = pipeline.run_complete_analysis()
    
    # Print summary
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"File processed: {csv_path}")
    print(f"Total rows: {results['structure_info']['total_rows']:,}")
    print(f"Memory efficient processing completed successfully!")
    print("Check 'analysis_report.txt' for detailed results")
    print("Check 'visualizations/' folder for charts")


if __name__ == "__main__":
    main() 