from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import bcrypt, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'agri_secret_key_2024'

app.config['MYSQL_HOST']        = 'localhost'
app.config['MYSQL_USER']        = 'root'
app.config['MYSQL_PASSWORD']    = 'Santhiya@05'   # ← change this
app.config['MYSQL_DB']          = 'agri_platform'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

os.makedirs('static/images/uploads', exist_ok=True)


# ══════════════════════════════════════════════════════════════
# ML HELPERS — lazy imports so app starts without scikit-learn
# ══════════════════════════════════════════════════════════════
def _predict_price(crop):
    from ml_models.price_predictor import predict_price
    return predict_price(crop)

def _get_crop_advice(location, season, soil_type):
    from ml_models.crop_advisor import get_crop_advice
    return get_crop_advice(location, season, soil_type)

def _grade_crop_quality(crop, params):
    from ml_models.quality_grader import grade_crop_quality
    return grade_crop_quality(crop, params)

def _match_schemes(state, crop, land_size, category):
    from ml_models.scheme_matcher import match_schemes
    return match_schemes(state, crop, land_size, category)

def _chatbot_response(message, session_id='default'):
    from ml_models.agri_chatbot import chatbot_response
    return chatbot_response(message, session_id)


# ══════════════════════════════════════════════════════════════
# NOTIFICATION HELPER
# ══════════════════════════════════════════════════════════════
def create_notification(user_id, message, notif_type='system'):
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO notifications (user_id, message, type, is_read, created_at) VALUES (%s,%s,%s,0,%s)",
            (user_id, message, notif_type, datetime.now())
        )
        mysql.connection.commit()
    except Exception as e:
        print(f"[Notif Error] {e}")


# ══════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════
@app.route('/')
def index():
    return render_template('index.html')


# ══════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form['name']
        email    = request.form['email']
        password = request.form['password'].encode('utf-8')
        role     = request.form['role']
        phone    = request.form.get('phone', '')
        location = request.form.get('location', '')
        hashed   = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))

        cur.execute(
            "INSERT INTO users (name,email,password,role,phone,location,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (name, email, hashed.decode('utf-8'), role, phone, location, datetime.now())
        )
        mysql.connection.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password'].encode('utf-8')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
            session['user_id']   = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            flash(f"Welcome back, {user['name']}!", 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid email or password!', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM listings WHERE status='active'");         active_listings    = cur.fetchone()['c']
    cur.execute("SELECT COUNT(*) AS c FROM users");                                   total_users        = cur.fetchone()['c']
    cur.execute("SELECT COUNT(*) AS c FROM equipment");                               total_equipment    = cur.fetchone()['c']
    cur.execute("SELECT COUNT(*) AS c FROM transactions");                            total_transactions = cur.fetchone()['c']
    cur.execute("""SELECT l.*,u.name AS farmer_name,u.location FROM listings l
                   JOIN users u ON l.user_id=u.id WHERE l.status='active'
                   ORDER BY l.created_at DESC LIMIT 6""")
    recent_listings = cur.fetchall()

    return render_template('dashboard.html',
        active_listings=active_listings, total_users=total_users,
        total_equipment=total_equipment, total_transactions=total_transactions,
        recent_listings=recent_listings)


# ══════════════════════════════════════════════════════════════
# MARKETPLACE
# ══════════════════════════════════════════════════════════════
@app.route('/marketplace')
def marketplace():
    cur             = mysql.connection.cursor()
    crop_filter     = request.args.get('crop', '')
    location_filter = request.args.get('location', '')
    sort            = request.args.get('sort', 'newest')

    q      = "SELECT l.*,u.name AS farmer_name,u.location,u.phone FROM listings l JOIN users u ON l.user_id=u.id WHERE l.status='active'"
    params = []
    if crop_filter:     q += " AND l.crop_name LIKE %s";  params.append(f'%{crop_filter}%')
    if location_filter: q += " AND u.location LIKE %s";   params.append(f'%{location_filter}%')
    q += " ORDER BY l.price_per_kg ASC" if sort=='price_low' else " ORDER BY l.price_per_kg DESC" if sort=='price_high' else " ORDER BY l.created_at DESC"

    cur.execute(q, params)
    return render_template('marketplace.html', listings=cur.fetchall(),
        crop_filter=crop_filter, location_filter=location_filter, sort=sort)


@app.route('/add_listing', methods=['GET', 'POST'])
def add_listing():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO listings (user_id,crop_name,quantity_kg,price_per_kg,description,harvest_date,quality_grade,status,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,'active',%s)",
            (session['user_id'], request.form['crop_name'], request.form['quantity_kg'],
             request.form['price_per_kg'], request.form.get('description',''),
             request.form.get('harvest_date') or None, request.form.get('quality_grade','B'), datetime.now())
        )
        mysql.connection.commit()
        flash('Listing added successfully!', 'success')
        return redirect(url_for('marketplace'))
    return render_template('add_listing.html')


