"""init

Revision ID: 12c0b3a26d60
Revises: 
Create Date: 2025-05-02 17:50:59.707313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12c0b3a26d60'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('balances',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('address', sa.String(), nullable=True),
    sa.Column('token_id', sa.String(), nullable=True),
    sa.Column('amount', sa.Numeric(precision=60, scale=0), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('address', 'token_id', name='token_id_address_uq')
    )
    op.create_index(op.f('ix_balances_address'), 'balances', ['address'], unique=False)
    op.create_index(op.f('ix_balances_token_id'), 'balances', ['token_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_balances_token_id'), table_name='balances')
    op.drop_index(op.f('ix_balances_address'), table_name='balances')
    op.drop_table('balances')
    # ### end Alembic commands ###
