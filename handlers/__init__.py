from . import admin_handlers
from . import user_handlers

from loader import dp
admin_handlers.register_admin_handlers(dp)
user_handlers.register_user_handlers(dp)