@app.route('/listing/<int:listing_id>')
def listing_detail(listing_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT l.*,u.name AS farmer_name,u.location,u.phone,u.email FROM listings l JOIN users u ON l.user_id=u.id WHERE l.id=%s", (listing_id,))
    listing = cur.fetchone()
    if not listing:
        flash('Listing not found', 'danger')
        return redirect(url_for('marketplace'))
    predicted = _predict_price(listing['crop_name'])
    cur.execute("SELECT b.*,u.name AS buyer_name FROM bids b JOIN users u ON b.user_id=u.id WHERE b.listing_id=%s ORDER BY b.amount DESC", (listing_id,))
    bids = cur.fetchall()
    return render_template('listing_detail.html', listing=listing, predicted_price=predicted, bids=bids)


@app.route('/place_bid', methods=['POST'])
def place_bid():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login required'})
    listing_id = request.form.get('listing_id')
    amount     = request.form.get('amount')
    if not listing_id or not amount:
        return jsonify({'success': False, 'message': 'Missing data'})
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO bids (listing_id,user_id,amount,created_at) VALUES (%s,%s,%s,%s)",
                (listing_id, session['user_id'], amount, datetime.now()))
    # Notify listing owner
    cur.execute("SELECT user_id FROM listings WHERE id=%s", (listing_id,))
    row = cur.fetchone()
    if row:
        create_notification(row['user_id'], f"New bid of ₹{amount}/kg on your listing!", 'bid')
    mysql.connection.commit()
    return jsonify({'success': True, 'message': f'Bid of ₹{amount}/kg placed!'})


# ══════════════════════════════════════════════════════════════
# BUY NOW
# ══════════════════════════════════════════════════════════════
@app.route('/buy_now', methods=['POST'])
def buy_now():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login required'})
    listing_id = request.form.get('listing_id')
    quantity   = float(request.form.get('quantity', 0))
    cur        = mysql.connection.cursor()
    cur.execute("SELECT * FROM listings WHERE id=%s", (listing_id,))
    listing = cur.fetchone()
    if not listing:
        return jsonify({'success': False, 'message': 'Listing not found'})
    if quantity > float(listing['quantity_kg']):
        return jsonify({'success': False, 'message': f"Only {listing['quantity_kg']} kg available"})
    total = float(listing['price_per_kg']) * quantity
    cur.execute(
        "INSERT INTO transactions (listing_id,buyer_id,seller_id,quantity_kg,total_amount,status,created_at) VALUES (%s,%s,%s,%s,%s,'completed',%s)",
        (listing_id, session['user_id'], listing['user_id'], quantity, total, datetime.now())
    )
    remaining = float(listing['quantity_kg']) - quantity
    if remaining <= 0:
        cur.execute("UPDATE listings SET status='sold' WHERE id=%s", (listing_id,))
    else:
        cur.execute("UPDATE listings SET quantity_kg=%s WHERE id=%s", (remaining, listing_id))
    # ← NOTIFICATION to seller
    create_notification(listing['user_id'],
        f"🛒 {session['user_name']} bought {quantity}kg of {listing['crop_name']} — ₹{total:.0f} earned!", 'sale')
    mysql.connection.commit()
    return jsonify({'success': True, 'message': f'Purchase successful! Total: ₹{total:.2f}', 'total': total})


