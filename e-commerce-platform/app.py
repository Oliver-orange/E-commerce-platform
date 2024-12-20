from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import database  # 导入之前创建的 database.py

app = Flask(__name__)
app.secret_key = 'secret_key'  # 用于会话管理

# 初始化数据库
database.create_tables()


# 根路由，展示产品列表
@app.route('/')
def product_listing():
    products = database.get_all_products()  # 获取所有产品
    return render_template('product_listing.html', products=products)


# 登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 在这里检查用户凭据
        conn = database.connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']  # 存储用户ID到session
            return redirect(url_for('product_listing'))
        else:
            return 'Invalid username or password', 401
    return render_template('login.html')


# 注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_id = database.add_user(username, email, password)
        if user_id:
            return redirect(url_for('login'))
        else:
            return 'User already exists', 400
    return render_template('register.html')


# 购物车
@app.route('/cart')
def cart():
    user_id = session.get('user_id')  # 从session获取用户ID
    if not user_id:
        return redirect(url_for('login'))  # 未登录则重定向到登录
    items = database.get_cart_items(user_id)

    # 计算总金额
    total_amount = sum(item['price'] * item['quantity'] for item in items)

    return render_template('cart.html', items=items, total_amount=total_amount)


# 添加产品到购物车
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    user_id = session.get('user_id')  # 获取用户ID
    if not user_id:
        return jsonify({'success': False}), 401  # 未登录返回401
    product_id = request.form.get('product_id')

    # 确保 product_id 是整数
    try:
        product_id = int(product_id)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid product ID'}), 400

    database.add_to_cart(user_id, product_id)
    return jsonify({'success': True})


# 提交结账
@app.route('/checkout', methods=['POST'])
def submit_checkout():
    user_id = session.get('user_id')  # 获取用户ID
    if not user_id:
        return jsonify({'success': False}), 401  # 未登录返回401
    database.clear_cart(user_id)  # 清空购物车
    return jsonify({'success': True})


# 用户个人资料
@app.route('/profile')
def profile():
    user_id = session.get('user_id')  # 从session获取用户ID
    if not user_id:
        return redirect(url_for('login'))  # 未登录则重定向到登录
    conn = database.connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT username, email FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    return render_template('profile.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
