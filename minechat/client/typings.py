from pydantic import BaseModel, root_validator


class RegistrationResult(BaseModel):
    username: str
    nickname: str
    token: str

    @root_validator(pre=True)
    def pre_load(cls, values):
        values["token"] = values["account_hash"]
        return values
