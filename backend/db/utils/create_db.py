from db.base import Base
from db.session import engine
import models.user
import models.product
import models.cart
import models.cartitem
import models.order
import models.orderitem

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("Database tables created!")