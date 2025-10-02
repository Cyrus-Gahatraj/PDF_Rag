from passlib.context import CryptContext

password_context = CryptContext(schemes=['argon2'], deprecated='auto')

def hash(password: str):
    return password_context.hash(password)

def verify(password_provided: str, hash_password: str):
    return password_context.verify(password_provided, hash_password)