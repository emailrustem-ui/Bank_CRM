from app import app, db, User

with app.app_context():
    user = User.query.filter_by(username='manager').first()
    if not user:
        user = User(username='manager', full_name='Менеджер', is_enabled=True)
        db.session.add(user)
    user.set_password('manager')
    user.is_enabled = True
    db.session.commit()
    print("ГОТОВО! Логин: manager, Пароль: manager")
