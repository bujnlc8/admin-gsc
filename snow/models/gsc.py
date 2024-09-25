from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, TEXT
from snow.ext import db


class Gsc(db.Model):
    __tablename__ = 'gsc'

    id_ = db.Column('id', INTEGER(display_width=11), nullable=False, primary_key=True, doc='')
    work_title = db.Column(
        'work_title', VARCHAR(charset='utf8mb4', collation='utf8mb4_bin', length=512), nullable=False, doc=''
    )
    work_author = db.Column(
        'work_author', VARCHAR(charset='utf8mb4', collation='utf8mb4_bin', length=512), nullable=False, doc=''
    )
    work_dynasty = db.Column(
        'work_dynasty', VARCHAR(charset='utf8mb4', collation='utf8mb4_bin', length=32), nullable=False, doc=''
    )
    content = db.Column('content', TEXT(charset='utf8mb4', collation='utf8mb4_bin'), nullable=False, doc='')
    translation = db.Column('translation', TEXT(charset='utf8mb4', collation='utf8mb4_bin'), nullable=False, doc='')
    intro = db.Column('intro', TEXT(charset='utf8mb4', collation='utf8mb4_bin'), nullable=False, doc='')
    baidu_wiki = db.Column('baidu_wiki', VARCHAR(charset='utf8', length=256), nullable=True, doc='')
    audio_id = db.Column('audio_id', INTEGER(display_width=11), nullable=False, doc='')
    foreword = db.Column('foreword', TEXT(charset='utf8mb4', collation='utf8mb4_bin'), nullable=False, doc='')
    annotation_ = db.Column('annotation_', TEXT(charset='utf8mb4', collation='utf8mb4_bin'), nullable=False, doc='')
    appreciation = db.Column('appreciation', TEXT(charset='utf8mb4', collation='utf8mb4_bin'), nullable=True, doc='')
    master_comment = db.Column(
        'master_comment', TEXT(charset='utf8mb4', collation='utf8mb4_bin'), nullable=True, doc=''
    )
    layout = db.Column('layout', VARCHAR(charset='utf8', length=10), nullable=True, doc='')


db.Index('idx_work_audio_id', Gsc.audio_id, unique=False)
db.Index('idx_layout', Gsc.layout, unique=False)
