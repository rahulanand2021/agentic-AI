from pydantic import BaseModel

# Create a Pydantic model for the Evaluation

class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str