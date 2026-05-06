import threading
import json
from pathlib import Path
from datetime import datetime
from loguru import logger

JOBS_DIR = Path("exports/jobs")
JOBS_DIR.mkdir(parents=True, exist_ok=True)

def _job_file(job_id):
    return JOBS_DIR / f"{job_id}.json"

def get_job(job_id):
    f = _job_file(job_id)
    if not f.exists():
        return {"status": "not_found"}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except:
        return {"status": "error"}

def _save_job(job_id, data):
    _job_file(job_id).write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def run_test_plan_in_background(job_id, cr_text):
    _save_job(job_id, {
        "job_id": job_id, "status": "running",
        "type": "test_plan",
        "started_at": datetime.now().isoformat(),
        "result": None, "error": None
    })
    def _run():
        try:
            from src.generation.test_plan_generator import generate_test_plan
            result = generate_test_plan(cr_text, stream=False)
            _save_job(job_id, {
                "job_id": job_id, "status": "done",
                "type": "test_plan",
                "finished_at": datetime.now().isoformat(),
                "result": result, "error": None
            })
            logger.info(f"Job {job_id} done")
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            _save_job(job_id, {
                "job_id": job_id, "status": "error",
                "error": str(e), "result": None
            })
    threading.Thread(target=_run, daemon=True).start()

def run_test_cases_in_background(job_id, cr_text):
    _save_job(job_id, {
        "job_id": job_id, "status": "running",
        "type": "test_cases",
        "started_at": datetime.now().isoformat(),
        "result": None, "error": None
    })
    def _run():
        try:
            from src.generation.test_case_generator import generate_test_cases
            result = generate_test_cases(cr_text, stream=False)
            _save_job(job_id, {
                "job_id": job_id, "status": "done",
                "type": "test_cases",
                "finished_at": datetime.now().isoformat(),
                "result": result, "error": None
            })
        except Exception as e:
            _save_job(job_id, {
                "job_id": job_id, "status": "error",
                "error": str(e), "result": None
            })
    threading.Thread(target=_run, daemon=True).start()

def list_recent_jobs(limit=10):
    jobs = []
    for f in sorted(JOBS_DIR.glob("*.json"), reverse=True)[:limit]:
        try:
            jobs.append(json.loads(f.read_text(encoding="utf-8")))
        except:
            pass
    return jobs