from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.status import HTTP_403_FORBIDDEN
import sqlite3 as sql
from pydantic import BaseModel

class DataBase:
    def __init__(self, conn):
        self.conn = conn
        self.conn.commit()
        self.conn.close()

    def sql_command(self, command):
        try:
            self.conn = sql.connect("logs_of_game.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute(command)

            self.data = self.cursor.fetchall()
            return self.data
        finally:
            self.conn.commit()
            self.conn.close()

class Input(BaseModel):
    name: str

app = FastAPI(
    title="GameServer",
    description="Server of games"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get('/welcome', tags=["Message Of Welcome"])
def message():
    return {
        "message": "Hola usuario bienvenido(a) al juego",
        "status": 200
    }

@app.post('/users', tags=["Logs Of Users"])
def save_data_of_users(data_of_input: Input):
    name = data_of_input.name
    conn = sql.connect("logs_of_game.db")

    app = DataBase(conn)
    app.sql_command(
        """CREATE TABLE IF NOT EXISTS users(
              id INTEGER,
              name TEXT,
              trys TEXT
        );"""
    )
    trys = app.sql_command("SELECT trys FROM users;")
    commands_forbidden = [
        "SELECT", "select",
        "UPDATE", "update",
        "SET", "set",
        "DROP", "drop",
        "DELETE", "delete",
        "CREATE", "create",
        "WHERE", "where",
        "INTO", "into",
        "VALUES", "values"
    ]
    forbidden = True

    if trys[0][0] < 1:
        for i in name:
            if i in (',', '(', ')', ';', '-', "'"):
                forbidden = False
                break
        for i in commands_forbidden:
            if i == name.split().strip():
                    print("No se permiten comandos SQL")
            elif not forbidden:
                    print("No se aceptan carácteres especiales, por favor solo escriba letras")
                    break
            else:
                app.sql_command(f"INSERT INTO users VALUES (1, '{name}', 1)")
                break

    return {
        "message": "Tus datos de usuario han sido guardados en el servidor exitosamente",
        "status": 201
    }

@app.delete('/users', tags=["Delete Data Of Users"])
def delete_data_of_users(data_of_input: Input):
    data_of_user_to_delete = data_of_input.name

    return {
        "status": 204
    }
