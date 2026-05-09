# middleware.py - Request/Response Middleware untuk Drama API

"""
Middleware untuk request logging, response timing, dan CORS error handling
"""

from functools import wraps
from flask import request, jsonify
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# REQUEST LOGGING MIDDLEWARE
# ============================================================

def request_logging(f):
    """
    Decorator untuk log semua incoming requests
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Log request info
        logger.info(f"[REQUEST] {request.method} {request.path}")
        logger.info(f"[ORIGIN] {request.origin}")
        logger.info(f"[ARGS] {request.args.to_dict()}")
        
        # Measure execution time
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"[RESPONSE] Status: 200, Time: {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[ERROR] {str(e)}, Time: {elapsed:.2f}s")
            raise
    
    return decorated_function


# ============================================================
# CORS ERROR HANDLER
# ============================================================

def handle_cors_error(app):
    """
    Register CORS error handler untuk better error messages
    """
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({
            "creator": "SanzzXD",
            "status": False,
            "code": 400,
            "message": "Bad Request - Invalid parameters",
            "error": str(e)
        }), 400
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "creator": "SanzzXD",
            "status": False,
            "code": 404,
            "message": "Endpoint not found",
            "path": request.path
        }), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({
            "creator": "SanzzXD",
            "status": False,
            "code": 500,
            "message": "Internal Server Error",
            "error": str(e)
        }), 500
    
    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({
            "creator": "SanzzXD",
            "status": False,
            "code": 403,
            "message": "CORS Error: Origin not allowed",
            "origin": request.origin
        }), 403


# ============================================================
# RESPONSE TIMING MIDDLEWARE
# ============================================================

class ResponseTimingMiddleware:
    """
    Track dan add response timing headers
    """
    def __init__(self, app):
        self.app = app
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        request.start_time = time.time()
    
    def after_request(self, response):
        if hasattr(request, 'start_time'):
            elapsed = time.time() - request.start_time
            response.headers['X-Response-Time'] = f"{elapsed:.3f}s"
        return response


# ============================================================
# PREFLIGHT REQUEST HANDLER
# ============================================================

def handle_preflight(app):
    """
    Explicit handler untuk OPTIONS/preflight requests
    """
    @app.before_request
    def handle_preflight_request():
        if request.method == "OPTIONS":
            response = jsonify({'status': 'ok'})
            response.headers.add("Access-Control-Allow-Origin", request.origin or "*")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
            response.headers.add("Access-Control-Max-Age", "3600")
            return response, 200
    
    return app


# ============================================================
# SECURITY HEADERS MIDDLEWARE
# ============================================================

def add_security_headers(app):
    """
    Add security headers to all responses
    """
    @app.after_request
    def set_security_headers(response):
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        # Enable XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response


# ============================================================
# REQUEST VALIDATION MIDDLEWARE
# ============================================================

def validate_request(f):
    """
    Decorator untuk validate required parameters
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if request origin is set (CORS awareness)
        origin = request.origin or request.remote_addr
        
        # Check if Content-Type is valid (if POST/PUT)
        if request.method in ['POST', 'PUT']:
            content_type = request.content_type
            if content_type and 'application/json' not in content_type:
                return jsonify({
                    "creator": "SanzzXD",
                    "status": False,
                    "code": 400,
                    "message": "Content-Type must be application/json"
                }), 400
        
        return f(*args, **kwargs)
    
    return decorated_function


# ============================================================
# RATE LIMITING HELPER (untuk future implementation)
# ============================================================

from collections import defaultdict
from datetime import datetime, timedelta

class SimpleRateLimiter:
    """
    Simple in-memory rate limiter
    Untuk production, gunakan Redis
    """
    def __init__(self, requests_per_minute=60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id):
        """
        Check if client is allowed to make request
        client_id bisa dari IP address atau user ID
        """
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.requests_per_minute:
            return False
        
        # Add current request
        self.requests[client_id].append(now)
        return True
    
    def get_remaining(self, client_id):
        """Get remaining requests for client"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        return self.requests_per_minute - len(self.requests[client_id])


# ============================================================
# SETUP FUNCTION
# ============================================================

def setup_middleware(app):
    """
    Setup semua middleware sekaligus
    
    Usage di index.py:
    from middleware import setup_middleware
    setup_middleware(app)
    """
    # Add error handlers
    handle_cors_error(app)
    
    # Add security headers
    add_security_headers(app)
    
    # Add preflight handler
    handle_preflight(app)
    
    # Add response timing
    ResponseTimingMiddleware(app)
    
    logger.info("[Middleware] All middleware loaded successfully")
    return app
