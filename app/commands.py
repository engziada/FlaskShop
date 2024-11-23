
import click
from flask.cli import with_appcontext
from app import db
from app.models import User, Category, Product
from werkzeug.security import generate_password_hash

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database with some test data."""
    # Drop all tables and recreate them
    db.drop_all()
    db.create_all()

    # Create admin user
    admin = User(
        username='admin',
        email='admin@example.com',
        password_hash=generate_password_hash('admin'),
        is_admin=True,
        first_name='Admin',
        last_name='User'
    )
    db.session.add(admin)

    # Create categories
    categories = [
        Category(name='Electronics', description='Electronic devices and accessories'),
        Category(name='Clothing', description='Fashion items and accessories'),
        Category(name='Books', description='Books and publications'),
        Category(name='Home & Garden', description='Items for home and garden')
    ]
    for category in categories:
        db.session.add(category)

    db.session.commit()

    # Create sample products
    products = [
        Product(
            name='Smartphone',
            description='Latest model smartphone with advanced features',
            price=699.99,
            stock=50,
            category_id=1
        ),
        Product(
            name='T-Shirt',
            description='Comfortable cotton t-shirt',
            price=19.99,
            stock=100,
            category_id=2
        ),
        Product(
            name='Python Programming Book',
            description='Learn Python programming from basics to advanced',
            price=39.99,
            stock=30,
            category_id=3
        ),
        Product(
            name='Garden Tools Set',
            description='Complete set of essential garden tools',
            price=89.99,
            stock=20,
            category_id=4
        )
    ]
    for product in products:
        db.session.add(product)

    db.session.commit()
    click.echo('Database initialized with test data.')
