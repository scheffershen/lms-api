from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.lov.answer_type import AnswerType, AnswerTypeCreate, UserShort
from app.db.session import get_db_connection
from app.api.v1.deps.auth import get_current_user
from datetime import datetime
from slugify import slugify

router = APIRouter()

@router.get("/answer-types", response_model=List[AnswerType])
async def list_answer_types(db=Depends(get_db_connection)):
    """
    Retrieve all answer types with their French translations.
    
    Returns:
        List[AnswerType]: List of all answer types with translations
    """
    async with db.cursor() as cursor:
        # First get all answer types
        await cursor.execute("""
            SELECT
                at.id,
                cu.id as create_user_id, cu.firstname as create_user_firstname, cu.lastname as create_user_lastname,
                uu.id as update_user_id, uu.firstname as update_user_firstname, uu.lastname as update_user_lastname,
                at.title, at.description, at.keywords, at.sort, at.revision, at.create_date, at.update_date, at.is_valid, at.conditional
            FROM answer_type at
            LEFT JOIN fos_user cu ON at.create_user_id = cu.id
            LEFT JOIN fos_user uu ON at.update_user_id = uu.id
        """)
        rows = await cursor.fetchall()
        
        # Get French translations separately
        if rows:
            answer_type_ids = [str(row[0]) for row in rows]
            placeholders = ','.join(['%s'] * len(answer_type_ids))
            await cursor.execute(f"""
                SELECT foreign_key, content 
                FROM ext_translations 
                WHERE object_class LIKE %s
                AND field = %s
                AND locale = %s
                AND foreign_key IN ({placeholders})
            """, ('%AnswerType%', 'title', 'fr', *answer_type_ids))
            translations = {str(row[0]): row[1] for row in await cursor.fetchall()}
        else:
            translations = {}
    
    return [
        AnswerType(
            id=row[0],
            create_user=UserShort(
                user_id=row[1], firstname=row[2], lastname=row[3]
            ) if row[1] else None,
            update_user=UserShort(
                user_id=row[4], firstname=row[5], lastname=row[6]
            ) if row[4] else None,
            title=row[7],
            title_fr=translations.get(str(row[0])),
            description=row[8],
            keywords=row[9],
            sort=row[10],
            revision=row[11],
            create_date=row[12],
            update_date=row[13],
            is_valid=bool(row[14]),
            conditional=row[15]
        )
        for row in rows
    ]

@router.get("/answer-types/{answer_type_id}", response_model=AnswerType)
async def get_answer_type(answer_type_id: int, db=Depends(get_db_connection)):
    """
    Retrieve a specific answer type with its French translation.
    
    Args:
        answer_type_id (int): The ID of the answer type to retrieve
        
    Returns:
        AnswerType: The answer type with its French translation
    """
    async with db.cursor() as cursor:
        # First get the answer type
        await cursor.execute("""
            SELECT
                at.id,
                cu.id as create_user_id, cu.firstname as create_user_firstname, cu.lastname as create_user_lastname,
                uu.id as update_user_id, uu.firstname as update_user_firstname, uu.lastname as update_user_lastname,
                at.title, at.description, at.keywords, at.sort, at.revision, at.create_date, at.update_date, at.is_valid, at.conditional
            FROM answer_type at
            LEFT JOIN fos_user cu ON at.create_user_id = cu.id
            LEFT JOIN fos_user uu ON at.update_user_id = uu.id
            WHERE at.id = %s
        """, (answer_type_id,))
        row = await cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="AnswerType not found")
        
        # Get French translation separately
        await cursor.execute("""
            SELECT content 
            FROM ext_translations 
            WHERE object_class LIKE %s
            AND field = %s
            AND locale = %s
            AND foreign_key = %s
        """, ('%AnswerType%', 'title', 'fr', str(answer_type_id)))
        translation_row = await cursor.fetchone()
        title_fr = translation_row[0] if translation_row else None
        
    return AnswerType(
        id=row[0],
        create_user=UserShort(
            user_id=row[1], firstname=row[2], lastname=row[3]
        ) if row[1] else None,
        update_user=UserShort(
            user_id=row[4], firstname=row[5], lastname=row[6]
        ) if row[4] else None,
        title=row[7],
        title_fr=title_fr,
        description=row[8],
        keywords=row[9],
        sort=row[10],
        revision=row[11],
        create_date=row[12],
        update_date=row[13],
        is_valid=bool(row[14]),
        conditional=row[15]
    )

