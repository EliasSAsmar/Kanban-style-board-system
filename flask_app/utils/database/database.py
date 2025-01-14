import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow
from datetime import datetime

class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables         = ['users', 'boards', 'board_members', 'lists', 'cards']
        
        # NEW IN HW 3-----------------------------------------------------------------
        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }
        #-----------------------------------------------------------------------------

    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        ''' FILL ME IN WITH CODE THAT CREATES YOUR DATABASE TABLES.'''

        #should be in order or creation - this matters if you are using forign keys.
         
        if purge:
            for table in self.tables[::-1]:
                self.query(f"""DROP TABLE IF EXISTS {table}""")
            
        # Execute all SQL queries in the /database/create_tables directory.
        for table in self.tables:
            
            #Create each table using the .sql file in /database/create_tables directory.
            with open(data_path + f"create_tables/{table}.sql") as read_file:
                create_statement = read_file.read()
            self.query(create_statement)

            # Import the initial data
            try:
                params = []
                with open(data_path + f"initial_data/{table}.csv") as read_file:
                    scsv = read_file.read()            
                for row in csv.reader(StringIO(scsv), delimiter=','):
                    params.append(row)
            
                # Insert the data
                cols = params[0]; params = params[1:] 
                self.insertRows(table = table,  columns = cols, parameters = params)
            except:
                print('no initial data')

    # def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        
    #     # Check if there are multiple rows present in the parameters
    #     has_multiple_rows = any(isinstance(el, list) for el in parameters)
    #     keys, values      = ','.join(columns), ','.join(['%s' for x in columns])
        
    #     # Construct the query we will execute to insert the row(s)
    #     query = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """
    #     if has_multiple_rows:
    #         for p in parameters:
    #             query += f"""({values}),"""
    #         query     = query[:-1] 
    #         parameters = list(itertools.chain(*parameters))
    #     else:
    #         query += f"""({values}) """                      
        
    #     insert_id = self.query(query,parameters)[0]['LAST_INSERT_ID()']         
    #     return insert_id

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################

    def createUser(self, email='me@email.com', password='password', role='user'):
        # Hash the password using a secure hashing algorithm
        hashed_password = self.onewayEncrypt(password)

        query = """
        INSERT INTO users (email, password, role)
        VALUES (%s, %s, %s)

        """

        try:
            self.query(query, (email, hashed_password, role))
            return {'success': 1, 'message': 'User created successfully'}
        except mysql.connector.Error as e:
            return {'success': 0, 'message': f'Error creating user: {e}'}

    def authenticate(self, email='me@email.com', password='password'):
        query = "SELECT password FROM users WHERE email = %s"
        
        try:
            result = self.query(query, (email,))
            
            if not result:
                return {'success': 0, 'message': 'User not found'}
            
            # Retrieve the stored hashed password
            stored_hashed_password = result[0]['password']
            
            # Hash the provided password
            hashed_password = self.onewayEncrypt(password)
            
            # Compare the hashed passwords
            if hashed_password == stored_hashed_password:
                return {'success': 1, 'message': 'Authentication successful'}
            else:
                return {'success': 0, 'message': 'Incorrect password'}
        
        except mysql.connector.Error as e:
            return {'success': 0, 'message': f'Error during authentication: {e}'}

    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string


    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message
    def about(self, nested=False):    
        query = """select concat(col.table_schema, '.', col.table_name) as 'table',
                          col.column_name                               as column_name,
                          col.column_key                                as is_key,
                          col.column_comment                            as column_comment,
                          kcu.referenced_column_name                    as fk_column_name,
                          kcu.referenced_table_name                     as fk_table_name
                    from information_schema.columns col
                    join information_schema.tables tab on col.table_schema = tab.table_schema and col.table_name = tab.table_name
                    left join information_schema.key_column_usage kcu on col.table_schema = kcu.table_schema
                                                                     and col.table_name = kcu.table_name
                                                                     and col.column_name = kcu.column_name
                                                                     and kcu.referenced_table_schema is not null
                    where col.table_schema not in('information_schema','sys', 'mysql', 'performance_schema')
                                              and tab.table_type = 'BASE TABLE'
                    order by col.table_schema, col.table_name, col.ordinal_position;"""
        results = self.query(query)
        if nested == False:
            return results

        table_info = {}
        for row in results:
            table_info[row['table']] = {} if table_info.get(row['table']) is None else table_info[row['table']]
            table_info[row['table']][row['column_name']] = {} if table_info.get(row['table']).get(row['column_name']) is None else table_info[row['table']][row['column_name']]
            table_info[row['table']][row['column_name']]['column_comment']     = row['column_comment']
            table_info[row['table']][row['column_name']]['fk_column_name']     = row['fk_column_name']
            table_info[row['table']][row['column_name']]['fk_table_name']      = row['fk_table_name']
            table_info[row['table']][row['column_name']]['is_key']             = row['is_key']
            table_info[row['table']][row['column_name']]['table']              = row['table']
        return table_info




    # def createTables(self, purge=False, data_path='flask_app/database'):
    #         # Purge tables if required
    #         if purge:
    #             tables = ['skills', 'experiences', 'positions', 'institutions', 'feedback']
    #             for table in reversed(tables):
    #                 try:
    #                     self.query(f"DROP TABLE IF EXISTS {table}")
    #                 except mysql.connector.Error as e:
    #                     print(f"Error dropping table {table}: {e}")


    #         # Create tables from SQL files
    #         table_files = ['institutions.sql', 'positions.sql', 'experiences.sql', 'skills.sql', 'feedback.sql']
    #         for file_name in table_files:
    #             file_path = os.path.join(data_path, 'create_tables', file_name)
    #             if os.path.exists(file_path):
    #                 with open(file_path, 'r') as f:
    #                     sql_script = f.read()
    #                     try:
    #                         self.query(sql_script)
    #                     except mysql.connector.Error as e:
    #                         print(f"Error executing {file_name}: {e}")

    #         # Load CSV files and populate tables
    #         csv_files = ['institutions.csv', 'positions.csv', 'experiences.csv', 'skills.csv', 'feedback.csv']
    #         for file_name in csv_files:
    #             file_path = os.path.join(data_path, 'initial_data', file_name)
    #             table_name = file_name.replace('.csv', '')

    #             if os.path.exists(file_path):
    #                 with open(file_path, 'r') as f:
    #                     reader = csv.reader(f)
    #                     try:
    #                         # Attempt to read the header row
    #                         columns = next(reader)
    #                         rows = [row for row in reader if row]  # Filter out any empty rows

    #                         # Only insert rows if there are non-empty rows
    #                         if rows:
    #                             self.insertRows(table_name, columns, rows)
    #                         else:
    #                             print(f"Skipping empty data for {table_name}")
    #                     except StopIteration:
    #                         print(f"Skipping empty CSV file: {file_path}")

    def insertRows(self, table, columns, parameters):
        # Prepare the SQL statement for inserting data
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES "
        values_list = []

        for row in parameters:
            cleaned_row = []
            for value in row:
                if value == 'NULL' or value == '':
                    cleaned_row.append("NULL")
                else:
                    # Attempt to parse dates if detected
                    try:
                        date_value = datetime.strptime(value, '%Y-%m-%d').date()
                        cleaned_row.append(f"'{date_value}'")
                    except ValueError:
                        escaped_value = value.replace("'", "''")
                        cleaned_row.append(f"'{escaped_value}'")
            
            values_list.append(f"({', '.join(cleaned_row)})")

        # Construct the full insert query
        final_query = query + ", ".join(values_list) + ";"

        try:
            self.query(final_query)
        except mysql.connector.Error as e:
            print(f"MySQL Error inserting into {table}: {e}")




    def getResumeData(self):
        # Query to get all relevant data from each table
        institutions = self.query("SELECT * FROM `institutions`")
        positions = self.query("SELECT * FROM `positions`")
        experiences = self.query("SELECT * FROM `experiences`")
        skills = self.query("SELECT * FROM `skills`")

        # Initialize the data structure for nested organization
        data = {}

        # Step 1: Add institutions and initialize nested dictionaries for positions
        for inst in institutions:
            inst_id = inst['inst_id']
            data[inst_id] = inst
            data[inst_id]['positions'] = {}

        # Step 2: Attach each position to its institution and initialize experiences
        for pos in positions:
            inst_id = pos['inst_id']
            pos_id = pos['position_id']
            if inst_id in data:
                data[inst_id]['positions'][pos_id] = pos
                data[inst_id]['positions'][pos_id]['experiences'] = {}

        # Step 3: Attach each experience to its position within the correct institution
        for exp in experiences:
            pos_id = exp['position_id']
            exp_id = exp['experience_id']
            for inst in data.values():
                if pos_id in inst['positions']:
                    inst['positions'][pos_id]['experiences'][exp_id] = exp
                    inst['positions'][pos_id]['experiences'][exp_id]['skills'] = {}

        # Step 4: Attach each skill to its corresponding experience
        for skill in skills:
            exp_id = skill['experience_id']
            for inst in data.values():
                for pos in inst['positions'].values():
                    if exp_id in pos['experiences']:
                        pos['experiences'][exp_id]['skills'][skill['skill_id']] = skill

        return data


    def create_default_lists(self, board_id):
        """
        Create the three default lists for a new board
        """
        print(f"Creating default lists for board {board_id}")  # Debug print
        default_lists = [
            ('To Do', 0),
            ('In Progress', 1),
            ('Completed', 2)
        ]
        
        for name, position in default_lists:
            try:
                self.query(
                    "INSERT INTO lists (board_id, name, position) VALUES (%s, %s, %s)",
                    (board_id, name, position)
                )
                print(f"Created list: {name}")  # Debug print
            except Exception as e:
                print(f"Error creating list {name}: {e}")  # Debug print