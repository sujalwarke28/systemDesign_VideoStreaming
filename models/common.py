from pydantic import BaseModel, BeforeValidator
from typing import Annotated, Any

# Custom type for PyObjectId, useful for handling MongoDB's _id
PyObjectId = Annotated[str, BeforeValidator(str)]
