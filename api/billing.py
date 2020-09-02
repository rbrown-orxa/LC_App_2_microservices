import psycopg2
import logging
import time


def make_tables(conn_str):
    success = False
    while not success:
        logging.info('Trying to make billing tables if not exist')
        try:
            with psycopg2.connect(conn_str) as conn:
                SQL =   """
                        CREATE EXTENSION IF NOT EXISTS citext;

                        CREATE TABLE
                        IF NOT EXISTS queries (
                        id SERIAL PRIMARY KEY,
                        created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        success BOOLEAN NOT NULL,
                        email citext,
                        subscription_id UUID,
                        CHECK (
                            email IS NOT NULL
                            OR subscription_id IS NOT NULL)
                        );

                        CREATE TABLE
                        IF NOT EXISTS billing (
                        subscription_id UUID PRIMARY KEY,
                        total_billed_queries INT NOT NULL DEFAULT 0 ) ;
                        """

                cur = conn.cursor()
                cur.execute(SQL)
                conn.commit()
                cur.close()

            logging.info('Success')
            success = True

        except Exception as err:
                logging.info(err)
                time.sleep(5)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    CONN_STR = 'postgres://postgres:password@localhost:5432/postgres'

    make_tables(CONN_STR)