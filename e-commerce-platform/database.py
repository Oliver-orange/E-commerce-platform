import sqlite3

# 数据库文件名
DATABASE = 'ecommerce.db'


def connect_db():
    """连接到数据库"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # 让返回的结果可以通过列名访问
    return conn


def create_tables():
    """创建所需的数据库表"""
    conn = connect_db()
    cursor = conn.cursor()

    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # 创建产品表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')

    # 创建购物车表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    conn.commit()
    conn.close()


def add_initial_products():
    """添加初始产品数据"""
    initial_products = [
        ('Product 1', 19.99),
        ('Product 2', 29.99),
        ('Product 3', 39.99),
        ('Product 4', 49.99),
        ('Product 5', 59.99)
    ]

    conn = connect_db()
    cursor = conn.cursor()

    for product in initial_products:
        cursor.execute('INSERT INTO products (name, price) VALUES (?, ?)', product)

    conn.commit()
    conn.close()


def add_user(username, email, password):
    """添加用户"""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                       (username, email, password))
        conn.commit()
    except sqlite3.IntegrityError:
        return None  # 用户名或邮箱已经存在
    finally:
        conn.close()

    return cursor.lastrowid


def add_product(name, price):
    """添加产品"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO products (name, price) VALUES (?, ?)', (name, price))
    conn.commit()
    conn.close()
    return cursor.lastrowid


def get_all_products():
    """获取所有产品"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    return products


def add_to_cart(user_id, product_id, quantity=1):
    """将产品添加到购物车"""
    conn = connect_db()
    cursor = conn.cursor()

    # 检查购物车中是否已经存在该产品
    cursor.execute('SELECT * FROM cart WHERE user_id = ? AND product_id = ?', (user_id, product_id))
    item = cursor.fetchone()

    if item:
        # 如果已存在，更新数量
        cursor.execute('UPDATE cart SET quantity = quantity + ? WHERE user_id = ? AND product_id = ?',
                       (quantity, user_id, product_id))
    else:
        # 如果不存在，插入新记录
        cursor.execute('INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)',
                       (user_id, product_id, quantity))

    conn.commit()
    conn.close()


def get_cart_items(user_id):
    """获取用户购物车中的所有项目"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.name, p.price, c.quantity FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    ''', (user_id,))
    items = cursor.fetchall()
    conn.close()
    return items


def clear_cart(user_id):
    """清空用户购物车"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()


# 初始化数据库
if __name__ == '__main__':
    create_tables()
    add_initial_products()  # 添加初始产品数据
