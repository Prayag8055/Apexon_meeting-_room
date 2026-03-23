import json
import boto3
import decimal
import logging
from datetime import datetime, timezone, timedelta
from boto3.dynamodb.conditions import Key, Attr
import base64
from typing import NamedTuple

# ---------- Logging Setup ----------
LOGGER = logging.getLogger()
if not LOGGER.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER.setLevel(logging.INFO)

AWS_REGION = "us-east-1"

# Create SSM client once at module level for performance
_ssm_client = boto3.client("ssm", region_name=AWS_REGION)

def _ssm():
    return _ssm_client

def get_parameter_value(parameter_name: str, decrypt: bool = True) -> str | None:
    if not parameter_name:
        return None
    try:
        resp = _ssm().get_parameter(Name=parameter_name, WithDecryption=decrypt)
        return resp["Parameter"]["Value"]
    except Exception as e:
        LOGGER.warning(f"SSM get_parameter failed for {parameter_name}: {e}")
        return None

def log_event(event, note="event"):
    try:
        snippet = json.dumps(event)[:2000]
        LOGGER.debug(f"{note}: {snippet}")
    except Exception as e:
        LOGGER.debug(f"{note}: <unserializable> - {e}")

# Initialize DynamoDB resources
dynamodb = boto3.resource("dynamodb")
WORKFLOW_TABLE_NAME = get_parameter_value("/lpc/aws-ls/dynamo_db/tables/workflow_table")
WORKFLOW_RUNS_TABLE_NAME = get_parameter_value("/lpc/aws-ls/dynamo_db/tables/workflow_runs_table")

if not WORKFLOW_TABLE_NAME:
    raise ValueError("WORKFLOW_TABLE_NAME parameter is not set in SSM.")
if not WORKFLOW_RUNS_TABLE_NAME:
    raise ValueError("WORKFLOW_RUNS_TABLE_NAME parameter is not set in SSM.")

workflows = dynamodb.Table(WORKFLOW_TABLE_NAME)
workflow_runs = dynamodb.Table(WORKFLOW_RUNS_TABLE_NAME)

# Initialize Athena resources
athena_client = boto3.client('athena', region_name=AWS_REGION)
ATHENA_CATALOG = "s3tablescatalog"
ATHENA_DATABASE = "lab-process-transformed-events"
ATHENA_OUTPUT_S3 = get_parameter_value("ATHENA_OUTPUT_S3")

def json_default(obj):
    if isinstance(obj, decimal.Decimal):
        return int(obj) if obj == int(obj) else float(obj)
    return str(obj)

def response(code, body):
    LOGGER.info(f"Response status={code}")
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "GET,POST,DELETE,OPTIONS"
        },
        "body": json.dumps(body, default=json_default)
    }

# -------- HTTP API v1 Parsing ---------

class ParsedEvent(NamedTuple):
    method: str
    path: str
    qs: dict
    body: dict

def normalize_path(raw_path: str, event: dict) -> str:
    """Remove stage prefix (/v1, /prod, /$default) if present and trim trailing slash."""
    if not raw_path:
        return "/"
    stage = (
        event.get("requestContext", {}).get("stage")
        or event.get("requestContext", {}).get("http", {}).get("stage")
    )
    if stage and raw_path.startswith(f"/{stage}/"):
        raw_path = raw_path[len(stage) + 2:]
        if not raw_path.startswith("/"):
            raw_path = "/" + raw_path
    if stage and raw_path == f"/{stage}":
        raw_path = "/"
    if len(raw_path) > 1 and raw_path.endswith("/"):
        raw_path = raw_path[:-1]
    return raw_path

def parse_event(event) -> ParsedEvent:
    """Parse API Gateway event with stage handling"""
    method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
    raw_path = event.get('path') or event.get('rawPath') or '/'
    path = normalize_path(raw_path, event)
    qs = event.get('queryStringParameters') or {}
    
    body_raw = event.get('body')
    if event.get('isBase64Encoded'):
        try:
            body_raw = base64.b64decode(body_raw or '').decode('utf-8')
        except Exception as e:
            LOGGER.warning(f"Failed to decode base64 body: {e}")
    
    try:
        body = json.loads(body_raw) if body_raw else {}
    except json.JSONDecodeError as e:
        LOGGER.warning(f"Failed to parse JSON body: {e}")
        body = {}
    
    LOGGER.info(f"Parsed method={method} path={path} (raw={raw_path})")
    return ParsedEvent(method, path, qs, body)

