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
    the_id: int
    name: str
    password: str

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

@app.post('/data_users', tags=["Logs Of Users"])
def save_data_of_users(data_of_input: Input):
    the_id = data_of_input.the_id
    name = data_of_input.name
    password = data_of_input.password
    conn = sql.connect("logs_of_game.db")

    app = DataBase(conn)
    app.sql_command(
        """CREATE TABLE IF NOT EXISTS users(
              id INTEGER,
              name TEXT,
              password TEXT
        );"""
    )
    user_name = app.sql_command(f"SELECT name FROM users WHERE id = '{the_id}';")
    user_password = app.sql_command("SELECT password FROM users WHERE id = '{the_id}';")
    print(user_name, user_password)

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

    if user_name[0][0] < 1 and user_password[0][0]: # Sorry por la tremenda tontería que he hecho en esta línea de código, jajajaja
        for i in id, name, password:
            if i in (',', '(', ')', ';', '-', "'"):
                forbidden = False
                break
        for i in commands_forbidden:
            if (i == id.split().strip()) or (i == name.split().strip()) or (i == password.split().strip()):
                    print("No se permiten comandos SQL")
            elif not forbidden:
                    print("No se aceptan carácteres especiales, por favor solo escriba letras")
                    break
            else:
                app.sql_command(f"INSERT INTO users VALUES ('{id}', '{name}', '{password}')")
                break

    return {
        "message": "Tus datos de usuario han sido guardados en el servidor exitosamente",
        "status": 201
    }

@app.delete('/delete_data', tags=["Delete Data Of Users"])
def delete_data_of_users(data_of_input: Input):
    data_of_user_to_delete = data_of_input.name

    return {
        "status": 204
    }
