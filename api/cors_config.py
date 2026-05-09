# cors_config.py - CORS Configuration untuk Drama API

"""
CORS Configuration Module
Menangani Cross-Origin Resource Sharing untuk memungkinkan request dari berbagai domain
"""

# ============================================================
# ALLOWED ORIGINS
# ============================================================
# Untuk production, tentukan domain spesifik
ALLOWED_ORIGINS = {
    "development": ["*"],  # Development: Allow all origins
    "production": [
        "https://dramacina.vip",
        "https://www.dramacina.vip",
        "https://melolo.dramabos.my.id",
        "https://yourfrontend.com",  # Ganti dengan domain frontend Anda
        # Tambahkan domain lain sesuai kebutuhan
    ]
}

# ============================================================
# CORS HEADERS
# ============================================================
CORS_CONFIG = {
    "origins": ["*"],  # Set ke list specific domains untuk production
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    "allow_headers": [
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Accept",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers"
    ],
    "expose_headers": [
        "Content-Type",
        "X-Total-Count",
        "X-Page-Number",
        "X-Page-Size",
        "Content-Length",
        "ETag"
    ],
    "supports_credentials": False,  # Set True jika perlu cookies/auth
    "max_age": 3600,  # Cache preflight selama 1 jam
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_cors_config(environment="development"):
    """
    Dapatkan CORS config berdasarkan environment
    
    Args:
        environment (str): "development" atau "production"
    
    Returns:
        dict: CORS configuration
    """
    config = CORS_CONFIG.copy()
    
    if environment == "production":
        config["origins"] = ALLOWED_ORIGINS["production"]
        config["supports_credentials"] = True
    else:
        config["origins"] = ALLOWED_ORIGINS["development"]
    
    return config


def add_cors_headers(response, origin=None):
    """
    Tambahkan CORS headers ke response secara manual (fallback)
    
    Args:
        response: Flask response object
        origin (str): Origin yang diperbolehkan
    
    Returns:
        response: Response dengan CORS headers
    """
    response.headers['Access-Control-Allow-Origin'] = origin or '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response