def lambda_handler(event, context):
    try:
        log_event(event, "incoming")
        parsed = parse_event(event)
        
        LOGGER.info(f"Processing {parsed.method} {parsed.path}")
        
        if parsed.method == 'OPTIONS':
            return response(200, {'message': 'OK'})
        
        if parsed.method == 'GET' and parsed.path == '/workflows':
            return handle_get_workflows(parsed.qs)
        
        if parsed.method == 'GET' and parsed.path.startswith('/workflows/'):
            workflow_id = parsed.path.split('/')[-1]
            return handle_get_workflow_by_id(workflow_id)
        
        if parsed.method == 'GET' and parsed.path == '/runs':
            return handle_get_runs(parsed.qs)
        
        if parsed.method == 'GET' and parsed.path.startswith('/runs/'):
            run_id = parsed.path.split('/')[-1]
            return handle_get_run_by_id(run_id)
        
        if parsed.method == 'GET' and parsed.path == '/dashboard':
            return handle_get_dashboard()
        
        if parsed.method == 'GET' and parsed.path == '/alerts':
            return handle_get_alerts(parsed.qs)
        
        return response(404, {'error': f'Route not found: {parsed.path}'})
        
    except Exception as e:
        LOGGER.exception("Unhandled error in lambda_handler")
        return response(500, {'error': 'Internal server error'})

# -------- Enhanced Workflow Operations ---------

def get_all_runs():
    """Get all workflow runs from DynamoDB table"""
    try:
        response = workflow_runs.scan()
        items = response.get('Items', [])
        
        while 'LastEvaluatedKey' in response:
            response = workflow_runs.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        
        LOGGER.info(f"Retrieved {len(items)} workflow runs")
        return items
    except Exception as e:
        LOGGER.error(f"Error retrieving workflow runs: {str(e)}")
        raise

def get_all_workflows():
    """Get all workflows from DynamoDB table - complete data"""
    try:
        response = workflows.scan()
        items = response.get('Items', [])
        
        while 'LastEvaluatedKey' in response:
            response = workflows.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        
        LOGGER.info(f"Retrieved {len(items)} workflows")
        return items
    except Exception as e:
        LOGGER.error(f"Error retrieving workflows: {str(e)}")
        raise

def get_workflow_by_id(workflow_id):
    """Get specific workflow by ID"""
    try:
        response = workflows.get_item(Key={'workflow_id': workflow_id})
        return response.get('Item')
    except Exception as e:
        LOGGER.error(f"Error retrieving workflow {workflow_id}: {str(e)}")
        raise

def get_run_by_id(run_id):
    """Get specific run by ID with workflow information"""
    try:
        run_response = workflow_runs.get_item(Key={'run_id': run_id})
        run = run_response.get('Item')
        
        if run:
            workflow_id = run.get('workflow_id')
            workflow = get_workflow_by_id(workflow_id) if workflow_id else {}
            
            if workflow:
                steps = workflow.get('steps', [])
                step_count = len(steps) if isinstance(steps, list) else workflow.get('step_count', 0)
            
            return {
                **run,
                'workflow_info': {
                    'description': workflow.get('description', ''),
                    'created_at': workflow.get('created_at', ''),
                    'step_count': step_count,
                    'steps': steps
                } if workflow else {}
            }
        return None
    except Exception as e:
        LOGGER.error(f"Error retrieving run {run_id}: {str(e)}")
        raise

