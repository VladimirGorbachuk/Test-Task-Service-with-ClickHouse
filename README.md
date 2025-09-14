"# Test-Task-Service-with-ClickHouse" 
(consists of four parts)

to check that it works:
# first: 
set or export
DATABASE_URL=your url to postgres
and simple script
import requests
response = requests.get("http://127.0.0.1:8000/api/db_version")
and then check response.status_code, response.text