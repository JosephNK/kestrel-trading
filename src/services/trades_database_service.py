from typing import List
from sqlalchemy.orm import Session

from src.databases.entity.trades_entity import Trades


class TradesDatabaseService:

    def __init__(self):
        print("TradesDatabaseService Init")

    # def create(self, db: Session, dto: Trades) -> Trades:
    #     try:
    #         entity = Trades(domain=dto.domain, content=dto.content)
    #         db.add(entity)
    #         db.commit()
    #         db.refresh(entity)
    #         return entity
    #     except:
    #         raise

    def get_all(self, db: Session) -> List[Trades]:
        try:
            return db.query(Trades).all()
        except:
            raise

    def get_one_by_id(self, db: Session, id: str) -> Trades:
        try:
            return db.query(Trades).filter_by(id=id).one()
        except:
            raise

    # def update(self, db: Session, dto: TemplateRequestUpdateDto) -> Template:
    #     try:
    #         query = {Template.domain: dto.domain, Template.content: dto.content}
    #         db.query(Trades).filter_by(id=dto.id).update(query)
    #         db.commit()
    #         return db.query(Trades).filter_by(id=dto.id).one()
    #     except:
    #         raise

    def delete_one_by_id(self, db: Session, id: str) -> bool:
        try:
            entity = db.query(Trades).filter_by(id=id).all()
            if not entity:
                return False
            db.query(Trades).filter_by(id=id).delete()
            db.commit()
            return True
        except:
            raise
