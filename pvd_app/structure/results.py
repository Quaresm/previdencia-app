from pvd_app import db
from pvd_app.structure.models import Users
import datetime

class Results(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))  
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    brute_income = db.Column(db.Integer)
    initial_application = db.Column(db.Integer)
    contributions_monthly = db.Column(db.Integer)
    date_retireday = db.Column(db.DateTime)
    spent_monthly = db.Column(db.Integer)
    validate_bank = db.Column(db.Boolean)
    application_type = db.Column(db.String(30))
    method = db.Column(db.String(10))

    def register_results(self, email, brute_income, initial_application,
                        contributions_monthly, date_retireday, spent_monthly,
                        validate_bank, application_type, method):
        
        users = Users()
        user_info = users.get_user(email)
        
        if user_info:
            new_result = Results(email=email, brute_income=brute_income, initial_application=initial_application,
                                contributions_monthly=contributions_monthly, date_retireday=date_retireday,
                                spent_monthly=spent_monthly, validate_bank=validate_bank, application_type=application_type,
                                method=method)

            db.session.add(new_result)
            db.session.commit()
    
    def search_results(self, email):
        return Results.query.filter_by(email=email).all()