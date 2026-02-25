import argparse
import sqlite3

VALID_ROLES = {"cliente", "administrativo"}


def update_user_role(email: str, role: str) -> None:
    role_value = role.strip().lower()
    if role_value not in VALID_ROLES:
        raise ValueError(f"Rol invalido. Usa uno de: {', '.join(sorted(VALID_ROLES))}")

    conn = sqlite3.connect("dev.db")
    cur = conn.cursor()

    cur.execute("SELECT id, full_name, email, role FROM users WHERE lower(email) = lower(?)", (email,))
    user = cur.fetchone()
    if not user:
        conn.close()
        raise ValueError("No se encontro un usuario con ese email")

    cur.execute("UPDATE users SET role = ? WHERE id = ?", (role_value, user[0]))
    conn.commit()
    conn.close()

    print(f"Usuario actualizado: {user[2]} -> {role_value}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cambia el rol de un usuario")
    parser.add_argument("email", help="Email del usuario")
    parser.add_argument(
        "role",
        choices=sorted(VALID_ROLES),
        help="Rol a asignar",
    )
    args = parser.parse_args()

    update_user_role(args.email, args.role)
