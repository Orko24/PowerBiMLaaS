

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd
from sqlalchemy import create_engine, text
from typing import List, Optional
from psycopg2.extras import execute_values

class CreateDatabase:

    def __init__(
            self, db_name="mlapp", user="postgres", password="pass",
            host="localhost", port="5432"
    ):

        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port


    def create_database(
            self, db_name="mlapp", user="postgres", password="pass", host="localhost", port="5432"
    ):
        try:
            # Connect to default 'postgres' DB
            conn = psycopg2.connect(
                dbname="postgres",
                user=user,
                password=password,
                host=host,
                port=port
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
                exists = cur.fetchone()
                if not exists:
                    cur.execute(f"CREATE DATABASE {db_name};")
                    print(f"✅ Database '{db_name}' created.")
                else:
                    print(f"ℹ️ Database '{db_name}' already exists.")

            conn.close()

        except Exception as e:
            print(f"❌ Error: {e}")




    def create_database_if_missing(self):

        self.create_database(
            db_name= self.db_name, user= self.user, password= self.password, host= self.host, port= self.port
        )




class LoadToPostgres:
    """
    Enhanced version of your LoadToPostgres class.

    KEY IMPROVEMENTS (non-breaking):
    1. ✅ Auto-creates tables if they don't exist (fixes your main issue)
    2. ✅ Better error handling with proper exception propagation
    3. ✅ Added flexible insert vs upsert options
    4. ✅ Maintains all your original methods and interface
    5. ✅ Your existing code will work unchanged
    """

    def __init__(
            self, db_url: str,
            csv_path: str,
            table_name: str = "transactions"
    ):
        # UNCHANGED - same interface as your original
        self.db_url = db_url
        self.csv_path = csv_path
        self.table_name = table_name
        self.engine = create_engine(self.db_url)

    def load_csv(self) -> pd.DataFrame:
        """
        UNCHANGED from your original - same data preprocessing logic
        """
        df = pd.read_csv(self.csv_path)

        # Drop "Time" if it exists
        if "Time" in df.columns:
            df = df.drop(columns=["Time"])

        # Rename for DB schema compatibility
        if "Class" in df.columns:
            df = df.rename(columns={"Class": "label"})
        if "Amount" in df.columns:
            df = df.rename(columns={"Amount": "amount"})

        # Ensure 'label' and 'amount' are last for consistency
        non_target_cols = [col for col in df.columns if col not in ["label", "amount"]]
        ordered_columns = non_target_cols + [col for col in ["amount", "label"] if col in df.columns]
        df = df[ordered_columns]

        # Lowercase for SQL compatibility
        df.columns = [col.lower() for col in df.columns]
        return df

    def create_table_if_not_exists(self, df: pd.DataFrame):
        """
        NEW METHOD - This is what fixes your "relation does not exist" error
        Automatically creates tables based on DataFrame schema
        """
        with self.engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = :table_name
                );
            """), {"table_name": self.table_name})

            table_exists = result.scalar()

            if not table_exists:
                print(f"🔧 Creating table '{self.table_name}'...")

                # Map pandas dtypes to PostgreSQL types
                column_definitions = []
                for col in df.columns:
                    if df[col].dtype == 'int64':
                        col_type = 'BIGINT'
                    elif df[col].dtype in ['int32', 'int16', 'int8']:
                        col_type = 'INTEGER'
                    elif df[col].dtype in ['float64', 'float32']:
                        col_type = 'DOUBLE PRECISION'
                    elif df[col].dtype == 'bool':
                        col_type = 'BOOLEAN'
                    else:
                        col_type = 'TEXT'

                    column_definitions.append(f"{col} {col_type}")

                # Create table with auto-incrementing ID
                create_sql = f"""
                CREATE TABLE {self.table_name} (
                    id SERIAL PRIMARY KEY,
                    {', '.join(column_definitions)}
                );
                """

                conn.execute(text(create_sql))
                conn.commit()
                print(f"✅ Table '{self.table_name}' created successfully!")
            else:
                print(f"ℹ️ Table '{self.table_name}' already exists.")

    def insert_to_postgres(self, df: pd.DataFrame):
        """
        ENHANCED version of your original method
        - Adds automatic table creation
        - Better error handling
        - Same interface, so your existing code works unchanged
        """

        # NEW: Auto-create table if needed
        self.create_table_if_not_exists(df)

        # SAME logic as your original
        cols = ','.join(df.columns)
        insert_query = f"""
            INSERT INTO {self.table_name} ({cols})
            VALUES %s
        """

        values = [tuple(x) for x in df.to_numpy()]
        conn = self.engine.raw_connection()
        cursor = conn.cursor()

        try:
            execute_values(cursor, insert_query, values)
            conn.commit()
            print(f"✅ Successfully inserted {len(df)} rows into '{self.table_name}'")

        except Exception as e:
            conn.rollback()
            print(f"❌ Error during INSERT: {e}")
            raise  # IMPROVED: Properly propagate errors

        finally:
            cursor.close()
            conn.close()

    def upsert_to_postgres(self, df: pd.DataFrame, conflict_columns: Optional[List[str]] = None):
        """
        NEW METHOD - Provides upsert functionality when you need it
        Your original code doesn't need to change - this is just an additional option
        """

        self.create_table_if_not_exists(df)
        cols = ','.join(df.columns)

        if conflict_columns:
            conflict_target = ','.join(conflict_columns)
            update_set = ', '.join([f"{col} = EXCLUDED.{col}" for col in df.columns if col not in conflict_columns])

            upsert_query = f"""
                INSERT INTO {self.table_name} ({cols})
                VALUES %s
                ON CONFLICT ({conflict_target}) DO UPDATE
                SET {update_set}
            """
        else:
            # Fallback to simple insert
            upsert_query = f"""
                INSERT INTO {self.table_name} ({cols})
                VALUES %s
            """

        values = [tuple(x) for x in df.to_numpy()]
        conn = self.engine.raw_connection()
        cursor = conn.cursor()

        try:
            execute_values(cursor, upsert_query, values)
            conn.commit()
            print(f"✅ Successfully upserted {len(df)} rows into '{self.table_name}'")

        except Exception as e:
            conn.rollback()
            print(f"❌ Error during UPSERT: {e}")
            raise

        finally:
            cursor.close()
            conn.close()

    def run(self, use_upsert: bool = False, conflict_columns: Optional[List[str]] = None):
        """
        ENHANCED version of your original run() method
        - Your existing calls to run() will work exactly the same (backward compatible)
        - Added optional parameters for advanced functionality
        """
        try:
            df = self.load_csv()

            if use_upsert:
                self.upsert_to_postgres(df, conflict_columns)
            else:
                self.insert_to_postgres(df)  # Same as your original behavior

        except Exception as e:
            print(f"❌ Failed to load data: {e}")
            raise