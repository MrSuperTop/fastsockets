from package.handlers import BaseActionHandler
from package.models import RegisterPayload, RegisterResponse


class RegisterHandler(BaseActionHandler):
    async def __call__(
        self,
        payload: RegisterPayload
    ) -> RegisterResponse:
        print(payload)

        return RegisterResponse(
            status=True
        )
