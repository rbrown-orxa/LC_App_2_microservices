import psycopg2
import logging
import time
import random
from flask import current_app



def check_subscription(email, subscription_id):
    if not current_app.config['APPLY_BILLING']:
        return # Check has passed
    if subscription_id:
        if not current_app.config['SUBSCRIPTION_VALID']:
            assert False, '402 Subscription not valid'
        return # Check has passed
    assert email, '401 Either email or subscription_id must be provided '

    free_queries_so_far =  get_unbillable_queries(
        current_app.config['BILLING_DB_CONN_STR'],
        email = email)
    logging.info('Free queries used so far: ' + str(free_queries_so_far) + \
        ' by user: ' + str(email))

    assert free_queries_so_far < current_app.config['MAX_FREE_CALLS'], \
        '402 Free quota query limits exceeded for user'

    logging.info('Subscription check passed')
    return


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
                            started TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                            success BOOLEAN NOT NULL DEFAULT FALSE,
                            email citext,
                            subscription_id UUID,
                            completed TIMESTAMPTZ,
                            billed BOOLEAN NOT NULL DEFAULT FALSE,
                            date_billed TIMESTAMPTZ
                        CHECK (
                            email IS NOT NULL
                            OR subscription_id IS NOT NULL)
                        ) ;
                        
                        CREATE TABLE
                        IF NOT EXISTS bills (
                            id SERIAL PRIMARY KEY,
                            subscription_id UUID NOT NULL,
                            units INT NOT NULL,
                            created TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        ) ;
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







# def register_billed_quantities(conn_str, units_billed):
#     """
#     Example units_billed dict:

#     { 'cef06856-837b-4661-a627-6b20fd268a5c': 4,
#       '61337278-ae07-4ef9-95d0-2791243e2283': 8 }
#     """

#     SQL =   """
#             UPDATE billing
#             SET total_billed_queries = total_billed_queries + %s
#             WHERE subscription_id = %s
#             """

#     with psycopg2.connect(conn_str) as conn:
#         cur = conn.cursor()
#         for subscription_id, units in units_billed.items():
#             cur.execute( SQL, (units, subscription_id) )
#             conn.commit()
#         cur.close()


# def get_unbillable_queries(conn_str, email=''):

#     if email:
#         SQL =   """
#                 SELECT count(*) 
#                 FROM queries 
#                 WHERE email = %s 
#                 AND success = True 
#                 AND subscription_id IS NULL;
#                 """
#         with psycopg2.connect(conn_str) as conn:
#             cur = conn.cursor()
#             cur.execute( SQL, (email, ) )
#             rv = cur.fetchone()[0]
#             cur.close()
#         return rv


def register_query_started(email='', subscription_id=None):
    
    if not current_app.config['APPLY_BILLING']:
        return None

    conn_str = current_app.config['BILLING_DB_CONN_STR']
    logging.info('Registering query started')
    
    SQL =  """
            INSERT INTO queries
            (email, subscription_id)
            VALUES (%s, %s) 
            RETURNING id;
            """

    with psycopg2.connect(conn_str) as conn:
        cur = conn.cursor()
        cur.execute( SQL, (email, subscription_id) )
        conn.commit()
        id = cur.fetchone()[0]
        cur.close()

    logging.info(f'Got query id: {id}')

    return id


def register_query_successful(query_id):

    if not current_app.config['APPLY_BILLING']:
        return

    conn_str = current_app.config['BILLING_DB_CONN_STR']
    logging.info('Registering successful query')
    
    SQL1 =  """
            UPDATE queries
            SET 
            success = true,
            completed = NOW()
            WHERE id = %s 
            -- RETURNING subscription_id 
            ;
            """


    # SQL2 =  """
    #         INSERT INTO billing (subscription_id)
    #         VALUES (%s)
    #         ON CONFLICT (subscription_id) DO
    #         UPDATE SET
    #         total_successful_queries = 1 + billing.total_successful_queries
    #         ;
    #         """


    with psycopg2.connect(conn_str) as conn:
        cur = conn.cursor()
        cur.execute( SQL1, (query_id, ) )
        conn.commit()
        # subscription_id = cur.fetchone()[0]

        # if subscription_id:
        #     logging.info(   f'Registering query: {query_id} ' \
        #                     + f'for billing: {subscription_id}')
        #     cur.execute( SQL2, (subscription_id, ) )
        #     conn.commit()
        cur.close()




if __name__ == '__main__':
    class CurrentApp():
        pass

    current_app = CurrentApp
    current_app.config = {}

    logging.basicConfig(level=logging.DEBUG)
    
    current_app.config['APPLY_BILLING'] = True
    current_app.config['BILLING_DB_CONN_STR'] = \
        'postgres://postgres:password@localhost:5432/postgres'

    make_tables(current_app.config['BILLING_DB_CONN_STR'])

    id1 = register_query_started(email='foo@foo.com')
    time.sleep(random.random()/2)
    register_query_successful(id1)

    id2 = register_query_started(
            subscription_id='CEF06856-837B-4661-A627-6B20FD268A5C')
    time.sleep(random.random()/2)
    register_query_successful(id2)

    id2 = register_query_started(
            subscription_id='CEF06856-837B-4661-A627-6B20FD268A5C')
    time.sleep(random.random()/2)
    register_query_successful(id2)

    id3 = register_query_started(email='foo1@foo2.com',
            subscription_id='61337278-AE07-4EF9-95D0-2791243E2283')
    time.sleep(random.random()/2)

    id4 = register_query_started(
            subscription_id='2EF06856-837B-4661-A627-6B20FD268A5B')
    time.sleep(random.random()/2)
    register_query_successful(id4)


    # bill = get_billing_quantities(current_app.config['BILLING_DB_CONN_STR'])
    # print(f'Unbilled units: {bill}')

    # time.sleep(random.random()) # simulate API billing request being sent

    # register_billed_quantities(current_app.config['BILLING_DB_CONN_STR'], bill)