@router.post("/answer-types", response_model=AnswerType, status_code=status.HTTP_201_CREATED)
async def create_answer_type(
    answer_type: AnswerTypeCreate,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user) 
):
    """
    Create a new answer type.
    
    Args:
        answer_type (AnswerTypeCreate): The answer type to create
        
    Returns:
        AnswerType: The created answer type
    """
    now = datetime.utcnow()
    conditional = slugify(answer_type.title)
    async with db.cursor() as cursor:
        # Insert main record
        await cursor.execute(
            "INSERT INTO answer_type (create_user_id, update_user_id, title, description, keywords, sort, revision, create_date, update_date, is_valid, conditional) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                current_user["id"], 
                current_user["id"],  
                answer_type.title,
                answer_type.description,
                answer_type.keywords,
                answer_type.sort,
                0, 
                now,
                now,
                True,
                conditional
            )
        )
        answer_type_id = cursor.lastrowid

        # Insert French translation if provided
        if answer_type.title_fr:
            await cursor.execute(
                "INSERT INTO ext_translations (locale, object_class, field, foreign_key, content) VALUES (%s, %s, %s, %s, %s)",
                (
                    'fr',
                    'App\\Entity\\LovManagement\\AnswerType',
                    'title',
                    str(answer_type_id),
                    answer_type.title_fr
                )
            )
        
        await db.commit()
    
    return AnswerType(
        id=answer_type_id,
        create_user=UserShort(
            user_id=current_user["id"],
            firstname=current_user["firstname"],
            lastname=current_user["lastname"]
        ),
        update_user=UserShort(
            user_id=current_user["id"],
            firstname=current_user["firstname"],
            lastname=current_user["lastname"]
        ),
        title=answer_type.title,
        title_fr=answer_type.title_fr,
        description=answer_type.description,
        keywords=answer_type.keywords,
        sort=answer_type.sort,
        revision=0,
        create_date=now,
        update_date=now,
        is_valid=True,
        conditional=conditional
    )

@router.put("/answer-types/{answer_type_id}", response_model=AnswerType)
async def update_answer_type(
    answer_type_id: int,
    answer_type: AnswerTypeCreate,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    """
    Update an existing answer type.
    
    Args:
        answer_type_id (int): The ID of the answer type to update
        answer_type (AnswerTypeCreate): The updated answer type data
        
    Returns:
        AnswerType: The updated answer type
    """
    now = datetime.utcnow()
    async with db.cursor() as cursor:
        # Get original create_user_id and revision for response
        await cursor.execute(
            "SELECT create_user_id, revision, create_date, is_valid, conditional FROM answer_type WHERE id = %s",
            (answer_type_id,)
        )
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="AnswerType not found")
        create_user_id, current_revision, create_date, is_valid, conditional = row
        new_revision = (current_revision or 0) + 1
        
        # Fetch create_user info
        await cursor.execute(
            "SELECT id, firstname, lastname FROM fos_user WHERE id = %s",
            (create_user_id,)
        )
        cu = await cursor.fetchone()
        create_user = None
        if cu:
            create_user = UserShort(user_id=cu[0], firstname=cu[1], lastname=cu[2])
        
        # Update main record
        await cursor.execute(
            "UPDATE answer_type SET update_user_id=%s, title=%s, description=%s, keywords=%s, sort=%s, revision=%s, update_date=%s WHERE id=%s",
            (
                current_user["id"],
                answer_type.title,
                answer_type.description,
                answer_type.keywords,
                answer_type.sort,
                new_revision,
                now,
                answer_type_id
            )
        )

        # Update or insert French translation
        if answer_type.title_fr is not None:
            await cursor.execute(
                """
                INSERT INTO ext_translations (locale, object_class, field, foreign_key, content)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE content = VALUES(content)
                """,
                (
                    'fr',
                    'App\\Entity\\LovManagement\\AnswerType',
                    'title',
                    str(answer_type_id),
                    answer_type.title_fr
                )
            )

        # Get current French translation
        await cursor.execute(
            """
            SELECT content FROM ext_translations 
            WHERE object_class LIKE %s
            AND foreign_key = %s
            AND field = %s
            AND locale = %s
            """,
            ('%AnswerType%', str(answer_type_id), 'title', 'fr')
        )
        title_fr_row = await cursor.fetchone()
        title_fr = title_fr_row[0] if title_fr_row else None

        await db.commit()
        
    return AnswerType(
        id=answer_type_id,
        create_user=create_user,
        update_user=UserShort(
            user_id=current_user["id"],
            firstname=current_user["firstname"],
            lastname=current_user["lastname"]
        ),
        title=answer_type.title,
        title_fr=title_fr,
        description=answer_type.description,
        keywords=answer_type.keywords,
        sort=answer_type.sort,
        revision=new_revision,
        create_date=create_date,
        update_date=now,
        is_valid=is_valid,
        conditional=conditional
    )

@router.post("/answer-types/{answer_type_id}/disable", status_code=status.HTTP_204_NO_CONTENT)
async def disable_answer_type(answer_type_id: int, db=Depends(get_db_connection), current_user=Depends(get_current_user)):
    """
    Disable an existing answer type.
    
    Args:
        answer_type_id (int): The ID of the answer type to disable
        
    Returns:
        None
    """
    now = datetime.utcnow()

    async with db.cursor() as cursor:
        await cursor.execute(
            "UPDATE answer_type SET is_valid = FALSE, update_user_id = %s, update_date = %s WHERE id = %s AND is_valid = TRUE",
            (current_user["id"], now, answer_type_id)
        )
        await db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="AnswerType not found or already disabled")
    return None

@router.post("/answer-types/{answer_type_id}/enable", status_code=status.HTTP_204_NO_CONTENT)
async def enable_answer_type(answer_type_id: int, db=Depends(get_db_connection), current_user=Depends(get_current_user)):
    """
    Enable an existing answer type.
    
    Args:
        answer_type_id (int): The ID of the answer type to enable
        
    Returns:
        None
    """
    now = datetime.utcnow()
    async with db.cursor() as cursor:
        await cursor.execute(
            "UPDATE answer_type SET is_valid = TRUE, update_user_id = %s, update_date = %s WHERE id = %s AND is_valid = FALSE",
            (current_user["id"], now, answer_type_id)
        )
        await db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="AnswerType not found or already enabled")
    return None
