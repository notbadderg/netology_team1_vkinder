TABLES = """
            CREATE TABLE IF NOT EXISTS target (
            vk_id       INTEGER     NOT NULL, 
            first_name  VARCHAR(50) NOT NULL, 
            last_name   VARCHAR(50) NOT NULL, 
            url         TEXT        NOT NULL, 
            PRIMARY KEY (vk_id)
            );
            
            CREATE TABLE IF NOT EXISTS favorite (
            client_vk_id INTEGER NOT NULL, 
            target_vk_id INTEGER NOT NULL, 
            PRIMARY KEY (client_vk_id, target_vk_id), 
            FOREIGN KEY (target_vk_id) REFERENCES target (vk_id) ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS photo (
            photo_id        TEXT    NOT NULL, 
            target_vk_id    INTEGER NOT NULL, 
            photo_link      TEXT    NOT NULL, 
            PRIMARY KEY (photo_id, target_vk_id), 
            FOREIGN KEY (target_vk_id) REFERENCES target (vk_id) ON DELETE CASCADE
            );
        """