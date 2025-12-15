from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.status import HTTP_403_FORBIDDEN
import pysqlite3-binary as sql
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

    is_valid = True

# Mala práctica en repetir dos iteraciones con tanto código

    if len(user_name) <= 2 and len(user_password) <= 2:
        for i in name:
            if i in (',', '(', ')', ';', '-', "'"):
                is_valid = False

            elif not is_valid:
                    return HTTPException(
                              status_code=422,
                              detail="No se aceptan carácteres especiales, por favor solo escriba letras"
                           )

        if is_valid:
            app.sql_command(f"INSERT INTO users (id, name) VALUES ('{the_id}', '{name}')")

        for i in password:
            if i in (',', '(', ')', ';', '-', "'"):
                is_valid = False

            elif not is_valid:
                    return HTTPException(
                             status_code=422,
                             detail="No se aceptan carácteres especiales, por favor solo escriba letras"
                           )

        if is_valid:
            app.sql_command(f"UPDATE users SET password = '{password}' WHERE id = '{the_id}'")

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
