from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.lov.answer_type import AnswerType
from app.db.session import get_db_connection

router = APIRouter()

@router.get("/answer-types", response_model=List[AnswerType])
async def list_answer_types(db=Depends(get_db_connection)):
    async with db.cursor() as cursor:
        await cursor.execute("SELECT id, create_user_id, update_user_id, title, description, keywords, sort, revision, create_date, update_date, is_valid, conditional FROM answer_type")
        rows = await cursor.fetchall()
    return [
        AnswerType(
            id=row[0],
            create_user_id=row[1],
            update_user_id=row[2],
            title=row[3],
            description=row[4],
            keywords=row[5],
            sort=row[6],
            revision=row[7],
            create_date=row[8],
            update_date=row[9],
            is_valid=bool(row[10]),
            conditional=row[11]
        )
        for row in rows
    ]

@router.get("/answer-types/{answer_type_id}", response_model=AnswerType)
async def get_answer_type(answer_type_id: int, db=Depends(get_db_connection)):
    async with db.cursor() as cursor:
        await cursor.execute("SELECT id, create_user_id, update_user_id, title, description, keywords, sort, revision, create_date, update_date, is_valid, conditional FROM answer_type WHERE id = %s", (answer_type_id,))
        row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="AnswerType not found")
    return AnswerType(
        id=row[0], create_user_id=row[1], update_user_id=row[2], title=row[3], description=row[4],
        keywords=row[5], sort=row[6], revision=row[7], create_date=row[8], update_date=row[9],
        is_valid=bool(row[10]), conditional=row[11]
    )

@router.post("/answer-types", response_model=AnswerType, status_code=status.HTTP_201_CREATED)
async def create_answer_type(answer_type: AnswerType, db=Depends(get_db_connection)):
    async with db.cursor() as cursor:
        await cursor.execute(
            "INSERT INTO answer_type (create_user_id, update_user_id, title, description, keywords, sort, revision, create_date, update_date, is_valid, conditional) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                answer_type.create_user_id, answer_type.update_user_id, answer_type.title, answer_type.description,
                answer_type.keywords, answer_type.sort, answer_type.revision, answer_type.create_date,
                answer_type.update_date, int(answer_type.is_valid), answer_type.conditional
            )
        )
        await db.commit()
        answer_type_id = cursor.lastrowid
    return {**answer_type.dict(), "id": answer_type_id}

@router.put("/answer-types/{answer_type_id}", response_model=AnswerType)
async def update_answer_type(answer_type_id: int, answer_type: AnswerType, db=Depends(get_db_connection)):
    async with db.cursor() as cursor:
        await cursor.execute(
            "UPDATE answer_type SET create_user_id=%s, update_user_id=%s, title=%s, description=%s, keywords=%s, sort=%s, revision=%s, create_date=%s, update_date=%s, is_valid=%s, conditional=%s WHERE id=%s",
            (
                answer_type.create_user_id, answer_type.update_user_id, answer_type.title, answer_type.description,
                answer_type.keywords, answer_type.sort, answer_type.revision, answer_type.create_date,
                answer_type.update_date, int(answer_type.is_valid), answer_type.conditional, answer_type_id
            )
        )
        await db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="AnswerType not found")
    return {**answer_type.dict(), "id": answer_type_id}

@router.delete("/answer-types/{answer_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer_type(answer_type_id: int, db=Depends(get_db_connection)):
    async with db.cursor() as cursor:
        await cursor.execute("DELETE FROM answer_type WHERE id = %s", (answer_type_id,))
        await db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="AnswerType not found")
