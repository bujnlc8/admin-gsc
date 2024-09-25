from typing import Self

from sqlalchemy.dialects.mysql import VARCHAR

from snow.ext import db


class Region(db.Model):
    __bind_key__ = 'challenge'

    __tablename__ = 'region'

    region_code = db.Column(
        'region_code',
        VARCHAR(charset='utf8mb4', collation='utf8mb4_bin', length=10),
        nullable=False,
        primary_key=True,
        doc='区划代码',
    )
    name = db.Column(
        'name', VARCHAR(charset='utf8mb4', collation='utf8mb4_bin', length=100), nullable=False, doc='区划名称'
    )
    discard_year = db.Column(
        'discard_year',
        VARCHAR(charset='utf8mb4', collation='utf8mb4_bin', length=10),
        nullable=True,
        doc='废止年份',
        server_default='""',
    )

    @classmethod
    def get_by_region_codes(cls, region_codes: list[str]) -> list[Self]:
        return cls.query.filter(cls.region_code.in_(region_codes)).order_by(cls.region_code).all()
