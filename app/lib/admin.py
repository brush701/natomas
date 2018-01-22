from lib.session_helper import session_required
from lib.user import User

def admin_required(func):
    "Decorator to check permissions."

    def wrapper(data, cursor):
        # Check that the user is an admin
        cursor.execute(
            """
            select count(*)
            from user_permissions a
            join permission_types b
                on a.permission_id = b.id
            where
                a.user_id = %s and
                b.name = 'admin'
            ;
            """,
            (data.get("user_id"),)
        )

        row = cursor.fetchone()
        is_admin = row and (row[0] > 0)

        if not is_admin:
            return {
                "status": "error",
                "msg": "This method is only available to admin users."
            }
        else:
            return func(data, cursor)

    return wrapper

class Admin:
    @staticmethod
    @admin_required
    @session_required
    def list(data, cursor):
        users = []
        user_ids = []

        # paginate
        count = data.get("count", 20)
        offset = data.get("page", 0) * count

        # Get user list
        cursor.execute(
            """
            select id, username, first_name, last_name, email, last_login
            from users
            where deleted = false
            order by id asc
            offset %s
            limit %s
            """,
            (offset, count)
        )

        for row in cursor:
            user_id, username, first, last, email, login = row
            users.append({
                "id": user_id,
                "username": username,
                "first_name": first,
                "last_name": last,
                "email": email,
                "last_login": login,
                "permissions": []
            })
            user_ids.append(user_id)

        # Look up what permissions the user has access to
        permissions = User._permission_dict(cursor, user_ids);

        # Assign the permissions
        for user in users:
            user["permissions"] = permissions.get(user["id"])

        # Get the total user count, for pagination
        cursor.execute("select count(*) from users where deleted = false")
        row = cursor.fetchone()
        if row:
            count = row[0]
        else:
            count = 0

        return {
            "status": "ok",
            "users": users,
            "total": count
        }

    @staticmethod
    @admin_required
    @session_required
    def get(data, cursor):
        user = User._get(cursor, data.get("lookup_user_id"))
        user["status"] = "ok"
        return user

    @staticmethod
    @admin_required
    @session_required
    def edit(data, cursor):
        error = User._edit(cursor, data.get("lookup_user_id"), data)

        if error:
            return error
        else:
            return {
                "status": "ok",
                "success": True
            }

    @staticmethod
    @admin_required
    @session_required
    def permissions(data, cursor):
        user_id = data.get("lookup_user_id")

        # delete user's permissions
        cursor.execute(
            "delete from user_permissions where user_id = %s",
            (user_id,)
        )

        # Add new permissions
        perms = data.get("permissions")
        User._add_permissions(cursor, user_id, perms)

        return {
            "status": "ok",
            "success": True
        }

    @staticmethod
    @admin_required
    @session_required
    def password(data, cursor):
        user_id = data.get("lookup_user_id")
        new_password = data.get("new_password")
        return User._password(cursor, user_id, new_password)

    @staticmethod
    @admin_required
    @session_required
    def delete(data, cursor):
        user_id = data.get("lookup_user_id")

        # delete user
        cursor.execute(
            """
            update users set deleted = true, username = null
            where id = %s
            """,
            (user_id,)
        )

        # Remove user's sessions
        cursor.execute(
            "delete from sessions where user_id = %s",
            (user_id,)
        )

        return {
            "status": "ok",
            "success": True
        }
