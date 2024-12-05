from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..utils.utils import get_openai_response
from ..utils.logger import log_message
from ..schemas.prompt import Prompt

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/match-analysis", response_model=Prompt)
async def match_analysis(prompt: str):
    try:
        response = await get_openai_response(prompt, max_tokens=250, temperature=0.5)
        return {"prompt": response}
    except Exception as e:
        log_message(f"An unexpected error occurred: {str(e)}", level="error")
        raise HTTPException(status_code=500, detail={
            "error": "Internal Server Error",
            "message": f"An unexpected error occurred: {str(e)}",
        }) from e
