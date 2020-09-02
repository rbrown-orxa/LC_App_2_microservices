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
                            total_successful_queries INT NOT NULL DEFAULT 1,
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


def register_query(conn_str, email='', subscription_id=None, success=True):

    logging.info('Registering query for billing')
    if (not email) and (not subscription_id):
        raise ValueError('email or subscription_id field must be not null')
    
    SQL1 =  """
            INSERT INTO queries
            (email, subscription_id, success)
            VALUES (%s, %s, %s) ;
            """


    SQL2 =  """
            INSERT INTO billing (subscription_id)
            VALUES (%s)
            ON CONFLICT (subscription_id) DO
            UPDATE SET
            total_successful_queries = 1 + billing.total_successful_queries
            ;
            """


    with psycopg2.connect(conn_str) as conn:
        cur = conn.cursor()
        cur.execute( SQL1, (email, subscription_id, success) )
        if success and subscription_id:
            cur.execute( SQL2, (subscription_id, ) )
        conn.commit()
        cur.close()


def get_billing_quantities(conn_str):
    SQL =   """
            SELECT
            subscription_id,
            total_successful_queries - total_billed_queries
                AS queries_to_bill
            FROM billing
            GROUP BY subscription_id ;
            """

    with psycopg2.connect(conn_str) as conn:
        cur = conn.cursor()
        cur.execute( SQL )
        rv = cur.fetchall()
        cur.close()
    
    return dict(rv)


def register_billed_quantities(conn_str, units_billed):
    """
    Example units_billed dict:

    { 'cef06856-837b-4661-a627-6b20fd268a5c': 4,
      '61337278-ae07-4ef9-95d0-2791243e2283': 8 }
    """

    SQL =   """
            UPDATE billing
            SET total_billed_queries = total_billed_queries + %s
            WHERE subscription_id = %s
            """

    with psycopg2.connect(conn_str) as conn:
        cur = conn.cursor()
        for subscription_id, units in units_billed.items():
            cur.execute( SQL, (units, subscription_id) )
            conn.commit()
        cur.close()


def get_unbillable_queries(conn_str, email=''):

    if email:
        SQL =   """
                SELECT count(*) 
                FROM queries 
                WHERE email = %s 
                AND success = True 
                AND subscription_id IS NULL;
                """
        with psycopg2.connect(conn_str) as conn:
            cur = conn.cursor()
            cur.execute( SQL, (email, ) )
            rv = cur.fetchone()[0]
            cur.close()
        return rv



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    CONN_STR = 'postgres://postgres:password@localhost:5432/postgres'

    make_tables(CONN_STR)

    register_query(CONN_STR, email='foo@foo.com')
    register_query(CONN_STR, email='foo1@foo2.com', success=False)
    register_query(CONN_STR, subscription_id='CEF06856-837B-4661-A627-6B20FD268A5C')
    register_query(CONN_STR, subscription_id='61337278-AE07-4EF9-95D0-2791243E2283')
    register_query(CONN_STR, subscription_id='61337278-AE07-4EF9-95D0-2791243E2283')

    bill = get_billing_quantities(CONN_STR)
    print(f'Unbilled units: {bill}')

    register_billed_quantities(CONN_STR, bill)

    unbillable_single = get_unbillable_queries(CONN_STR, 'foo@foo.com')
    print(f'Unbillable units for foo@foo.com: {unbillable_single}')





