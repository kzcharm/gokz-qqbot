from typing import Generator, Annotated

from nonebot.internal.params import Depends
from sqlmodel import Session

from ..database.db import engine


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
