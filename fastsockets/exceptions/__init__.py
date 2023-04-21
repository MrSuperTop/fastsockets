from fastapi import HTTPException, status

NOT_AUTHENTICATED = HTTPException(
    status.HTTP_401_UNAUTHORIZED,
    'You should login first'
)

ALREADY_AUTHENICATED = HTTPException(
    status.HTTP_403_FORBIDDEN,
    'Already authenticated'
)