# ══════════════════════════════════════════════════════════════
# EQUIPMENT RENTAL
# ══════════════════════════════════════════════════════════════
@app.route('/equipment')
def equipment():
    cur = mysql.connection.cursor()
    cur.execute("SELECT e.*,u.name AS owner_name,u.phone,u.location FROM equipment e JOIN users u ON e.owner_id=u.id WHERE e.availability_status='available' ORDER BY e.id DESC")
    return render_template('equipment.html', equipments=cur.fetchall())


@app.route('/add_equipment', methods=['GET', 'POST'])
def add_equipment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO equipment (owner_id,name,eq_type,rate_per_hr,location,description,availability_status,created_at) VALUES (%s,%s,%s,%s,%s,%s,'available',%s)",
            (session['user_id'], request.form['name'], request.form['eq_type'],
             request.form['rate_per_hr'], request.form['location'],
             request.form.get('description',''), datetime.now())
        )
        mysql.connection.commit()
        flash('Equipment listed successfully!', 'success')
        return redirect(url_for('equipment'))
    return render_template('add_equipment.html')


@app.route('/rent_equipment', methods=['POST'])
def rent_equipment():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login required'})
    equipment_id = request.form.get('equipment_id')
    hours        = int(request.form.get('hours', 1))
    rental_date  = request.form.get('rental_date')
    cur          = mysql.connection.cursor()
    cur.execute("SELECT * FROM equipment WHERE id=%s", (equipment_id,))
    eq = cur.fetchone()
    if not eq:
        return jsonify({'success': False, 'message': 'Equipment not found'})
    total_cost = float(eq['rate_per_hr']) * hours
    cur.execute(
        "INSERT INTO rentals (equipment_id,renter_id,rental_date,hours,total_cost,status,created_at) VALUES (%s,%s,%s,%s,%s,'confirmed',%s)",
        (equipment_id, session['user_id'], rental_date, hours, total_cost, datetime.now())
    )
    cur.execute("UPDATE equipment SET availability_status='rented' WHERE id=%s", (equipment_id,))
    # ← NOTIFICATION to equipment owner
    create_notification(eq['owner_id'],
        f"🚜 {session['user_name']} rented your {eq['name']} for {hours}hr on {rental_date} — ₹{total_cost:.0f}", 'sale')
    mysql.connection.commit()
    return jsonify({'success': True, 'message': f'Booking confirmed! Total: ₹{total_cost:.2f}', 'cost': total_cost})


# ══════════════════════════════════════════════════════════════
# CRM MACHINES
# ══════════════════════════════════════════════════════════════
@app.route('/crm_machines')
def crm_machines():
    cur = mysql.connection.cursor()
    cur.execute("SELECT c.*,u.name AS owner_name,u.phone,u.location FROM crm_machines c JOIN users u ON c.owner_id=u.id WHERE c.availability_status='available' ORDER BY c.id DESC")
    return render_template('crm_machines.html', crm_machines=cur.fetchall())


@app.route('/add_crm', methods=['GET', 'POST'])
def add_crm():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO crm_machines (owner_id,name,crm_type,rate_per_acre,rate_per_hr,location,description,suitable_crops,availability_status,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'available',%s)",
            (session['user_id'], request.form['name'], request.form['crm_type'],
             request.form['rate_per_acre'], request.form.get('rate_per_hr', 0),
             request.form['location'], request.form.get('description',''),
             request.form.get('suitable_crops',''), datetime.now())
        )
        mysql.connection.commit()
        flash('CRM machine listed!', 'success')
        return redirect(url_for('crm_machines'))
    return render_template('add_crm.html')