def get_dashboard_data():
    """Get combined KPI and timeline data - optimized single pass"""
    try:
        runs = get_all_runs()
        
        workflow_response = workflows.scan(
            ProjectionExpression='workflow_id, #status, created_at, updated_at',
            ExpressionAttributeNames={'#status': 'status'}
        )
        workflow_items = workflow_response.get('Items', [])
        
        while 'LastEvaluatedKey' in workflow_response:
            workflow_response = workflows.scan(
                ExclusiveStartKey=workflow_response['LastEvaluatedKey'],
                ProjectionExpression='workflow_id, #status, created_at, updated_at',
                ExpressionAttributeNames={'#status': 'status'}
            )
            workflow_items.extend(workflow_response.get('Items', []))
        
        run_status_counts = {'active': 0, 'completed': 0, 'failed': 0, 'total': len(runs)}
        now = datetime.now(timezone.utc)
        hours_48_ago = now - timedelta(hours=48)
        completed_last_48h = 0
        
        intervals = [{'period': f"{i*6}-{(i+1)*6}h", 'completed': 0, 'running': 0, 'failed': 0} for i in range(8)]
        
        for run in runs:
            status = run.get('status', '').upper()
            start_time_str = run.get('start_time', '')
            end_time_str = run.get('end_time', '')
            
            if status in ['STARTED', 'IN_PROGRESS']:
                run_status_counts['active'] += 1
            elif status == 'COMPLETED':
                run_status_counts['completed'] += 1
                if end_time_str:
                    try:
                        end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                        if end_time >= hours_48_ago:
                            completed_last_48h += 1
                    except:
                        pass
            elif status in ['FAILED', 'WAITING_FOR_INSTRUMENT']:
                run_status_counts['failed'] += 1
            
            try:
                if end_time_str and status in ['COMPLETED', 'FAILED', 'WAITING_FOR_INSTRUMENT']:
                    end_time_parsed = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                    for i, interval in enumerate(intervals):
                        interval_start = hours_48_ago + timedelta(hours=i*6)
                        interval_end = interval_start + timedelta(hours=6)
                        if interval_start <= end_time_parsed < interval_end:
                            if status == 'COMPLETED':
                                interval['completed'] += 1
                            elif status in ['FAILED', 'WAITING_FOR_INSTRUMENT']:
                                interval['failed'] += 1
                            break
                elif start_time_str and status in ['STARTED', 'IN_PROGRESS']:
                    start_time_parsed = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                    for i, interval in enumerate(intervals):
                        interval_start = hours_48_ago + timedelta(hours=i*6)
                        interval_end = interval_start + timedelta(hours=6)
                        if interval_start <= start_time_parsed < interval_end:
                            interval['running'] += 1
                            break
            except Exception as e:
                LOGGER.warning(f"Error parsing timestamp for run {run.get('run_id')}: {e}")
                continue
        
        return {
            'total_workflows': len(workflow_items),
            'active_runs': run_status_counts['active'],
            'failed_runs': run_status_counts['failed'],
            'completed_runs_48h': completed_last_48h,
            'total_runs': run_status_counts['total'],
            'run_status_breakdown': {
                'active': run_status_counts['active'],
                'completed': run_status_counts['completed'],
                'failed': run_status_counts['failed']
            },
            'execution_activity': intervals,
            'period': '48_hours',
            'interval': '6_hours'
        }
    except Exception as e:
        LOGGER.error(f"Error retrieving dashboard data: {str(e)}")
        raise

# -------- Route Handlers ---------

def handle_get_workflows(qs):
    """Handle GET /workflows - return all workflows complete data"""
    try:
        workflows_data = get_all_workflows()
        return response(200, {
            'workflows': workflows_data,
            'count': len(workflows_data)
        })
    except Exception as e:
        LOGGER.error(f"Error in handle_get_workflows: {str(e)}")
        return response(500, {'error': 'Internal server error'})

def handle_get_workflow_by_id(workflow_id):
    """Handle GET /workflows/{id} - return specific workflow"""
    try:
        workflow = get_workflow_by_id(workflow_id)
        if not workflow:
            return response(404, {'error': 'Workflow not found'})
        return response(200, {'workflow': workflow})
    except Exception as e:
        LOGGER.error(f"Error in handle_get_workflow_by_id: {str(e)}")
        return response(500, {'error': 'Internal server error'})

def handle_get_runs(qs):
    """Handle GET /runs - return all runs mapped with workflow data"""
    try:
        runs_data = get_all_runs()
        
        workflows_data = get_all_workflows()
        workflow_map = {wf.get('workflow_id'): wf for wf in workflows_data}
        
        enhanced_runs = []
        for run in runs_data:
            workflow_id = run.get('workflow_id')
            workflow_info = workflow_map.get(workflow_id, {})
            
            enhanced_run = {
                **run,
                'workflow_info': {
                    'description': workflow_info.get('description', ''),
                    'created_at': workflow_info.get('created_at', ''),
                    'status': workflow_info.get('status', '')
                }
            }
            enhanced_runs.append(enhanced_run)
        
        return response(200, {
            'runs': enhanced_runs,
            'count': len(enhanced_runs)
        })
    except Exception as e:
        LOGGER.error(f"Error in handle_get_runs: {str(e)}")
        return response(500, {'error': 'Internal server error'})

