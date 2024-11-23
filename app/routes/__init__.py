# Import blueprints for easy access
from .main import bp as main_bp
from .shop import bp as shop_bp
from .admin import bp as admin_bp
from .auth import bp as auth_bp
from .cart import bp as cart_bp

# Export blueprints
__all__ = ['main_bp', 'shop_bp']
