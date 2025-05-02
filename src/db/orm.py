import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Balance(Base):
    __tablename__ = "balances"
    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    address = sa.Column(sa.String(), index=True)
    token_id = sa.Column(sa.String(), index=True)
    amount = sa.Column(sa.Numeric(60, 0))

    __table_args__ = (
        sa.UniqueConstraint("address", "token_id", name="token_id_address_uq"),
    )
