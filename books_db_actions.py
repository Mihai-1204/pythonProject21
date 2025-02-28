import os
import psycopg2 as ps
from psycopg2 import OperationalError
from init_config import config


def get_data(sql_query: str, db_config: dict, params=None, return_as_dict: bool = True):
    try:
        with ps.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_query, params)
                data = cursor.fetchall()
                if return_as_dict:
                    columns = [desc.name for desc in cursor.description]
                    items_list = [dict(zip(columns, item)) for item in data]
                    return items_list
                else:
                    return data
    except OperationalError as e:
        print(f"The database config data is wrong: {e}")
    except Exception as e:
        print(f"Exception here: {e}")
    return []


def insert_row(sql_query: str, params, db_config: dict):
    try:
        with ps.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_query, params)
                conn.commit()  #
                print("Row was added")
    except Exception as e:
        print(f"Exception was raised: {e}")


def delete_row(name: str, db_config: dict, table_name: str = "book"):
    try:
        query = f"DELETE FROM public.{table_name} WHERE \"name\" = %s"
        with ps.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (name,))
                conn.commit()
                print(f"Successfully deleted row from table: {table_name}, name: {name}")
    except Exception as e:
        print(f"Failed to delete the instance {name}: {e}")


if __name__ == '__main__':
    sql_query = "insert into book(\"name\", number_of_sales, reviews, author_id) values('Harry Potter7', 200000, 9, 1)"
    database_config = config.get("database_config")
    database_config['password'] = os.environ['dbeaver_pass']

    if database_config:
        delete_row("Harry Potter3", database_config)
        query = "select * from public.book"
        response = get_data(query, database_config)
        print(response)
    else:
        print("No database configuration found")
