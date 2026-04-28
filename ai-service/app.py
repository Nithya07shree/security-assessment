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

@app.route('/', methods=['GET'])
def health():
    return {"status": "ok", "service": "tool-53-ai-service"}, 200

 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)