import json
from pathlib import Path
from datetime import datetime
from typing import Mapping, Any

RESULTS_PATH = Path("data/survey.ndjson")

#added Code
import hashlib
from typing import Optional
from models import SurveySubmission

def sha256_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def save_submission(submission: SurveySubmission, ip: str, user_agent: Optional[str] = None):
    try:
        record = submission.dict(exclude_none = True)

        # Hash PII

        # Add or compute submission_id
        if not record.get("submission_id"):
            date_hour = datetime.utcnow().strftime("%Y%m%d%H")
            record["submission_id"] = sha256_hash(submission.email + date_hour)
        
        record["email"] = sha256_hash(record["email"])
        record["age"] = sha256_hash(str(record["age"]))
        # Add server-enriched fields
        record["received_at"] = datetime.utcnow().isoformat()
        record["ip"] = ip
        record["user_agent"] = record.get("user_agent") or user_agent

        # Print record to debug
        print("Saving record:", record)

        # Append to NDJSON
        append_json_line(record)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Error inside save_submission():", e)
        raise
#
def append_json_line(record: Mapping[str, Any]) -> None:
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_PATH.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                record,
                ensure_ascii=False,
                default=lambda o: o.isoformat() if isinstance(o, datetime) else o
            ) + "\n"
        )