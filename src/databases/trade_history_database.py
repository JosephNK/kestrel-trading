from typing import List
from sqlalchemy.orm import Session

from src.databases.entity.trade_history_entity import TradeHistoryEntity
from src.models.trading_dto import TradingDto


class TradeHistoryDatabase:

    def __init__(self):
        print("TradeHistoryDatabase Init")

    def create(self, db: Session, dto: TradingDto) -> TradeHistoryEntity:
        try:
            base_currency, target_currency = dto.ticker.split("-")

            entity = TradeHistoryEntity(
                name=target_currency,
                unit=base_currency,
                decision=dto.decision,
                reason=dto.reason,
                trading_volume=dto.trading_volume,
                trading_unit_price=dto.trading_unit_price,
                trading_price=dto.trading_price,
                total_tokens=dto.total_tokens,
                prompt_tokens=dto.prompt_tokens,
                completion_tokens=dto.completion_tokens,
                total_token_cost=dto.total_token_cost,
                exchange_provider=dto.exchange_provider,
            )

            db.add(entity)
            db.commit()
            db.refresh(entity)

            return entity
        except:
            raise

    def get_all(self, db: Session) -> List[TradeHistoryEntity]:
        try:
            return db.query(TradeHistoryEntity).all()
        except:
            raise

    def get_one_by_id(self, db: Session, id: str) -> TradeHistoryEntity:
        try:
            return db.query(TradeHistoryEntity).filter_by(id=id).one()
        except:
            raise

    def get_last_one(self, db: Session) -> TradeHistoryEntity:
        try:
            return (
                db.query(TradeHistoryEntity)
                .order_by(TradeHistoryEntity.id.desc())
                .first()
            )
        except:
            raise

    # def update(self, db: Session, dto: TemplateRequestUpdateDto) -> TradeHistoryEntity:
    #     try:
    #         query = {Template.domain: dto.domain, Template.content: dto.content}
    #         db.query(TradeHistoryEntity).filter_by(id=dto.id).update(query)
    #         db.commit()
    #         return db.query(TradeHistoryEntity).filter_by(id=dto.id).one()
    #     except:
    #         raise

    def delete_one_by_id(self, db: Session, id: str) -> bool:
        try:
            entity = db.query(TradeHistoryEntity).filter_by(id=id).all()
            if not entity:
                return False
            db.query(TradeHistoryEntity).filter_by(id=id).delete()
            db.commit()
            return True
        except:
            raise
