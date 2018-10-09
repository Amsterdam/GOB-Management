from api.storage import db

# Models
class Log(db.Model):
    __tablename__ = 'logs'

    logid = db.Column(db.Integer, primary_key=True)
    msg = db.Column(db.String)

    def __repr__(self):
        return f'<Msg {self.msg}>'
