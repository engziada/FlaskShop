from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from flask_login import login_required
from sqlalchemy import or_
from app import db
from app.models import Product, Category

bp = Blueprint("shop", __name__, url_prefix="/shop")

@bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    per_page = 9
    query = Product.query
    
    search = request.args.get("search", "")
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term)
            )
        )
    
    category_id = request.args.get("category", type=int)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    sort = request.args.get("sort", "")
    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort == "name_asc":
        query = query.order_by(Product.name.asc())
    elif sort == "name_desc":
        query = query.order_by(Product.name.desc())
    else:
        query = query.order_by(Product.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items
    categories = Category.query.all()
    
    return render_template("shop/index.html",
                         products=products,
                         categories=categories,
                         pagination=pagination,
                         search=search,
                         category_id=category_id,
                         min_price=min_price,
                         max_price=max_price,
                         sort=sort)

@bp.route("/product/<int:id>")
def product(id):
    product = Product.query.get_or_404(id)
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id
    ).limit(3).all()
    return render_template("shop/product.html",
                         product=product,
                         related_products=related_products)

@bp.route("/category/<int:id>")
def category(id):
    category = Category.query.get_or_404(id)
    page = request.args.get("page", 1, type=int)
    per_page = 9
    products = Product.query.filter_by(category_id=id).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template("shop/category.html",
                         category=category,
                         products=products)

@bp.route("/cart")
@login_required
def cart():
    cart_items = []
    subtotal = 0
    shipping = 10.00
    
    if "cart" in session:
        for product_id, quantity in session["cart"].items():
            product = Product.query.get(int(product_id))
            if product:
                item_total = product.price * quantity
                cart_items.append({
                    "product": product,
                    "quantity": quantity,
                    "total": item_total
                })
                subtotal += item_total
    
    total = subtotal + shipping if cart_items else 0
    
    cart_count = len(cart_items)

    return render_template(
        "shop/cart.html",
        cart_items=cart_items,
        subtotal=subtotal,
        shipping=shipping,
        total=total,
        cart_count=cart_count,
    )

@bp.route("/add-to-cart/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get("quantity", 1))
    
    if quantity > product.stock:
        flash(f"Sorry, only {product.stock} items available in stock.", "danger")
        return redirect(url_for("shop.product", id=product_id))
    
    if "cart" not in session:
        session["cart"] = {}
    
    if str(product_id) in session["cart"]:
        session["cart"][str(product_id)] += quantity
    else:
        session["cart"][str(product_id)] = quantity
    
    session.modified = True
    flash(f"{product.name} ({quantity} items) added to cart.", "success")
    return redirect(url_for("shop.cart"))

@bp.route("/update-cart", methods=["POST"])
@login_required
def update_cart():
    data = request.get_json()
    product_id = str(data.get("product_id"))
    quantity = data.get("quantity")
    
    if not all([product_id, quantity]):
        return jsonify({"success": False, "error": "Invalid request data"})
    
    if "cart" not in session:
        session["cart"] = {}
    
    product = Product.query.get(int(product_id))
    if not product:
        return jsonify({"success": False, "error": "Product not found"})
    
    if isinstance(quantity, int):
        if quantity <= 0:
            if product_id in session["cart"]:
                del session["cart"][product_id]
        elif quantity <= product.stock:
            session["cart"][product_id] = quantity
        else:
            return jsonify({"success": False, "error": "Not enough stock"})
    else:
        current_quantity = session["cart"].get(product_id, 0)
        new_quantity = current_quantity + quantity
        
        if new_quantity <= 0:
            if product_id in session["cart"]:
                del session["cart"][product_id]
        elif new_quantity <= product.stock:
            session["cart"][product_id] = new_quantity
        else:
            return jsonify({"success": False, "error": "Not enough stock"})
    
    session.modified = True
    return jsonify({"success": True})

@bp.route("/remove-from-cart/<int:product_id>", methods=["POST"])
@login_required
def remove_from_cart(product_id):
    if "cart" in session and str(product_id) in session["cart"]:
        del session["cart"][str(product_id)]
        session.modified = True
        flash("Item removed from cart.", "success")
    return redirect(url_for("shop.cart"))

@bp.route("/checkout")
@login_required
def checkout():
    if "cart" not in session or not session["cart"]:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("shop.cart"))
    return render_template("shop/checkout.html")
