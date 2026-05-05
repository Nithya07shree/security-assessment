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


from services.rag_pipeline import seed_collection

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

seed_collection()

@app.route('/', methods=['GET'])
def health():
    return {"status": "ok", "service": "tool-53-ai-service"}, 200

@app.after_request
def add_security_headers(response):

    # strict content type enforcement
    response.headers[
        "X-Content-Type-Options"
    ] = "nosniff"

    # prevent clickjacking
    response.headers[
        "X-Frame-Options"
    ] = "DENY"

    # prevent referrer tracking
    response.headers[
        "Referrer-Policy"
    ] = "no-referrer"

    # hide Flask version
    response.headers.pop(
        "Server",
        None
    )

    # CSP
    response.headers[
        "Content-Security-Policy"
    ] = (
        "default-src 'self'; "
        "frame-ancestors 'none'; "
        "object-src 'none';"
    )

    # remove server info if possible
    response.headers.pop(
        "Server",
        None
    )

    return response
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)