def handle_get_run_by_id(run_id):
    """Handle GET /runs/{id} - return specific run with workflow info"""
    try:
        run = get_run_by_id(run_id)
        if not run:
            return response(404, {'error': 'Run not found'})
        return response(200, {'run': run})
    except Exception as e:
        LOGGER.error(f"Error in handle_get_run_by_id: {str(e)}")
        return response(500, {'error': 'Internal server error'})

def handle_get_dashboard():
    """Handle GET /dashboard - return combined KPI and timeline data"""
    try:
        dashboard_data = get_dashboard_data()
        return response(200, dashboard_data)
    except Exception as e:
        LOGGER.error(f"Error in handle_get_dashboard: {str(e)}")
        return response(500, {'error': 'Internal server error'})

def execute_athena_query(query):
    """Execute Athena query and return results"""
    try:
        execution = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': ATHENA_DATABASE, 'Catalog': ATHENA_CATALOG},
            ResultConfiguration={'OutputLocation': ATHENA_OUTPUT_S3}
        )
        execution_id = execution['QueryExecutionId']
        
        while True:
            status_response = athena_client.get_query_execution(QueryExecutionId=execution_id)
            status = status_response['QueryExecution']['Status']
            state = status['State']
            if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                break
        
        if state != 'SUCCEEDED':
            reason = status.get('StateChangeReason', 'Unknown error')
            LOGGER.error(f"Athena query failed. State: {state}, Reason: {reason}")
            LOGGER.error(f"Failed query: {query}")
            raise Exception(f"Query failed with state: {state}. Reason: {reason}")
        
        results = athena_client.get_query_results(QueryExecutionId=execution_id)
        rows = results['ResultSet']['Rows']
        if len(rows) < 2:
            return []
        
        headers = [col['VarCharValue'] for col in rows[0]['Data']]
        return [dict(zip(headers, [col.get('VarCharValue', '') for col in row['Data']])) for row in rows[1:]]
    except Exception as e:
        LOGGER.error(f"Athena query error: {str(e)}")
        raise

def get_alerts_data(start_date=None, end_date=None):
    """Get alerts from anomaly_events and workflow_events with workflow mapping"""
    try:
        date_filter = ""
        if start_date and end_date:
            date_filter = f"WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'"
        elif start_date:
            date_filter = f"WHERE timestamp >= '{start_date}'"
        elif end_date:
            date_filter = f"WHERE timestamp <= '{end_date}'"
        
        anomaly_query = f"SELECT id, event_type, run_id, step_id, timestamp, details FROM anomaly_events {date_filter} ORDER BY timestamp DESC"
        workflow_events_query = f"SELECT id, event_type, run_id, workflow_id, timestamp, user_id FROM workflow_events {date_filter} ORDER BY timestamp DESC"
        
        anomaly_events = execute_athena_query(anomaly_query)
        workflow_events = execute_athena_query(workflow_events_query)
        
        runs = get_all_runs()
        run_to_workflow = {run['run_id']: run.get('workflow_id') for run in runs}
        
        for event in anomaly_events:
            run_id = event.get('run_id')
            event['workflow_id'] = run_to_workflow.get(run_id, '')
        
        return {
            'anomaly_events': anomaly_events,
            'workflow_events': workflow_events,
            'total_anomalies': len(anomaly_events),
            'total_workflow_events': len(workflow_events)
        }
    except Exception as e:
        LOGGER.error(f"Error retrieving alerts: {str(e)}")
        raise

def handle_get_alerts(qs):
    """Handle GET /alerts - return anomaly and workflow events with date filtering"""
    try:
        start_date = qs.get('start_date')
        end_date = qs.get('end_date')
        alerts_data = get_alerts_data(start_date, end_date)
        return response(200, alerts_data)
    except Exception as e:
        LOGGER.error(f"Error in handle_get_alerts: {str(e)}")
        return response(500, {'error': 'Internal server error'})

# -------- Testing Code ---------