@app.route('/book_crm', methods=['POST'])
def book_crm():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Login required'})
    crm_id = request.form.get('crm_id')
    acres  = float(request.form.get('acres', 0))
    date   = request.form.get('booking_date')
    cur    = mysql.connection.cursor()
    cur.execute("SELECT c.*,u.name AS owner_name FROM crm_machines c JOIN users u ON c.owner_id=u.id WHERE c.id=%s", (crm_id,))
    m = cur.fetchone()
    if not m:
        return jsonify({'success': False, 'message': 'Machine not found'})
    total = float(m['rate_per_acre']) * acres
    cur.execute(
        "INSERT INTO crm_bookings (crm_id,booker_id,booking_date,acres,total_cost,status,created_at) VALUES (%s,%s,%s,%s,%s,'confirmed',%s)",
        (crm_id, session['user_id'], date, acres, total, datetime.now())
    )
    # ← NOTIFICATION to CRM owner
    create_notification(m['owner_id'],
        f"♻️ {session['user_name']} booked your {m['name']} for {acres} acres on {date} — ₹{total:.0f}", 'crm')
    mysql.connection.commit()
    return jsonify({'success': True, 'message': f'CRM booked! Total: ₹{total:.2f}'})


# ══════════════════════════════════════════════════════════════
# AI TOOLS
# ══════════════════════════════════════════════════════════════
@app.route('/ai_tools')
def ai_tools():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('ai_tools.html')


