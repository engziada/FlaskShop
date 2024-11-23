from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, session
from flask_login import login_required
from app.models import Product

bp = Blueprint('cart', __name__, url_prefix='/cart')

@bp.route('/')
@login_required
def index():
    cart_items = []
    subtotal = 0
    shipping = 10.00
    
    if 'cart' in session:
        for product_id, quantity in session['cart'].items():
            product = Product.query.get(int(product_id))
            if product:
                item_total = product.price * quantity
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'total': item_total
                })
                subtotal += item_total
    
    total = subtotal + shipping if cart_items else 0
    
    return render_template('shop/cart.html',
                         cart_items=cart_items,
                         subtotal=subtotal,
                         shipping=shipping,
                         total=total)

@bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    
    if quantity > product.stock:
        flash(f'Sorry, only {product.stock} items available in stock.', 'danger')
        return redirect(url_for('shop.product', id=product_id))
    
    if 'cart' not in session:
        session['cart'] = {}
    
    if str(product_id) in session['cart']:
        session['cart'][str(product_id)] += quantity
    else:
        session['cart'][str(product_id)] = quantity
    
    session.modified = True
    flash(f'{product.name} ({quantity} items) added to cart.', 'success')
    return redirect(url_for('cart.index'))

@bp.route('/update', methods=['POST'])
@login_required
def update():
    data = request.get_json()
    product_id = str(data.get('product_id'))
    quantity = data.get('quantity')
    
    if not all([product_id, quantity]):
        return jsonify({'success': False, 'error': 'Invalid request data'})
    
    if 'cart' not in session:
        session['cart'] = {}
    
    product = Product.query.get(int(product_id))
    if not product:
        return jsonify({'success': False, 'error': 'Product not found'})
    
    if isinstance(quantity, int):
        if quantity <= 0:
            if product_id in session['cart']:
                del session['cart'][product_id]
        elif quantity <= product.stock:
            session['cart'][product_id] = quantity
        else:
            return jsonify({'success': False, 'error': 'Not enough stock'})
    else:
        current_quantity = session['cart'].get(product_id, 0)
        new_quantity = current_quantity + quantity
        
        if new_quantity <= 0:
            if product_id in session['cart']:
                del session['cart'][product_id]
        elif new_quantity <= product.stock:
            session['cart'][product_id] = new_quantity
        else:
            return jsonify({'success': False, 'error': 'Not enough stock'})
    
    session.modified = True
    return jsonify({'success': True})

@bp.route('/remove/<int:product_id>', methods=['POST'])
@login_required
def remove(product_id):
    if 'cart' in session and str(product_id) in session['cart']:
        del session['cart'][str(product_id)]
        session.modified = True
        flash('Item removed from cart.', 'success')
    return redirect(url_for('cart.index'))

@bp.route('/checkout')
@login_required
def checkout():
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('cart.index'))
    return render_template('shop/checkout.html')