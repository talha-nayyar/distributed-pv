from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AddSecretRequest(_message.Message):
    __slots__ = ("user_id", "secret_name", "data")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    SECRET_NAME_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    secret_name: str
    data: str
    def __init__(self, user_id: _Optional[str] = ..., secret_name: _Optional[str] = ..., data: _Optional[str] = ...) -> None: ...

class AddSecretResponse(_message.Message):
    __slots__ = ("secret_id", "message", "success")
    SECRET_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    secret_id: str
    message: str
    success: bool
    def __init__(self, secret_id: _Optional[str] = ..., message: _Optional[str] = ..., success: bool = ...) -> None: ...

class RetrieveSecretRequest(_message.Message):
    __slots__ = ("user_id", "secret_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    SECRET_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    secret_id: str
    def __init__(self, user_id: _Optional[str] = ..., secret_id: _Optional[str] = ...) -> None: ...

class RetrieveSecretResponse(_message.Message):
    __slots__ = ("secret_id", "data", "success")
    SECRET_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    secret_id: str
    data: str
    success: bool
    def __init__(self, secret_id: _Optional[str] = ..., data: _Optional[str] = ..., success: bool = ...) -> None: ...

class UpdateSecretRequest(_message.Message):
    __slots__ = ("user_id", "secret_id", "data")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    SECRET_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    secret_id: str
    data: str
    def __init__(self, user_id: _Optional[str] = ..., secret_id: _Optional[str] = ..., data: _Optional[str] = ...) -> None: ...

class UpdateSecretResponse(_message.Message):
    __slots__ = ("secret_id", "message", "success")
    SECRET_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    secret_id: str
    message: str
    success: bool
    def __init__(self, secret_id: _Optional[str] = ..., message: _Optional[str] = ..., success: bool = ...) -> None: ...

class DeleteSecretRequest(_message.Message):
    __slots__ = ("user_id", "secret_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    SECRET_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    secret_id: str
    def __init__(self, user_id: _Optional[str] = ..., secret_id: _Optional[str] = ...) -> None: ...

class DeleteSecretResponse(_message.Message):
    __slots__ = ("secret_id", "message", "success")
    SECRET_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    secret_id: str
    message: str
    success: bool
    def __init__(self, secret_id: _Optional[str] = ..., message: _Optional[str] = ..., success: bool = ...) -> None: ...

class ListSecretsRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class SecretMetadata(_message.Message):
    __slots__ = ("secret_id", "secret_name", "created_at", "updated_at", "is_shared")
    SECRET_ID_FIELD_NUMBER: _ClassVar[int]
    SECRET_NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    IS_SHARED_FIELD_NUMBER: _ClassVar[int]
    secret_id: str
    secret_name: str
    created_at: str
    updated_at: str
    is_shared: bool
    def __init__(self, secret_id: _Optional[str] = ..., secret_name: _Optional[str] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ..., is_shared: bool = ...) -> None: ...

class ListSecretsResponse(_message.Message):
    __slots__ = ("secrets", "total_count")
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    secrets: _containers.RepeatedCompositeFieldContainer[SecretMetadata]
    total_count: int
    def __init__(self, secrets: _Optional[_Iterable[_Union[SecretMetadata, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class ShareSecretRequest(_message.Message):
    __slots__ = ("owner_id", "secret_id", "target_user_id")
    OWNER_ID_FIELD_NUMBER: _ClassVar[int]
    SECRET_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_USER_ID_FIELD_NUMBER: _ClassVar[int]
    owner_id: str
    secret_id: str
    target_user_id: str
    def __init__(self, owner_id: _Optional[str] = ..., secret_id: _Optional[str] = ..., target_user_id: _Optional[str] = ...) -> None: ...

class ShareSecretResponse(_message.Message):
    __slots__ = ("message", "success")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    message: str
    success: bool
    def __init__(self, message: _Optional[str] = ..., success: bool = ...) -> None: ...

class CheckAccessRequest(_message.Message):
    __slots__ = ("user_id", "secret_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    SECRET_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    secret_id: str
    def __init__(self, user_id: _Optional[str] = ..., secret_id: _Optional[str] = ...) -> None: ...

class CheckAccessResponse(_message.Message):
    __slots__ = ("has_access", "owner_id")
    HAS_ACCESS_FIELD_NUMBER: _ClassVar[int]
    OWNER_ID_FIELD_NUMBER: _ClassVar[int]
    has_access: bool
    owner_id: str
    def __init__(self, has_access: bool = ..., owner_id: _Optional[str] = ...) -> None: ...

class ReplicateSecretRequest(_message.Message):
    __slots__ = ("secret_id", "user_id", "secret_name", "data", "created_at")
    SECRET_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    SECRET_NAME_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    secret_id: str
    user_id: str
    secret_name: str
    data: str
    created_at: str
    def __init__(self, secret_id: _Optional[str] = ..., user_id: _Optional[str] = ..., secret_name: _Optional[str] = ..., data: _Optional[str] = ..., created_at: _Optional[str] = ...) -> None: ...

class ReplicateSecretResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class ReplicateUpdateRequest(_message.Message):
    __slots__ = ("secret_id", "data", "updated_at")
    SECRET_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    secret_id: str
    data: str
    updated_at: str
    def __init__(self, secret_id: _Optional[str] = ..., data: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class ReplicateUpdateResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class ReplicateDeletionRequest(_message.Message):
    __slots__ = ("secret_id",)
    SECRET_ID_FIELD_NUMBER: _ClassVar[int]
    secret_id: str
    def __init__(self, secret_id: _Optional[str] = ...) -> None: ...

class ReplicateDeletionResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class ReplicateShareRequest(_message.Message):
    __slots__ = ("secret_id", "owner_id", "target_user_id")
    SECRET_ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_USER_ID_FIELD_NUMBER: _ClassVar[int]
    secret_id: str
    owner_id: str
    target_user_id: str
    def __init__(self, secret_id: _Optional[str] = ..., owner_id: _Optional[str] = ..., target_user_id: _Optional[str] = ...) -> None: ...

class ReplicateShareResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...