@app.route('/api/predict_price', methods=['POST'])
def api_predict_price():
    data = request.get_json(silent=True) or {}
    try:
        r = _predict_price(data.get('crop', 'Tomato'))
        return jsonify({k: float(v) if isinstance(v, (int, float)) else v for k, v in r.items()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/crop_advice', methods=['POST'])
def api_crop_advice():
    data = request.get_json(silent=True) or {}
    try:
        r = _get_crop_advice(data.get('location',''), data.get('season','kharif'), data.get('soil_type','loamy'))
        return jsonify({'recommended_crops': r.get('recommended_crops',[]), 'soil_tip': r.get('soil_tip',''),
                        'watering_advice': r.get('watering_advice',''), 'fertilizer_tip': r.get('fertilizer_tip',''),
                        'expected_yield': r.get('expected_yield',''), 'season': r.get('season','')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/grade_quality', methods=['POST'])
def api_grade_quality():
    data = request.get_json(silent=True) or {}
    try:
        r = _grade_crop_quality(data.get('crop',''), data.get('params',{}))
        return jsonify({'grade': r.get('grade','B'), 'grade_label': r.get('grade_label',''), 'score': r.get('score',70),
                        'color': r.get('color','#f0a500'), 'price_multiplier': float(r.get('price_multiplier',1.0)),
                        'price_impact': r.get('price_impact','0%'), 'recommendations': r.get('recommendations',[]),
                        'parameters_analyzed': r.get('parameters_analyzed',[])})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/match_schemes', methods=['POST'])
def api_match_schemes():
    data = request.get_json(silent=True) or {}
    try:
        schemes = _match_schemes(data.get('state',''), data.get('crop',''),
                                  float(data.get('land_size',0)), data.get('category','General'))
        return jsonify({'schemes': schemes, 'count': len(schemes)})
    except Exception as e:
        return jsonify({'error': str(e), 'schemes': []}), 500


# ══════════════════════════════════════════════════════════════
# NLP CHATBOT
# ══════════════════════════════════════════════════════════════
@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    data       = request.get_json(silent=True) or {}
    message    = data.get('message', '').strip()
    session_id = str(session.get('user_id', 'guest'))
    if not message:
        return jsonify({'response': 'Please type a farming question! 🌾'})
    try:
        response = _chatbot_response(message, session_id)
    except Exception:
        response = '🌾 I can help with crop prices, schemes, weather, equipment and more. What do you need?'
    return jsonify({'response': response})


# ══════════════════════════════════════════════════════════════
# NOTIFICATIONS API
# ══════════════════════════════════════════════════════════════
@app.route('/api/notifications')
def api_notifications():
    if 'user_id' not in session:
        return jsonify({'notifications': []})
    limit = int(request.args.get('limit', 20))
    cur   = mysql.connection.cursor()
    cur.execute("SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT %s",
                (session['user_id'], limit))
    notifs = cur.fetchall()
    for n in notifs:
        if n.get('created_at'):
            n['created_at'] = str(n['created_at'])
    return jsonify({'notifications': notifs})


@app.route('/api/notifications/<int:nid>/read', methods=['POST'])
def mark_notif_read(nid):
    if 'user_id' not in session:
        return jsonify({'success': False})
    cur = mysql.connection.cursor()
    cur.execute("UPDATE notifications SET is_read=1 WHERE id=%s AND user_id=%s", (nid, session['user_id']))
    mysql.connection.commit()
    return jsonify({'success': True})


@app.route('/api/notifications/read_all', methods=['POST'])
def mark_all_read():
    if 'user_id' not in session:
        return jsonify({'success': False})
    cur = mysql.connection.cursor()
    cur.execute("UPDATE notifications SET is_read=1 WHERE user_id=%s", (session['user_id'],))
    mysql.connection.commit()
    return jsonify({'success': True})


# ══════════════════════════════════════════════════════════════
# MAP USERS API
# ══════════════════════════════════════════════════════════════
@app.route('/api/map_users')
def api_map_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id,name,role,location,gps_lat AS lat,gps_lng AS lng FROM users WHERE gps_lat IS NOT NULL")
    users = cur.fetchall()
    safe  = [{'id':u['id'],'name':u['name'],'role':u['role'],'location':u['location'],
               'lat':float(u['lat']),'lng':float(u['lng'])} for u in users]
    return jsonify({'users': safe})


# ══════════════════════════════════════════════════════════════
# DASHBOARD CHARTS API
# ══════════════════════════════════════════════════════════════
@app.route('/api/stats')
def api_stats():
    cur = mysql.connection.cursor()
    cur.execute("SELECT crop_name,AVG(price_per_kg) AS avg_price FROM listings GROUP BY crop_name ORDER BY avg_price DESC LIMIT 8")
    prices = [{'crop_name':r['crop_name'],'avg_price':float(r['avg_price'])} for r in cur.fetchall()]
    cur.execute("SELECT DATE(created_at) AS date,COUNT(*) AS count FROM transactions GROUP BY DATE(created_at) ORDER BY date DESC LIMIT 7")
    txn = [{'date':str(r['date']),'count':r['count']} for r in cur.fetchall()]
    return jsonify({'crop_prices': prices, 'daily_transactions': txn})


# ══════════════════════════════════════════════════════════════
# MY LISTINGS
# ══════════════════════════════════════════════════════════════
@app.route('/my_listings')
def my_listings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM listings WHERE user_id=%s ORDER BY created_at DESC", (session['user_id'],))
    listings = cur.fetchall()
    cur.execute("SELECT t.*,l.crop_name FROM transactions t JOIN listings l ON t.listing_id=l.id WHERE t.buyer_id=%s OR t.seller_id=%s ORDER BY t.created_at DESC",
                (session['user_id'], session['user_id']))
    transactions = cur.fetchall()
    return render_template('my_listings.html', listings=listings, transactions=transactions)


# ══════════════════════════════════════════════════════════════
# GOVT DASHBOARD
# ══════════════════════════════════════════════════════════════
@app.route('/govt_dashboard')
def govt_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('user_role') != 'govt':
        flash('Access restricted to government accounts only.', 'danger')
        return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT crop_name,SUM(quantity_kg) AS total_qty,AVG(price_per_kg) AS avg_price,COUNT(*) AS listings FROM listings GROUP BY crop_name ORDER BY total_qty DESC LIMIT 10")
    crop_stats = cur.fetchall()
    cur.execute("SELECT u.location,COUNT(l.id) AS listings FROM listings l JOIN users u ON l.user_id=u.id GROUP BY u.location")
    location_stats = cur.fetchall()
    return render_template('govt_dashboard.html', crop_stats=crop_stats, location_stats=location_stats)


# ══════════════════════════════════════════════════════════════
# EXTRA PAGES
# ══════════════════════════════════════════════════════════════
@app.route('/distance_map')
def distance_map():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('distance_map.html')

@app.route('/weather_page')
def weather_page():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('weather_page.html')

@app.route('/notifications_page')
def notifications_page():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('notifications_page.html')


# ══════════════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)