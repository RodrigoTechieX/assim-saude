# services/db.py
import os
from sqlite3 import IntegrityError
import time
from urllib.parse import urlparse
from contextlib import contextmanager

# Dependências opcionais
try:
    import pymysql
    from pymysql.cursors import DictCursor
except Exception:
    pymysql = None
    DictCursor = None

try:
    import psycopg2
    import psycopg2.extras
except Exception:
    psycopg2 = None

# Wrapper para normalizar comportamento de cursor entre MySQL e Postgres
class ConnWrapper:
    def __init__(self, conn, kind):
        self._conn = conn
        self.kind = kind  # 'mysql' ou 'postgres'

    @contextmanager
    def cursor(self, *args, **kwargs):
        """
        Retorna um contexto para usar: `with self.conn.cursor() as cur:`
        Garante cursor dict-like em ambos os DBs.
        """
        if self.kind == 'postgres':
            cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            try:
                yield cur
            finally:
                try:
                    cur.close()
                except Exception:
                    pass
        else:
            # pymysql: se a conexão foi criada com cursorclass=DictCursor, o cursor padrão já é dict-like
            cur = self._conn.cursor()
            try:
                yield cur
            finally:
                try:
                    cur.close()
                except Exception:
                    pass

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        return self._conn.close()


class Database:
    def __init__(self, retries: int = 10, delay: int = 3):
        """
        Conecta automaticamente:
         - Se DATABASE_URL estiver definido -> usa essa URL (Postgres ou MySQL compatível)
         - Senão -> usa variáveis locais (DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME) para MySQL
        """
        db_url = os.getenv("DATABASE_URL") or os.getenv("CLEARDB_DATABASE_URL")

        attempt = 0
        while True:
            try:
                if db_url:
                    # Produção: parse da URL
                    url = urlparse(db_url)
                    scheme = url.scheme or ''
                    # postgres://... ou postgresql://...
                    if scheme.startswith('postgres'):
                        if not psycopg2:
                            raise RuntimeError("psycopg2 não instalado. Rode: pip install psycopg2-binary")
                        host = url.hostname
                        port = url.port or 5432
                        user = url.username
                        password = url.password
                        database = url.path.lstrip('/')
                        # Conecta com SSL requerido em serviços na nuvem
                        pg_conn = psycopg2.connect(
                            host=host,
                            port=port,
                            user=user,
                            password=password,
                            dbname=database,
                            sslmode="require"
                        )
                        # deixa autocommit True para evitar surpresas com transações pendentes
                        pg_conn.autocommit = True
                        self.conn = ConnWrapper(pg_conn, 'postgres')
                    else:
                        # Assume MySQL-style URL (mysql:// ou mysql+pymysql://)
                        if not pymysql:
                            raise RuntimeError("pymysql não instalado. Rode: pip install PyMySQL")
                        host = url.hostname
                        port = url.port or 3306
                        user = url.username
                        password = url.password
                        database = url.path.lstrip('/')
                        mysql_conn = pymysql.connect(
                            host=host,
                            port=port,
                            user=user,
                            password=password,
                            database=database,
                            cursorclass=DictCursor,
                            autocommit=True,
                        )
                        self.conn = ConnWrapper(mysql_conn, 'mysql')
                else:
                    # Local (Docker / MySQL Workbench)
                    if not pymysql:
                        raise RuntimeError("pymysql não instalado. Rode: pip install PyMySQL")
                    host = os.getenv("DB_HOST", "localhost")
                    port = int(os.getenv("DB_PORT", 3306))
                    user = os.getenv("DB_USER", "root")
                    password = os.getenv("DB_PASSWORD", "root")
                    database = os.getenv("DB_NAME", "assim_saude")
                    mysql_conn = pymysql.connect(
                        host=host,
                        port=port,
                        user=user,
                        password=password,
                        database=database,
                        cursorclass=DictCursor,
                        autocommit=True,
                    )
                    self.conn = ConnWrapper(mysql_conn, 'mysql')

                print(f"[Database] ✅ Conectado com sucesso ({'Postgres' if self.conn.kind == 'postgres' else 'MySQL'})")
                break

            except Exception as e:
                attempt += 1
                if attempt >= retries:
                    print(f"[Database] ❌ Não foi possível conectar depois de {retries} tentativas: {e}")
                    raise
                print(f"[Database] ❌ Falha na conexão (tentativa {attempt}/{retries}): {e}")
                time.sleep(delay)

    # Exemplo de uso dos métodos já existentes no seu arquivo:
    def buscar_cargos_por_nome(self, nome=''):
        with self.conn.cursor() as cur:
            sql = "SELECT * FROM cargos WHERE nome LIKE %s ORDER BY id DESC"
            cur.execute(sql, (f"%{nome}%",))
            return cur.fetchall()

    def inserir_cargo(self, nome, salario, descricao):
        with self.conn.cursor() as cur:
            sql = "INSERT INTO cargos (nome, salario, descricao) VALUES (%s, %s, %s)"
            cur.execute(sql, (nome, salario, descricao))
            # para psycopg2, o lastrowid não existe; usamos RETURNING id em SQL ao precisar do id
            try:
                return cur.lastrowid
            except Exception:
                # tenta pegar id via cursor (Postgres precisa de RETURNING id na query)
                return None

    def atualizar_cargo(self, cargo_id, nome, salario, descricao):
        with self.conn.cursor() as cur:
            sql = "UPDATE cargos SET nome=%s, salario=%s, descricao=%s WHERE id=%s"
            cur.execute(sql, (nome, salario, descricao, cargo_id))
            return cur.rowcount > 0

    def deletar_cargo(self, cargo_id):
        try:
            with self.conn.cursor() as cursor:
                sql = "DELETE FROM cargos WHERE id = %s"
                linhas = cursor.execute(sql, (cargo_id,))
                self.conn.commit()
                return linhas > 0
        except Exception as e:
            self.conn.rollback()
            print("Erro ao deletar cargo:", e)
            raise

    # ----------------------------
    # MÉTODOS DE FUNCIONÁRIO
    # ----------------------------
    def buscar_funcionarios(self, nome='', cpf=''):
        with self.conn.cursor() as cur:
            sql = """SELECT f.*, c.nome AS cargo_nome, c.salario AS cargo_salario
                     FROM funcionarios f
                     JOIN cargos c ON f.cargo_id = c.id
                     WHERE f.nome LIKE %s AND f.cpf LIKE %s
                     ORDER BY f.id DESC"""
            cur.execute(sql, (f"%{nome}%", f"%{cpf}%"))
            return cur.fetchall()

    def inserir_funcionario(self, nome, data_nascimento, endereco, cpf, email, telefone, cargo_id):
        if not self.validar_cpf(cpf):
            raise ValueError("CPF inválido")
        with self.conn.cursor() as cur:
            sql = """INSERT INTO funcionarios
                     (nome, data_nascimento, endereco, cpf, email, telefone, cargo_id)
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            try:
                cur.execute(sql, (nome, data_nascimento, endereco, cpf, email, telefone, cargo_id))
                return cur.lastrowid
            except IntegrityError as e:
                raise

    def atualizar_funcionario(self, func_id, data):
        cpf = data.get('cpf')
        if cpf and not self.validar_cpf(cpf):
            raise ValueError("CPF inválido")
        with self.conn.cursor() as cur:
            sql = """UPDATE funcionarios
                     SET nome=%s, data_nascimento=%s, endereco=%s, cpf=%s, email=%s, telefone=%s, cargo_id=%s
                     WHERE id=%s"""
            cur.execute(sql, (
                data.get('nome'),
                data.get('data_nascimento'),
                data.get('endereco'),
                data.get('cpf'),
                data.get('email'),
                data.get('telefone'),
                data.get('cargo_id'),
                func_id
            ))
            return cur.rowcount > 0

    def deletar_funcionario(self, func_id):
        with self.conn.cursor() as cur:
            sql = "DELETE FROM funcionarios WHERE id=%s"
            cur.execute(sql, (func_id,))
            return cur.rowcount > 0

    # ----------------------------
    # VALIDAÇÃO DE CPF
    # ----------------------------
    def validar_cpf(self, cpf: str) -> bool:
        if not cpf:
            return False
        cpf = ''.join(filter(str.isdigit, str(cpf)))
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False

        def calc_digito(cpf, peso):
            soma = 0
            for i in range(peso - 1):
                soma += int(cpf[i]) * (peso - i)
            resto = (soma * 10) % 11
            return resto if resto < 10 else 0

        try:
            return (calc_digito(cpf, 10) == int(cpf[9]) and
                    calc_digito(cpf, 11) == int(cpf[10]))
        except Exception:
            return False
