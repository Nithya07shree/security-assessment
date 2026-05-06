""" 
Flask entry point

- Adding sanitization middleware
- Adding rate limiting
"""
from flask import Flask
import logging
from middleware.input_sanitize import register_sanitization_hooks
from middleware.rate_limit import register_rate_limiting

from routes.describe import describe_bp
from routes.recommend import recommend_bp
from routes.categorise import categorise_bp
from routes.test_rag import test_rag_bp
from routes.generate_report import generate_report_bp
from routes.query import query_bp
from routes.health import health_bp
from routes.analyse_document import analyse_document_bp
from routes.batch_process import batch_process_bp
from routes.job_status import job_status_bp
from flask_talisman import Talisman

from services.rag_pipeline import seed_collection

werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_logger.setLevel(logging.ERROR)
# register logging
logging.basicConfig(
    filename='application_logs.log',
    level = logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)

app = Flask(__name__)


""" 
sanitization checks every incoming request body
To be called before any routes are registered

sanitization to be placed before rate limiting as: 
- the requests are sanitized (if malicious) that could consume user's rate limit quota before being rejected
- bad requests get a 400 status code and are never counted against rate limit
"""
register_sanitization_hooks(app)
register_rate_limiting(app)

# register routes below
app.register_blueprint(describe_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(categorise_bp)
app.register_blueprint(test_rag_bp)
app.register_blueprint(generate_report_bp)
app.register_blueprint(query_bp)
app.register_blueprint(health_bp)
app.register_blueprint(analyse_document_bp)
app.register_blueprint(batch_process_bp)
app.register_blueprint(job_status_bp)

seed_collection()

Talisman(
    app,
    force_https=False,
    frame_options="DENY",
    content_security_policy={
        "default-src":"'self'",
        "script-src":"'self'",
        "style-src":"'self'",
        "img-src":["'self'","data:"],
        "object-src":"'none'",
        "base-uri":"'self'",
        "frame-ancestors":"'none'"
    },
    referrer_policy="no-referrer"
)

@app.route('/', methods=['GET'])
def health():
    return {"status": "ok", "service": "tool-53-ai-service"}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)