from fastapi import HTTPException, status

INVALID_USER_CREDENTIALS = HTTPException(
    status.HTTP_400_BAD_REQUEST,
    'Invalid credentials were provided'
)

USER_ALREADY_EXISTS = HTTPException(
    status.HTTP_400_BAD_REQUEST,
    'This user already exists'
)

NOT_AUTHENTICATED = HTTPException(
    status.HTTP_401_UNAUTHORIZED,
    'You should login first'
)

USER_NOT_FOUND = HTTPException(
    status.HTTP_404_NOT_FOUND,
    'User not found'
)
