from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import ValidationError
#from models import SurveySubmission, StoredSurveyRecord
from storage import append_json_line

#added code
from models import SurveySubmission
from storage import save_submission
#
app = Flask(__name__)
# Allow cross-origin requests so the static HTML can POST from localhost or file://
CORS(app, resources={r"/v1/*": {"origins": "*"}})

@app.route("/ping", methods=["GET"])
def ping():
    """Simple health check endpoint."""
    return jsonify({
        "status": "ok",
        "message": "API is alive",
        "utc_time": datetime.now(timezone.utc).isoformat()
    })

@app.post("/v1/survey")
def submit_survey():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "invalid_json", "detail": "Body must be application/json"}), 400

    try:
        submission = SurveySubmission(**payload)
    except ValidationError as ve:
        return jsonify({"error": "validation_error", "detail": ve.errors()}), 422
    
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "")
    user_agent = request.headers.get("User-Agent")

    try:
        save_submission(submission, ip=ip, user_agent=user_agent)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Error saving submission:", e)
        return jsonify({"error": "internal_server_error", "detail": str(e)}), 500

    return jsonify({"status": "ok"}), 201

if __name__ == "__main__":
    app.run(port=5000, debug=True)
