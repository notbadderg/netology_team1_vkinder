import psycopg2
from src.config import DatabaseConfig
from .db_tables import TABLES
from .data_classes import Target, Photo


class DatabaseInterface(DatabaseConfig):
    def __init__(self):
        super().__init__()
        self.db_conn = psycopg2.connect(host=self.host,
                                        port=self.port,
                                        dbname=self.dbname,
                                        user=self.user,
                                        password=self.password)
        self._create_table()

    def _create_table(self):
        with self.db_conn as conn:
            with conn.cursor() as curs:
                if self.launch_drop:
                    curs.execute("""
                                    DROP TABLE IF EXISTS target CASCADE;
                                    DROP TABLE IF EXISTS favorite CASCADE;
                                    DROP TABLE IF EXISTS client CASCADE;
                    """)
                curs.execute(TABLES)
                return None

    def add_to_favorite(self, target: Target, client_vk_id: int):
        with self.db_conn as conn:
            with conn.cursor() as curs:
                curs.execute("""
                    INSERT INTO target (vk_id, first_name, last_name, url)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    RETURNING vk_id;
                """, (target.vk_id, target.first_name, target.last_name, target.url))
                for photo in target.photos:
                    curs.execute("""
                        INSERT INTO photo (photo_id, target_vk_id, photo_link)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (photo.photo_id, photo.target_vk_id, photo.photo_link))

                curs.execute("""
                    INSERT INTO favorite (client_vk_id, target_vk_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                    RETURNING client_vk_id, target_vk_id;
                """, (client_vk_id, target.vk_id))

                curs.execute("""
                    SELECT client_vk_id, target_vk_id 
                      FROM favorite
                     WHERE (client_vk_id=%s AND target_vk_id=%s);
                """, (client_vk_id, target.vk_id))
                result = curs.fetchall()
        if result[0][0] == client_vk_id and result[0][1] == target.vk_id:
            return True
        return False

    def remove_favorite(self, target: Target, client_vk_id: int) -> bool:
        result = False
        with self.db_conn as conn:
            with conn.cursor() as curs:
                curs.execute("""
                    DELETE FROM favorite
                     WHERE (client_vk_id=%s AND target_vk_id=%s)
                    RETURNING client_vk_id;
                """, (client_vk_id, target.vk_id))
                if curs.fetchall():
                    result = True

                curs.execute("""
                    DELETE FROM target AS t
                     WHERE t.vk_id IN (SELECT t.vk_id
                                         FROM target AS t
                                              LEFT JOIN favorite AS f
                                                     ON t.vk_id = f.target_vk_id
                                        WHERE f.target_vk_id IS NULL)
                    RETURNING t.vk_id;
                """)
                curs.execute("""
                    DELETE FROM photo AS p
                     WHERE p.target_vk_id IN (SELECT p.target_vk_id
                                         FROM photo AS p
                                              LEFT JOIN target AS t
                                                     ON t.vk_id = p.target_vk_id
                                        WHERE t.vk_id IS NULL)
                    RETURNING p.target_vk_id;
                """)
        return result

    def get_client_favorites_list(self, client_vk_id: int) -> list:
        with self.db_conn as conn:
            with conn.cursor() as curs:
                curs.execute("""
                SELECT t.vk_id, t.first_name, t.last_name, t.url 
                 FROM target AS t 
                        JOIN favorite AS f 
                          ON t.vk_id = f.target_vk_id 
                WHERE f.client_vk_id = %s
                """, (client_vk_id,))
                favorites_list = []
                for a, b, c, d in curs.fetchall():
                    target = Target(a, b, c, d)
                    curs.execute("""
                        SELECT p.photo_id, p.target_vk_id, p.photo_link
                          FROM photo AS p
                         WHERE p.target_vk_id = %s
                    """, (target.vk_id,))
                    for e, f, g in curs.fetchall():
                        target.photos.append(Photo(e, f, g))
                    favorites_list.append(target)
        return favorites_list
