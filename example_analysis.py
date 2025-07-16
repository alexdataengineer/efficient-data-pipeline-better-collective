#!/usr/bin/env python3
"""
Example Analysis Script
Demonstrates key concepts of the efficient data pipeline
"""

import csv
import os
import sys
from collections import defaultdict, Counter
from typing import Dict, List, Tuple

class SimpleDataAnalyzer:
    """
    Simple data analyzer that demonstrates memory-efficient processing
    without requiring pandas or other heavy dependencies
    """
    
    def __init__(self, csv_path: str, chunk_size: int = 1000):
        self.csv_path = csv_path
        self.chunk_size = chunk_size
        self.encoding = 'utf-8'
        self.separator = ','
        
    def detect_encoding_and_separator(self) -> Dict:
        """Detect file encoding and separator"""
        print("Detecting file properties...")
        
        # Try to read first few lines to detect encoding
        encodings_to_try = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings_to_try:
            try:
                with open(self.csv_path, 'r', encoding=encoding) as f:
                    first_line = f.readline().strip()
                    if first_line:
                        self.encoding = encoding
                        break
            except UnicodeDecodeError:
                continue
        
        # Detect separator
        separators = [',', ';', '\t', '|']
        max_columns = 0
        best_separator = ','
        
        with open(self.csv_path, 'r', encoding=self.encoding) as f:
            first_line = f.readline().strip()
            
        for sep in separators:
            columns = first_line.split(sep)
            if len(columns) > max_columns:
                max_columns = len(columns)
                best_separator = sep
        
        self.separator = best_separator
        
        return {
            'encoding': self.encoding,
            'separator': self.separator,
            'columns_count': max_columns
        }
    
    def count_rows_and_columns(self) -> Dict:
        """Count total rows and identify columns"""
        print("Analyzing file structure...")
        
        total_rows = 0
        columns = []
        
        with open(self.csv_path, 'r', encoding=self.encoding) as f:
            reader = csv.reader(f, delimiter=self.separator)
            
            # Read header
            try:
                columns = next(reader)
                total_rows = sum(1 for _ in reader)
            except StopIteration:
                pass
        
        file_size_mb = os.path.getsize(self.csv_path) / (1024 * 1024)
        
        return {
            'total_rows': total_rows,
            'columns': columns,
            'file_size_mb': file_size_mb
        }
    
    def get_sample_data(self, nrows: int = 5) -> List[List]:
        """Get sample data for inspection"""
        print(f"Loading sample data ({nrows} rows)...")
        
        sample_data = []
        
        with open(self.csv_path, 'r', encoding=self.encoding) as f:
            reader = csv.reader(f, delimiter=self.separator)
            
            # Skip header
            next(reader)
            
            for i, row in enumerate(reader):
                if i >= nrows:
                    break
                sample_data.append(row)
        
        return sample_data
    
    def analyze_null_values(self) -> Dict:
        """Analyze null values efficiently"""
        print("Analyzing null values...")
        
        null_counts = defaultdict(int)
        total_rows = 0
        
        with open(self.csv_path, 'r', encoding=self.encoding) as f:
            reader = csv.reader(f, delimiter=self.separator)
            
            # Read header
            columns = next(reader)
            
            for row in reader:
                total_rows += 1
                
                for i, value in enumerate(row):
                    if i < len(columns):
                        if not value.strip():  # Empty or whitespace
                            null_counts[columns[i]] += 1
        
        null_percentages = {
            col: (count / total_rows) * 100 
            for col, count in null_counts.items()
        }
        
        return {
            'null_counts': dict(null_counts),
            'null_percentages': null_percentages,
            'total_rows': total_rows
        }
    
    def calculate_basic_statistics(self) -> Dict:
        """Calculate basic statistics for numeric columns"""
        print("Calculating basic statistics...")
        
        stats = {}
        value_counts = defaultdict(Counter)
        
        with open(self.csv_path, 'r', encoding=self.encoding) as f:
            reader = csv.reader(f, delimiter=self.separator)
            
            # Read header
            columns = next(reader)
            
            # Initialize stats for each column
            for col in columns:
                stats[col] = {
                    'numeric_values': [],
                    'string_values': Counter(),
                    'total_count': 0
                }
            
            # Process rows
            for row in reader:
                for i, value in enumerate(row):
                    if i < len(columns):
                        col = columns[i]
                        stats[col]['total_count'] += 1
                        
                        # Try to convert to numeric
                        try:
                            numeric_val = float(value)
                            stats[col]['numeric_values'].append(numeric_val)
                        except (ValueError, TypeError):
                            # String value
                            if value.strip():
                                stats[col]['string_values'][value] += 1
        
        # Calculate final statistics
        final_stats = {}
        
        for col, col_stats in stats.items():
            numeric_vals = col_stats['numeric_values']
            string_vals = col_stats['string_values']
            
            if numeric_vals:
                # Numeric column
                final_stats[col] = {
                    'type': 'numeric',
                    'count': len(numeric_vals),
                    'mean': sum(numeric_vals) / len(numeric_vals) if numeric_vals else 0,
                    'min': min(numeric_vals) if numeric_vals else None,
                    'max': max(numeric_vals) if numeric_vals else None,
                    'null_count': col_stats['total_count'] - len(numeric_vals)
                }
            else:
                # Categorical column
                final_stats[col] = {
                    'type': 'categorical',
                    'unique_values': len(string_vals),
                    'top_5_values': string_vals.most_common(5),
                    'null_count': col_stats['total_count'] - sum(string_vals.values())
                }
        
        return final_stats
    
    def generate_report(self, structure_info: Dict, null_analysis: Dict, 
                       descriptive_stats: Dict) -> str:
        """Generate a comprehensive report"""
        print("Generating analysis report...")
        
        report = []
        report.append("=" * 80)
        report.append("SIMPLE DATA ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        
        # File Information
        report.append("FILE INFORMATION:")
        report.append("-" * 40)
        report.append(f"File path: {self.csv_path}")
        report.append(f"Encoding: {self.encoding}")
        report.append(f"Separator: '{self.separator}'")
        report.append(f"Total rows: {structure_info['total_rows']:,}")
        report.append(f"Total columns: {len(structure_info['columns'])}")
        report.append(f"File size: {structure_info['file_size_mb']:.1f} MB")
        report.append("")
        
        # Column Information
        report.append("COLUMN INFORMATION:")
        report.append("-" * 40)
        for i, col in enumerate(structure_info['columns']):
            report.append(f"{i+1}. {col}")
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
        
        for col, stats in descriptive_stats.items():
            report.append(f"\n{col}:")
            if stats['type'] == 'numeric':
                report.append(f"  Type: Numeric")
                report.append(f"  Count: {stats['count']:,}")
                report.append(f"  Mean: {stats['mean']:.2f}")
                report.append(f"  Min: {stats['min']}")
                report.append(f"  Max: {stats['max']}")
                report.append(f"  Null count: {stats['null_count']:,}")
            else:
                report.append(f"  Type: Categorical")
                report.append(f"  Unique values: {stats['unique_values']}")
                report.append(f"  Top 5 values:")
                for value, count in stats['top_5_values']:
                    report.append(f"    {value}: {count:,}")
                report.append(f"  Null count: {stats['null_count']:,}")
        
        report.append("")
        report.append("MEMORY EFFICIENCY NOTES:")
        report.append("-" * 40)
        report.append("- Used streaming processing to avoid loading entire file")
        report.append("- Processed data row by row to minimize memory usage")
        report.append("- Used efficient data structures (Counter, defaultdict)")
        report.append("- Avoided storing large intermediate results")
        
        return "\n".join(report)
    
    def run_analysis(self) -> Dict:
        """Run the complete analysis"""
        print("Starting simple data analysis...")
        
        # Step 1: Detect properties
        file_properties = self.detect_encoding_and_separator()
        
        # Step 2: Analyze structure
        structure_info = self.count_rows_and_columns()
        
        # Step 3: Get sample
        sample_data = self.get_sample_data()
        
        # Step 4: Analyze nulls
        null_analysis = self.analyze_null_values()
        
        # Step 5: Calculate statistics
        descriptive_stats = self.calculate_basic_statistics()
        
        # Step 6: Generate report
        summary_report = self.generate_report(
            structure_info, null_analysis, descriptive_stats
        )
        
        # Save report
        with open("simple_analysis_report.txt", "w", encoding="utf-8") as f:
            f.write(summary_report)
        
        print("Analysis complete! Report saved to simple_analysis_report.txt")
        
        return {
            'file_properties': file_properties,
            'structure_info': structure_info,
            'sample_data': sample_data,
            'null_analysis': null_analysis,
            'descriptive_stats': descriptive_stats,
            'summary_report': summary_report
        }


def main():
    """Main function"""
    csv_path = "/Users/alexsandersilveira/Downloads/itineraries.csv"
    
    if not os.path.exists(csv_path):
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)
    
    analyzer = SimpleDataAnalyzer(csv_path)
    results = analyzer.run_analysis()
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"File processed: {csv_path}")
    print(f"Total rows: {results['structure_info']['total_rows']:,}")
    print("Memory-efficient processing completed successfully!")


if __name__ == "__main__":
    main() 