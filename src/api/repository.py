from sqlalchemy import Numeric, select
from sqlalchemy.dialects.postgresql import insert

from ..db import UnitOfWork, orm


async def _update_balance(address, token_id, delta, *, session) -> Numeric:
    stmt = (
        insert(orm.Balance)
        .values(token_id=token_id, address=address, amount=delta)
        .on_conflict_do_update(
            "token_id_address_uq", set_={"amount": orm.Balance.amount + delta}
        )
        .returning(orm.Balance.amount)
    )
    q = await session.execute(stmt)
    return q.scalars().first()


async def update_balance(address, token_id, delta):
    async with UnitOfWork(autocommit=True) as session:
        balance = await _update_balance(address, token_id, delta, session=session)
        return {
            "token_id": token_id,
            "address": address,
            "amount": balance,
        }


async def update_balance_bulk(*args: list[dict]):
    results = []
    async with UnitOfWork(autocommit=True) as session:
        for row in args:
            balance = await _update_balance(
                row["address"], row["token_id"], row["delta"], session=session
            )
            results.append(
                {
                    "address": row["address"],
                    "token_id": row["token_id"],
                    "amount": balance,
                }
            )
    return results


async def get_balances(address) -> list[dict]:
    async with UnitOfWork() as session:
        stmt = select(orm.Balance.token_id, orm.Balance.amount).where(
            orm.Balance.address == address
        )
        q = await session.execute(stmt)
        return q.mappings().all()
