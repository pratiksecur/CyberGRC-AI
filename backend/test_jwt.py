from app.auth.jwt_handler import create_access_token

token = create_access_token(
    {
        "sub": "pratik@gmail.com"
    }
)

print("JWT Token:")
print(token)