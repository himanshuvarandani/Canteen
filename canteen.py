from app import app, db
from app.models import Dishes, History, Orders, Quantity, RecentOrders, User


@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'Dishes':Dishes, 'History':History,
        'Orders':Orders, 'RecentOrders':RecentOrders,
        'User':User}
