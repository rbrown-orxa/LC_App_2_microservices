import psycopg2
import logging
import time
import random
from flask import current_app

import subscription



def check_subscription(object_id):

    if not current_app.config['APPLY_BILLING']:
        return '' # Check has passed, but no subscription_id
    assert object_id, '401 User object id required'
    return subscription.check_user_subscribed(object_id)


def make_tables(conn_str):

    success = False
    while not success:
        logging.info('Trying to make billing tables if not exist')
        try:
            with psycopg2.connect(conn_str) as conn:
                SQL =   """
                        CREATE TABLE
                        IF NOT EXISTS queries (
                            id SERIAL PRIMARY KEY,
                            started TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                            success BOOLEAN NOT NULL DEFAULT FALSE,
                            subscription_id UUID,
                            completed TIMESTAMPTZ,
                            billed BOOLEAN NOT NULL DEFAULT FALSE,
                            date_billed TIMESTAMPTZ 
                        );
                        
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


def register_query_started(subscription_id):
    
    if not current_app.config['APPLY_BILLING']:
        # return None
        pass

    conn_str = current_app.config['BILLING_DB_CONN_STR']
    logging.info('Registering query started')
    
    SQL =  """
            INSERT INTO queries
            (subscription_id)
            VALUES (%s) 
            RETURNING id;
            """

    with psycopg2.connect(conn_str) as conn:
        cur = conn.cursor()
        cur.execute( SQL, (subscription_id, ) )
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

    with psycopg2.connect(conn_str) as conn:
        cur = conn.cursor()
        cur.execute( SQL1, (query_id, ) )
        conn.commit()
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


    id2 = register_query_started(
            subscription_id='CEF06856-837B-4661-A627-6B20FD268A5C')
    time.sleep(random.random()/2)
    register_query_successful(id2)

    id2 = register_query_started(
            subscription_id='CEF06856-837B-4661-A627-6B20FD268A5C')
    time.sleep(random.random()/2)
    register_query_successful(id2)

    id4 = register_query_started(
            subscription_id='2EF06856-837B-4661-A627-6B20FD268A5B')
    time.sleep(random.random()/2)
    register_query_successful(id4)


    # bill = get_billing_quantities(current_app.config['BILLING_DB_CONN_STR'])
    # print(f'Unbilled units: {bill}')

    # time.sleep(random.random()) # simulate API billing request being sent

    # register_billed_quantities(current_app.config['BILLING_DB_CONN_STR'], bill)



