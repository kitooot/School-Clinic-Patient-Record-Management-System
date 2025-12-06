"""Database connection helpers for the clinic management system."""
from __future__ import annotations # Ensure compatibility with future Python versions

import pymysql # MySQL database connector

DB_NAME = 'clinicmanagementsystem'

# Create a new connection to the MySQL server.
def get_connection() -> pymysql.connections.Connection:
    """Create a new connection to the MySQL server."""
    return pymysql.connect(host='localhost', user='root', password='')

# Ensure the application database and patient table exist.
def ensure_schema(cursor: pymysql.cursors.Cursor, connection: pymysql.connections.Connection) -> None:
    """Create the application database and patient table if they do not exist."""
    cursor.execute(f'create database if not exists {DB_NAME}')
    cursor.execute(f'use {DB_NAME}')
    cursor.execute(
        'create table if not exists patient ('
        'patient_id varchar(30) primary key, '
        'name varchar(30), mobile varchar(30), email varchar(30), '
        'address varchar(100), gender varchar(30), dob varchar(30), '
        'diagnosis varchar(30), visit_date varchar(30)'
        ')'
    )
    cursor.execute(
        'create table if not exists users ('
        'username varchar(50) primary key, '
        'password varchar(255) not null'
        ')'
    )
    connection.commit()


# Initialize shared connection and cursor for the application.
db_connection = get_connection()
db_cursor = db_connection.cursor()
ensure_schema(db_cursor, db_connection)
