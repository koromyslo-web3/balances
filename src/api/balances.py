from . import repository


async def update_balance(address, token_id: str, delta: int | str):
    return await repository.update_balance(address, token_id, delta)


async def update_balance_bulk(*args: list[dict]):
    return await repository.update_balance_bulk(*args)


async def get_balances(address):
    return await repository.get_balances(address)
