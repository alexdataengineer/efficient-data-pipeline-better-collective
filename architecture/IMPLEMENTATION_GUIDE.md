# ETL Implementation Guide

## Quick Start

### 1. Extraction Setup

#### Airflow DAG Example
```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

def extract_api_data():
    import requests
    response = requests.get('https://api.example.com/data')
    return response.json()

def extract_database_data():
    import psycopg2
    conn = psycopg2.connect("host=localhost dbname=my_db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

dag = DAG('etl_pipeline', start_date=datetime(2024, 1, 1))

extract_api = PythonOperator(
    task_id='extract_api',
    python_callable=extract_api_data,
    dag=dag
)

extract_db = PythonOperator(
    task_id='extract_db',
    python_callable=extract_database_data,
    dag=dag
)
```

#### Kafka Connect Configuration
```json
{
  "name": "postgres-source",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
    "connection.url": "jdbc:postgresql://localhost:5432/mydb",
    "topic.prefix": "postgres-",
    "mode": "incrementing",
    "incrementing.column.name": "id"
  }
}
```

### 2. Transformation Setup

#### Spark Transformation
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder.appName("ETL").getOrCreate()

# Read data
df = spark.read.json("data/raw/")

# Transform
transformed_df = df.select(
    col("id"),
    upper(col("name")).alias("name_upper"),
    col("amount") * 1.1
).filter(col("amount") > 100)

# Write
transformed_df.write.mode("overwrite").parquet("data/transformed/")
```

#### dbt Model
```sql
-- models/transformed_users.sql
SELECT 
    user_id,
    UPPER(first_name) as first_name_upper,
    UPPER(last_name) as last_name_upper,
    email,
    created_at,
    CASE 
        WHEN age >= 18 THEN 'adult'
        ELSE 'minor'
    END as age_group
FROM {{ ref('raw_users') }}
WHERE email IS NOT NULL
```

### 3. Loading Setup

#### Airflow Loading Task
```python
def load_to_warehouse():
    import snowflake.connector
    
    conn = snowflake.connector.connect(
        user='username',
        password='password',
        account='account',
        warehouse='warehouse',
        database='database',
        schema='schema'
    )
    
    cursor = conn.cursor()
    cursor.execute("""
        COPY INTO users 
        FROM @my_stage/users.csv
        FILE_FORMAT = (TYPE = 'CSV')
    """)
    
    conn.close()

load_task = PythonOperator(
    task_id='load_to_warehouse',
    python_callable=load_to_warehouse,
    dag=dag
)
```

## Technology Choices Explained

### Why Apache Airflow?
- **Scheduling**: Complex dependencies between tasks
- **Monitoring**: Built-in UI shows pipeline status
- **Retry Logic**: Automatic failure recovery
- **Scalability**: Can handle thousands of tasks

### Why Apache Spark?
- **Performance**: 10-100x faster than traditional Hadoop
- **Memory**: In-memory processing reduces I/O
- **Languages**: Python, Java, Scala, R support
- **Ecosystem**: MLlib, GraphX, Spark SQL

### Why dbt?
- **SQL**: Data analysts can write transformations
- **Testing**: Built-in data quality tests
- **Documentation**: Auto-generates data lineage
- **Version Control**: Git-based development workflow

### Why Snowflake?
- **Scalability**: Auto-scaling compute and storage
- **Performance**: Columnar storage with caching
- **Cost**: Pay-per-use pricing model
- **Multi-cloud**: Works on AWS, Azure, GCP

## Alternative Stacks

### Option 1: Modern Data Stack
```
Fivetran → dbt → Snowflake → Looker
```
**Pros**: Easy to use, managed services
**Cons**: Vendor lock-in, expensive

### Option 2: Open Source Stack
```
Airflow → Spark → PostgreSQL → Grafana
```
**Pros**: Free, full control
**Cons**: More maintenance, steeper learning curve

### Option 3: Cloud Native
```
AWS Glue → AWS EMR → Amazon Redshift → QuickSight
```
**Pros**: Integrated, managed
**Cons**: AWS lock-in, expensive

## Key Considerations

### Scalability
- **Horizontal**: Add more nodes
- **Vertical**: Increase node capacity
- **Auto-scaling**: Cloud-based solutions

### Reliability
- **Fault Tolerance**: Handle node failures
- **Data Consistency**: ACID properties
- **Backup/Recovery**: Disaster recovery

### Cost
- **Infrastructure**: Servers, storage, network
- **Licensing**: Software licenses
- **Maintenance**: Operational costs

## Best Practices

### 1. Data Quality
```python
# Data validation
def validate_data(df):
    assert df.count() > 0, "No data found"
    assert df.filter(col("id").isNull()).count() == 0, "Null IDs found"
    return df
```

### 2. Error Handling
```python
# Retry logic
@retry(stop_max_attempt_number=3)
def extract_with_retry():
    return extract_data()
```

### 3. Monitoring
```python
# Metrics collection
def log_metrics(records_processed, processing_time):
    logger.info(f"Processed {records_processed} records in {processing_time}s")
```

### 4. Testing
```sql
-- dbt test
SELECT COUNT(*) as null_count
FROM {{ ref('users') }}
WHERE email IS NULL
```

## Deployment

### Docker Compose
```yaml
version: '3.8'
services:
  airflow:
    image: apache/airflow:2.7.1
    ports:
      - "8080:8080"
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
  
  spark:
    image: bitnami/spark:3.5
    ports:
      - "4040:4040"
  
  kafka:
    image: confluentinc/cp-kafka:7.4.0
    ports:
      - "9092:9092"
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: airflow
spec:
  replicas: 3
  selector:
    matchLabels:
      app: airflow
  template:
    metadata:
      labels:
        app: airflow
    spec:
      containers:
      - name: airflow
        image: apache/airflow:2.7.1
```

## Performance Optimization

### 1. Partitioning
```python
# Spark partitioning
df.write.partitionBy("date", "country").parquet("data/")
```

### 2. Caching
```python
# Spark caching
df.cache()
df.count()  # Materialize cache
```

### 3. Compression
```python
# Parquet compression
df.write.option("compression", "snappy").parquet("data/")
```

## Monitoring and Alerting

### 1. Airflow Alerts
```python
from airflow.operators.email_operator import EmailOperator

email_alert = EmailOperator(
    task_id='send_alert',
    to='admin@company.com',
    subject='ETL Pipeline Failed',
    html_content='<p>Pipeline failed at {{ ds }}</p>',
    dag=dag
)
```

### 2. Custom Metrics
```python
import time
from datetime import datetime

def track_performance(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # Send to monitoring system
        send_metric('processing_time', end_time - start_time)
        return result
    return wrapper
```

This implementation guide provides practical examples and best practices for building a robust ETL architecture. 