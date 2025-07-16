#!/usr/bin/env python3
"""
Quick Demo - Efficient Data Pipeline
Processes only a sample of the large CSV file for demonstration
"""

import csv
import os
import sys
from collections import defaultdict, Counter
from typing import Dict, List

class QuickDataAnalyzer:
    """Quick analyzer that processes only a sample of the large file"""
    
    def __init__(self, csv_path: str, max_rows: int = 10000):
        self.csv_path = csv_path
        self.max_rows = max_rows
        self.encoding = 'utf-8'
        self.separator = ','
        
    def analyze_sample(self) -> Dict:
        """Analyze only a sample of the large file"""
        print(f"Analyzing sample of {self.max_rows:,} rows from large file...")
        
        # Detect encoding and separator
        self._detect_properties()
        
        # Analyze structure
        structure_info = self._analyze_structure()
        
        # Get sample data
        sample_data = self._get_sample()
        
        # Analyze nulls
        null_analysis = self._analyze_nulls()
        
        # Calculate statistics
        stats = self._calculate_stats()
        
        # Generate report
        report = self._generate_report(structure_info, null_analysis, stats)
        
        # Save report
        with open("quick_demo_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        
        print("✓ Quick analysis complete! Report saved to quick_demo_report.txt")
        
        return {
            'structure_info': structure_info,
            'sample_data': sample_data,
            'null_analysis': null_analysis,
            'stats': stats,
            'report': report
        }
    
    def _detect_properties(self):
        """Detect file properties quickly"""
        print("Detecting file properties...")
        
        # Try common encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                with open(self.csv_path, 'r', encoding=encoding) as f:
                    first_line = f.readline().strip()
                    if first_line:
                        self.encoding = encoding
                        break
            except UnicodeDecodeError:
                continue
        
        # Detect separator
        with open(self.csv_path, 'r', encoding=self.encoding) as f:
            first_line = f.readline().strip()
            
        separators = [',', ';', '\t', '|']
        max_columns = 0
        best_separator = ','
        
        for sep in separators:
            columns = first_line.split(sep)
            if len(columns) > max_columns:
                max_columns = len(columns)
                best_separator = sep
        
        self.separator = best_separator
        print(f"✓ Detected: encoding={self.encoding}, separator='{self.separator}'")
    
    def _analyze_structure(self) -> Dict:
        """Analyze file structure from sample"""
        print("Analyzing file structure...")
        
        total_rows = 0
        columns = []
        
        # Count total rows efficiently
        with open(self.csv_path, 'r', encoding=self.encoding) as f:
            total_rows = sum(1 for _ in f) - 1  # Subtract header
        
        # Get columns from header
        with open(self.csv_path, 'r', encoding=self.encoding) as f:
            reader = csv.reader(f, delimiter=self.separator)
            columns = next(reader)
        
        file_size_mb = os.path.getsize(self.csv_path) / (1024 * 1024)
        
        print(f"✓ File: {total_rows:,} rows, {len(columns)} columns, {file_size_mb:.1f}MB")
        
        return {
            'total_rows': total_rows,
            'columns': columns,
            'file_size_mb': file_size_mb
        }
    
    def _get_sample(self) -> List[List]:
        """Get sample data"""
        print(f"Loading sample data ({self.max_rows} rows)...")
        
        sample_data = []
        
        with open(self.csv_path, 'r', encoding=self.encoding) as f:
            reader = csv.reader(f, delimiter=self.separator)
            
            # Skip header
            next(reader)
            
            for i, row in enumerate(reader):
                if i >= self.max_rows:
                    break
                sample_data.append(row)
        
        print(f"✓ Loaded {len(sample_data)} sample rows")
        return sample_data
    
    def _analyze_nulls(self) -> Dict:
        """Analyze null values in sample"""
        print("Analyzing null values...")
        
        null_counts = defaultdict(int)
        total_rows = 0
        
        with open(self.csv_path, 'r', encoding=self.encoding) as f:
            reader = csv.reader(f, delimiter=self.separator)
            
            # Read header
            columns = next(reader)
            
            for i, row in enumerate(reader):
                if i >= self.max_rows:
                    break
                    
                total_rows += 1
                
                for j, value in enumerate(row):
                    if j < len(columns):
                        if not value.strip():
                            null_counts[columns[j]] += 1
        
        null_percentages = {
            col: (count / total_rows) * 100 
            for col, count in null_counts.items()
        }
        
        print(f"✓ Analyzed {total_rows} rows for null values")
        
        return {
            'null_counts': dict(null_counts),
            'null_percentages': null_percentages,
            'total_rows': total_rows
        }
    
    def _calculate_stats(self) -> Dict:
        """Calculate basic statistics from sample"""
        print("Calculating statistics...")
        
        stats = {}
        
        with open(self.csv_path, 'r', encoding=self.encoding) as f:
            reader = csv.reader(f, delimiter=self.separator)
            
            # Read header
            columns = next(reader)
            
            # Initialize stats
            for col in columns:
                stats[col] = {
                    'numeric_values': [],
                    'string_values': Counter(),
                    'total_count': 0
                }
            
            # Process sample rows
            for i, row in enumerate(reader):
                if i >= self.max_rows:
                    break
                    
                for j, value in enumerate(row):
                    if j < len(columns):
                        col = columns[j]
                        stats[col]['total_count'] += 1
                        
                        # Try numeric conversion
                        try:
                            numeric_val = float(value)
                            stats[col]['numeric_values'].append(numeric_val)
                        except (ValueError, TypeError):
                            if value.strip():
                                stats[col]['string_values'][value] += 1
        
        # Calculate final stats
        final_stats = {}
        
        for col, col_stats in stats.items():
            numeric_vals = col_stats['numeric_values']
            string_vals = col_stats['string_values']
            
            if numeric_vals:
                final_stats[col] = {
                    'type': 'numeric',
                    'count': len(numeric_vals),
                    'mean': sum(numeric_vals) / len(numeric_vals) if numeric_vals else 0,
                    'min': min(numeric_vals) if numeric_vals else None,
                    'max': max(numeric_vals) if numeric_vals else None,
                    'null_count': col_stats['total_count'] - len(numeric_vals)
                }
            else:
                final_stats[col] = {
                    'type': 'categorical',
                    'unique_values': len(string_vals),
                    'top_5_values': string_vals.most_common(5),
                    'null_count': col_stats['total_count'] - sum(string_vals.values())
                }
        
        print(f"✓ Calculated statistics for {len(final_stats)} columns")
        return final_stats
    
    def _generate_report(self, structure_info: Dict, null_analysis: Dict, stats: Dict) -> str:
        """Generate comprehensive report"""
        print("Generating report...")
        
        report = []
        report.append("=" * 80)
        report.append("QUICK DEMO - EFFICIENT DATA PIPELINE ANALYSIS")
        report.append("=" * 80)
        report.append("")
        
        # File Information
        report.append("FILE INFORMATION:")
        report.append("-" * 40)
        report.append(f"File path: {self.csv_path}")
        report.append(f"Encoding: {self.encoding}")
        report.append(f"Separator: '{self.separator}'")
        report.append(f"Total rows: {structure_info['total_rows']:,}")
        report.append(f"Sample size: {self.max_rows:,} rows")
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
        report.append("NULL VALUE ANALYSIS (Sample):")
        report.append("-" * 40)
        for col, percentage in null_analysis['null_percentages'].items():
            if percentage > 0:
                report.append(f"{col}: {percentage:.2f}% null values")
        report.append("")
        
        # Statistics
        report.append("DESCRIPTIVE STATISTICS (Sample):")
        report.append("-" * 40)
        
        for col, col_stats in stats.items():
            report.append(f"\n{col}:")
            if col_stats['type'] == 'numeric':
                report.append(f"  Type: Numeric")
                report.append(f"  Count: {col_stats['count']:,}")
                report.append(f"  Mean: {col_stats['mean']:.2f}")
                report.append(f"  Min: {col_stats['min']}")
                report.append(f"  Max: {col_stats['max']}")
                report.append(f"  Null count: {col_stats['null_count']:,}")
            else:
                report.append(f"  Type: Categorical")
                report.append(f"  Unique values: {col_stats['unique_values']}")
                report.append(f"  Top 5 values:")
                for value, count in col_stats['top_5_values']:
                    report.append(f"    {value}: {count:,}")
                report.append(f"  Null count: {col_stats['null_count']:,}")
        
        report.append("")
        report.append("MEMORY EFFICIENCY FEATURES:")
        report.append("-" * 40)
        report.append("✓ Processed only sample of large file")
        report.append("✓ Used streaming processing")
        report.append("✓ Efficient data structures")
        report.append("✓ No full file loading")
        report.append("")
        
        report.append("PRODUCTION RECOMMENDATIONS:")
        report.append("-" * 40)
        report.append("1. Use chunked processing for full file")
        report.append("2. Implement data validation")
        report.append("3. Add error handling and retries")
        report.append("4. Monitor memory usage")
        report.append("5. Consider distributed processing for very large files")
        
        return "\n".join(report)


def main():
    """Main function"""
    csv_path = "/Users/alexsandersilveira/Downloads/itineraries.csv"
    
    if not os.path.exists(csv_path):
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)
    
    # Quick analysis with limited sample
    analyzer = QuickDataAnalyzer(csv_path, max_rows=10000)
    results = analyzer.analyze_sample()
    
    print("\n" + "="*80)
    print("QUICK DEMO COMPLETE")
    print("="*80)
    print(f"✓ File processed: {csv_path}")
    print(f"✓ Sample analyzed: {results['structure_info']['total_rows']:,} total rows")
    print(f"✓ Report generated: quick_demo_report.txt")
    print("✓ Memory-efficient processing demonstrated!")


if __name__ == "__main__":
    main() 