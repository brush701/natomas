import bcrypt
import uuid
from collections import defaultdict
from lib.session_helper import session_required
import psycopg2

class User:
    COLUMNS = [

    ]

    @staticmethod
    def create(data, cursor):
        # Check for existing user
        cursor.execute(
            "select count(*) from users where username = %s",
            (data.get("username"),)
        )

        row = cursor.fetchone()
        if row and row[0] > 0:
            return {
                "status": "error",
                "msg": "This username has already been taken."
            }

        # Create User
        passhash = bcrypt.hashpw(data["password"], bcrypt.gensalt())
        cursor.execute(
            """
            insert into users(
                username,
                first_name,
                last_name,
                email,
                cryptpass,
                last_login
            )
            values (%s, %s, %s, %s, %s, extract(epoch from now())::integer)
            returning id
            """,
            (
                data["username"],
                data["first_name"],
                data["last_name"],
                data["email"],
                passhash
            )
        )
        row = cursor.fetchone()
        user_id = row[0]

        # Add permissions
        perms = ["basic"]
        User._add_permissions(cursor, user_id, perms)

        # Create session
        session_id = str(uuid.uuid4())
        cursor.execute(
            "insert into sessions(user_id, session_id) values (%s, %s)",
            (user_id, session_id)
        )

        return {
            "status": "ok",
            "user_id": user_id,
            "session_id": session_id
        }

    @staticmethod
    def _add_permissions(cursor, user_id, perms):
        # Cache permission map
        permission_map = {}
        cursor.execute("select id, name from permission_types")
        for perm_id, perm_name in cursor:
            permission_map[perm_name] = perm_id

        # Apply Permissions
        for p in perms:
            if p in permission_map:
                cursor.execute(
                    """
                    insert into user_permissions (user_id, permission_id)
                    values (%s, %s)
                    """,
                    (user_id, permission_map.get(p))
                )

    @staticmethod
    @session_required
    def get(data, cursor):
        user = User._get(cursor, data.get("user_id"))
        user["status"] = "ok"
        return user

    @staticmethod
    def _get(cursor, user_id):
        cursor.execute(
            """
            select username, first_name, last_name, email, last_login
            from users
            where id = %s and deleted = false
            """,
            (user_id,)
        )

        row = cursor.fetchone()

        # Look up what permissions the user has access to
        permissions = User._permission_dict(cursor, [user_id])[user_id];

        return {
            "id": user_id,
            "username": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "email": row[3],
            "last_login": row[4],
            "permissions": permissions
        }

    @staticmethod
    def _permission_dict(cursor, user_ids):
        output = defaultdict(list)

        # Look up what permissions the user has access to
        cursor.execute(
            """
            select a.user_id, b.name
            from user_permissions a
            join permission_types b
                on a.permission_id = b.id
            where a.user_id = ANY(%s)
            """,
            (user_ids,)
        )

        for user_id, perm in cursor:
            output[user_id].append(perm)

        return output

    @staticmethod
    @session_required
    def edit(data, cursor):
        error = User._edit(cursor, data.get("user_id"), data)

        if error:
            return error
        else:
            return {
                "status": "ok",
                "success": True
            }

    @staticmethod
    def _edit(cursor, user_id, data):
        col_list = []
        val_list = []
        for x in ("username", "first_name", "last_name", "email"):
            if x in data:
                col_list.append(x + " = %s")
                val_list.append(data.get(x))

        val_list.append(user_id)

        try:
            cursor.execute(
                "update users set " + ", ".join(col_list) + "where id = %s",
                val_list
            )

            return None
        except psycopg2.IntegrityError:
            return {
                "status": "error",
                "msg": "Username already in use."
            }

    @staticmethod
    @session_required
    def password(data, cursor):
        return User._password(
            cursor,
            data.get("user_id"),
            data.get("new_password")
        )

    @staticmethod
    def _password(cursor, user_id, new_password):
        if (new_password is None) or (len(new_password) == 0):
            return {
                "status": "error",
                "msg": "New password is required."
            }

        passhash = bcrypt.hashpw(new_password, bcrypt.gensalt())
        cursor.execute(
            "update users set cryptpass = %s where id = %s",
            (passhash, user_id)
        )

        return {
            "status": "ok"
        }

