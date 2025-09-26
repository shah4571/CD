# bot/handlers/__init__.py
# Import all handler registration functions here

from .start import register_start
from .cap import register_cap
from .account import register_account
from .withdraw import register_withdraw
from .support import register_support
from .admin import register_admin

def init_handlers(app):
    """
    Register all bot handlers
    """
    register_start(app)
    register_cap(app)
    register_account(app)
    register_withdraw(app)
    register_support(app)
    register_admin(app)
