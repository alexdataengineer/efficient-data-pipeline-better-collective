# Efficient Data Pipeline - Better Collective Data Engineer Position

## Overview

This project implements a memory-efficient data pipeline for processing large CSV files with a 4GB memory constraint. The solution is designed for containerized environments like ECS with limited resources.

## Features

- **Memory-efficient processing**: Uses chunked reading to avoid loading entire files into memory
- **Automatic encoding detection**: Detects file encoding and separator automatically
- **Comprehensive analysis**: Provides descriptive statistics, null value analysis, and data quality insights
- **Visualization support**: Creates charts and graphs for data exploration
- **Professional documentation**: Clear code comments and comprehensive reporting

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure the CSV file is available at the specified path:
```python
csv_path = "/Users/alexsandersilveira/Downloads/itineraries.csv"
```

## Usage

Run the complete analysis pipeline:

```bash
python data_pipeline.py
```

## Output

The pipeline generates:
- `analysis_report.txt`: Comprehensive analysis report
- `visualizations/`: Directory containing charts and graphs
- Console output with progress logging

## Memory Efficiency Features

1. **Chunked Processing**: Processes data in configurable chunks (default: 10,000 rows)
2. **Memory Management**: Explicitly deletes processed chunks to free memory
3. **Efficient Data Types**: Uses appropriate data types to minimize memory usage
4. **Limited Sampling**: Limits visualization data to prevent memory overflow
5. **Streaming Analysis**: Performs statistics calculations without storing entire dataset

## Code Structure

- `EfficientDataPipeline`: Main class handling all data processing
- `detect_file_properties()`: Automatic encoding and separator detection
- `analyze_file_structure()`: File size and structure analysis
- `analyze_null_values()`: Memory-efficient null value analysis
- `calculate_descriptive_statistics()`: Streaming statistics calculation
- `create_visualizations()`: Memory-conscious chart generation
- `generate_summary_report()`: Comprehensive reporting

## Requirements

- Python 3.8+
- pandas >= 1.5.0
- dask >= 2023.1.0
- pyarrow >= 10.0.0
- matplotlib >= 3.6.0
- seaborn >= 0.12.0
- numpy >= 1.24.0
- chardet >= 5.0.0

## Design Decisions

1. **Chunked Processing**: Prevents memory overflow for large files
2. **Automatic Detection**: Reduces manual configuration requirements
3. **Comprehensive Logging**: Provides visibility into processing progress
4. **Error Handling**: Graceful handling of file access and processing errors
5. **Modular Design**: Easy to extend and maintain

## Performance Considerations

- Estimated memory usage: ~2x file size
- Processing speed: Optimized for memory over speed
- Scalability: Can handle files larger than available RAM
- Resource monitoring: Built-in memory usage tracking

## Production Recommendations

1. **Data Validation**: Add schema validation for data quality
2. **Error Recovery**: Implement retry logic for failed operations
3. **Monitoring**: Add metrics collection for performance tracking
4. **Caching**: Implement result caching for repeated analyses
5. **Parallelization**: Consider Dask for distributed processing