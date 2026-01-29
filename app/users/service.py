import uuid
from fastapi import HTTPException, status

from app.users.dao import UserDAO
from app.auth.password_handler import hash_password, verify_password, DUMMY_PASSWORD_HASH
from app.auth.jwt import create_access_token
from app.users.model import UserRegisterResponse, TokenResponse


class UserService:
    def __init__(self, dao: UserDAO | None = None, db_pool=None):
        if dao is not None:
            self.dao = dao
        elif db_pool is not None:
            self.dao = UserDAO(db_pool)
        else:
            raise ValueError("UserService requires either dao or db_pool")

    async def register_user(self, email: str, password: str, phone_number: str, username: str) -> UserRegisterResponse:

        # Normalize inputs
        email = email.strip().lower()
        username = username.strip()

        # 1. Check if user already exists
        existing = await self.dao.get_by_email_and_username(
            email=email,
            username=username,
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )

        # 2. Hash password (includes validation)
        try:
            hashed_password = hash_password(password)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        # 3. Create user
        user_id = str(uuid.uuid4())

        created_user_id = await self.dao.create_user(
            user_id=user_id,
            username=username,
            email=email,
            hashed_password=hashed_password,
            phone_number=phone_number
        )

        if not created_user_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User creation failed",
            )

        return UserRegisterResponse(
            message="User account successfully created",
            user_id=created_user_id,
        )

    async def user_login(self, email: str, password: str) -> TokenResponse:
        email = email.strip().lower()

        user = await self.dao.get_by_email(email)

        # Fake hash to normalize timing if user does not exist
        fake_hash = (
            "$argon2id$v=19$m=65536,t=3,p=4$"
            "c29tZXNhbHQ$"
            "c29tZWhhc2g"
        )

        password_hash = user.password if user and user.password else DUMMY_PASSWORD_HASH

        if not user or not verify_password(password, password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        access_token = create_access_token(
            subject=str(user.id)  # sub is now correctly a string
        )

        return TokenResponse(access_token=access_token)

