from fastapi import APIRouter


router = APIRouter()


@router.get("/agents/")
async def get_agents():
    return ["Item 1", "Item 2", "Item 3", "Item 4"]
