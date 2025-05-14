import json
import time
import sys
import os

# ✅ Ensure root of project is in the Python path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ✅ Now import using full path from root
from backend.scrapers.amazon.scrape_amazon_titles import scrape_amazon_product_page

from uuid import uuid4

QUEUE_PATH = "scrape_queue.json"
RESULTS_PATH = "scrape_results.json"

def load_queue():
    if not os.path.exists(QUEUE_PATH):
        return []
    with open(QUEUE_PATH, "r") as f:
        return json.load(f)

def save_queue(queue):
    with open(QUEUE_PATH, "w") as f:
        json.dump(queue, f, indent=2)

def load_results():
    if not os.path.exists(RESULTS_PATH):
        return {}
    with open(RESULTS_PATH, "r") as f:
        return json.load(f)

def save_results(results):
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)

def process_jobs():
    print("📦 Worker started")
    while True:
        queue = load_queue()
        updated = False
        for job in queue:
            if job["status"] == "queued":
                print(f"🔧 Processing job {job['id']}...")

                try:
                    product = scrape_amazon_product_page(job["amazon_url"])
                    job["status"] = "done"
                    job["result"] = product
                    print(f"✅ Finished job {job['id']}")

                    # Save to result store
                    results = load_results()
                    results[job["id"]] = product
                    save_results(results)
                except Exception as e:
                    job["status"] = "error"
                    job["error"] = str(e)
                    print(f"❌ Failed to process job {job['id']}: {e}")
                updated = True

        if updated:
            save_queue(queue)

        time.sleep(5)  # Poll every few seconds


if __name__ == "__main__":
    process_jobs()
