import uuid
from app import db
from datetime import datetime, timezone

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    meme = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    delete_token = db.Column(db.String(36), nullable=False, default=lambda: str(uuid.uuid4()))
    click = db.Column(db.Integer(),default = 0,server_default="0")
    category = db.Column(db.String(100),nullable = True)

    @property
    def formatted_date(self):
        if self.date_created:
            return self.date_created.strftime('%B %Y')
        return ""