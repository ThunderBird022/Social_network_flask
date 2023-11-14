from flask import jsonify, request
from models import User, Post, PostLike
from extensions import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import datetime
from sqlalchemy import func

def register_routes(app):
    @app.route('/signup', methods=['POST'])
    def signup():
        data = request.get_json()
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already taken'}), 400

        try:
            user = User(username=data['username'])
            user.set_password(data['password'])
            db.session.add(user)
            db.session.commit()
            return jsonify({'message': 'User created successfully'}), 201
        except Exception as e:
            db.session.rollback()  
            return jsonify({'error': str(e)}), 500


    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            token = create_access_token(identity=data['username'])
            user.last_login = datetime.utcnow()
            db.session.commit()
            return jsonify({'token': token}), 200
        return jsonify({'message': 'Invalid username or password'}), 401
    
    @app.route('/protected', methods=['GET'])
    @jwt_required()
    def protected():
        current_user = get_jwt_identity()
        return jsonify(logged_in_as=current_user), 200

    @app.route('/post', methods=['POST'])
    @jwt_required()
    def create_post():
        user_id = get_jwt_identity()
        content = request.json.get('content')
        if not content:
            return jsonify({"message": "Content is required"}), 400

        post = Post(content=content, user_id=user_id)
        db.session.add(post)
        db.session.commit()
        return jsonify({"message": "Post created", "post_id": post.id}), 201
    
    @app.route('/like_post', methods=['POST'])
    @jwt_required()
    def like_post():
        user_id = get_jwt_identity()
        post_id = request.json.get('post_id')
        
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "Post not found"}), 404

        if PostLike.query.filter_by(user_id=user_id, post_id=post_id).first():
            return jsonify({"message": "Post already liked"}), 400

        new_like = PostLike(user_id=user_id, post_id=post_id)
        post.like_count += 1

        db.session.add(new_like)
        db.session.commit()
        return jsonify({"message": "Post liked", "like_count": post.like_count}), 200

    @app.route('/unlike_post', methods=['POST'])
    @jwt_required()
    def unlike_post():
        user_id = get_jwt_identity()
        post_id = request.json.get('post_id')

        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "Post not found"}), 404

        post_like = PostLike.query.filter_by(user_id=user_id, post_id=post_id).first()
        if not post_like:
            return jsonify({"message": "Post not liked yet"}), 400

        post.like_count -= 1

        db.session.delete(post_like)
        db.session.commit()
        return jsonify({"message": "Post unliked", "like_count": post.like_count}), 200

    @app.route('/api/analytics/', methods=['GET'])
    def analytics():
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

        # Making query
        likes = db.session.query(func.date(PostLike.timestamp).label('day'),func.count('*').label('likes')
        ).filter(
            PostLike.timestamp >= date_from,
            PostLike.timestamp <= date_to
        ).group_by(
            func.date(PostLike.timestamp)
        ).all()
        print(likes)

        return jsonify({'analytics': f'{likes}'}) 

    @app.route('/user_activity/<username>', methods=['GET'])
    def user_activity(username):
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "username": username,
            "last_login": user.last_login.isoformat() if user.last_login else "Never logged in",
            "last_request": user.last_request.isoformat() if user.last_request else "No recorded requests"
        }), 200

    @app.before_request
    def before_request():
        if request.endpoint in ['login', 'signup']:
            return

        try:
            verify_jwt_in_request()
            user_identity = get_jwt_identity()
            user = User.query.filter_by(username=user_identity).first()
            if user:
                user.last_request = datetime.utcnow()
                db.session.commit()
        except Exception as e:
            pass 