if __name__ == '__main__':
    print("="*100)
    print("WORKFLOW INFORMATION API - JSON RESPONSE SAMPLES FOR UI BINDING")
    print("="*100)
    
    # 1. GET /workflows
    print("\n\n" + "="*100)
    print("1️⃣  ENDPOINT: GET /workflows")
    print("="*100)
    test_event = {'httpMethod': 'GET', 'path': '/workflows', 'queryStringParameters': {}, 'body': None}
    result = lambda_handler(test_event, None)
    print(f"\nStatus Code: {result['statusCode']}")
    print("\nJSON RESPONSE:")
    print(json.dumps(json.loads(result['body']), indent=2, default=json_default))
    
    # 2. GET /workflows/{id}
    print("\n\n" + "="*100)
    print("2️⃣  ENDPOINT: GET /workflows/{workflow_id}")
    print("="*100)
    test_event = {'httpMethod': 'GET', 'path': '/workflows/bb12b5e1-e758-4d22-b9b0-12e7cbce5f9e', 'queryStringParameters': {}, 'body': None}
    result = lambda_handler(test_event, None)
    print(f"\nStatus Code: {result['statusCode']}")
    print("\nJSON RESPONSE:")
    print(json.dumps(json.loads(result['body']), indent=2, default=json_default))
    
    # 3. GET /runs
    print("\n\n" + "="*100)
    print("3️⃣  ENDPOINT: GET /runs")
    print("="*100)
    test_event = {'httpMethod': 'GET', 'path': '/runs', 'queryStringParameters': {}, 'body': None}
    result = lambda_handler(test_event, None)
    print(f"\nStatus Code: {result['statusCode']}")
    print("\nJSON RESPONSE:")
    print(json.dumps(json.loads(result['body']), indent=2, default=json_default))
    
    # 4. GET /runs/{id}
    print("\n\n" + "="*100)
    print("4️⃣  ENDPOINT: GET /runs/{run_id}")
    print("="*100)
    test_event = {'httpMethod': 'GET', 'path': '/runs/ae31104e-858c-4323-9384-1d5a15457d02', 'queryStringParameters': {}, 'body': None}
    result = lambda_handler(test_event, None)
    print(f"\nStatus Code: {result['statusCode']}")
    print("\nJSON RESPONSE:")
    print(json.dumps(json.loads(result['body']), indent=2, default=json_default))
    
    # 5. GET /dashboard
    print("\n\n" + "="*100)
    print("5️⃣  ENDPOINT: GET /dashboard")
    print("="*100)
    test_event = {'httpMethod': 'GET', 'path': '/dashboard', 'queryStringParameters': {}, 'body': None}
    result = lambda_handler(test_event, None)
    print(f"\nStatus Code: {result['statusCode']}")
    print("\nJSON RESPONSE:")
    print(json.dumps(json.loads(result['body']), indent=2, default=json_default))
    
    # 6. GET /alerts
    print("\n\n" + "="*100)
    print("6️⃣  ENDPOINT: GET /alerts")
    print("="*100)
    test_event = {'httpMethod': 'GET', 'path': '/alerts', 'queryStringParameters': {}, 'body': None}
    result = lambda_handler(test_event, None)
    print(f"\nStatus Code: {result['statusCode']}")
    print("\nJSON RESPONSE:")
    print(json.dumps(json.loads(result['body']), indent=2, default=json_default))
    
    # 7. GET /alerts with date range
    print("\n\n" + "="*100)
    print("7️⃣  ENDPOINT: GET /alerts?start_date=2026-01-01&end_date=2026-12-31")
    print("="*100)
    test_event = {'httpMethod': 'GET', 'path': '/alerts', 'queryStringParameters': {'start_date': '2026-01-01 00:00:00', 'end_date': '2026-12-31 23:59:59'}, 'body': None}
    result = lambda_handler(test_event, None)
    print(f"\nStatus Code: {result['statusCode']}")
    print("\nJSON RESPONSE:")
    print(json.dumps(json.loads(result['body']), indent=2, default=json_default))
    
    print("\n\n" + "="*100)
    print("✅ ALL ENDPOINT JSON RESPONSES PRINTED ABOVE")
    print("="*100)
    print("\nENDPOINTS:")
    print("  1. GET /workflows          - All workflows with complete data")
    print("  2. GET /workflows/{id}     - Specific workflow by ID")
    print("  3. GET /runs               - All workflow runs with workflow info")
    print("  4. GET /runs/{id}          - Specific run by ID with workflow info")
    print("  5. GET /dashboard          - Combined KPI metrics and timeline (48h, 6h intervals)")
    print("  6. GET /alerts             - All alerts from anomaly_events and workflow_events")
    print("  7. GET /alerts?start_date=YYYY-MM-DD HH:MM:SS&end_date=YYYY-MM-DD HH:MM:SS")
    print("="*100)
