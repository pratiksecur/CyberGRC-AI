from app.auth.hashing import hash_password, verify_password

password = "Pratik@123"

hashed = hash_password(password)

print("Original Password :", password)
print("Hashed Password   :", hashed)

print("\nVerification Result:")
print(verify_password(password, hashed))