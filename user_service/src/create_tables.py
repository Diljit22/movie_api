import logging

from user_api.database import Base, engine

logging.basicConfig(level=logging.INFO)


def main():
    logging.info("Creating database tables for user_service...")
    Base.metadata.create_all(bind=engine)
    logging.info("Database tables created successfully.")


if __name__ == "__main__":
    main()
