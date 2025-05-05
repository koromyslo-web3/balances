from time import time

from fastapi import Body, Depends, FastAPI, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, model_validator
from web3.auto import w3

from .config import DEBUG, AUTH_JWT_ALGO, AUTH_JWT_PUBLIC_B64
from .api import balances

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def authenticate(token_str: str = Depends(oauth2_scheme)):
    if not token_str:
        raise HTTPException(401)
    try:
        decoded = jwt.decode(token_str, AUTH_JWT_PUBLIC_B64, algorithms=[AUTH_JWT_ALGO])
    except JWTError:
        raise HTTPException(401)

    return decoded


docs = dict(docs_url=None, redoc_url=None, openapi_url=None) if not DEBUG else {}
app = FastAPI(**docs)


class UpdateRequest(BaseModel):
    address: str
    delta: int | str
    token_id: str

    @model_validator(mode="after")
    def validate(self):
        try:
            self.address = w3.to_checksum_address(self.address)
            self.delta = int(self.delta)
            self.token_id = str(self.token_id)
            return self
        except Exception as e:
            raise ValueError(e)


class BalancesResponse(BaseModel):
    token_id: str
    address: str
    amount: str


@app.post("/", response_model=BalancesResponse)
async def update(data: UpdateRequest = Body(), service: str = Depends(authenticate)):
    return await balances.update_balance(data.address, data.token_id, data.delta)


@app.post("/bulk", response_model=list[BalancesResponse])
async def update_bulk(
    data: list[UpdateRequest] = Body(), service: str = Depends(authenticate)
):
    return await balances.update_balance_bulk(*[row.model_dump() for row in data])


@app.get("/", response_model=list[BalancesResponse])
async def get(address: str = Query(), service: str = Depends(authenticate)):
    return await balances.get_balances(address)
