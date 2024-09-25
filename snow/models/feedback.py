from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, DATETIME
from snow.ext import db


class Feedback(db.Model):
    __bind_key__ = 'challenge'

    __tablename__ = 'feedback'

    id_ = db.Column('id', INTEGER(display_width=11), nullable=False, primary_key=True, doc='')
    uid = db.Column('uid', INTEGER(display_width=11), nullable=False, doc='')
    question_id = db.Column('question_id', INTEGER(display_width=11), nullable=False, doc='')
    remark = db.Column(
        'remark', VARCHAR(charset='utf8mb4', collation='utf8mb4_bin', length=512), nullable=False, doc=''
    )
    nickname = db.Column(
        'nickname', VARCHAR(charset='utf8mb4', collation='utf8mb4_bin', length=100), nullable=False, doc=''
    )
    type_ = db.Column('type', INTEGER(display_width=1), nullable=False, doc='')
    status = db.Column('status', INTEGER(display_width=1), nullable=False, doc='')
    create_time = db.Column('create_time', DATETIME())
