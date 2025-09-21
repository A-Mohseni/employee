import logging
from fastapi import HTTPException, status
from pymongo import MongoClient,collection
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Collection, List, Optional
from models.log import logCreate, logOut
from utils.db import get_db
from pymongo import ASCENDING, DESCENDING


logger = logging.getLogger("employee_app")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def service_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            logger.exception("Service exception in %s: %s", func.__name__, exc)
            raise
    return wrapper

def create_log_indexes():
    try:
        db = get_db()
        collection = db["logs"]
        collection.create_index([("created_at", DESCENDING)])
        collection.create_index([("action_type", ASCENDING)])
        collection.create_index([("user_id", ASCENDING)])
        logger.info("Log indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating log indexes: {str(e)}")

create_log_indexes()

def create_log(data:logCreate,current_user:dict)->logOut:
    db=get_db()
    collection=db["logs"]

    log_data={
            "_id":ObjectId(),
            "action_type":data.action_type,
            "user_id":ObjectId(data.user_id),
            "description":data.description,
            "created_at":datetime.now()
    }

    try:
        collection.insert_one(log_data)
        return logOut(
            _id=str(log_data["_id"]),
            action_type=log_data["action_type"],
            user_id=str(log_data["user_id"]),
            description=log_data["description"],
            created_at=log_data["created_at"],
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))


def get_logs(current_user:dict,limit : int=20,offset:int=0,recent_hours:Optional[int]=None)->list[logOut]:
    allowed_roles={"manager_men","manager_women","admin1","admin2"}
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Access denied")

    db=get_db()
    collection=db["logs"]
    filter_query={}
    if recent_hours is not None and recent_hours>0:
        from_time=datetime.now()-timedelta(hours=recent_hours)
        filter_query["created_at"]={"$gte":from_time}

    try:
        cursor=(
            collection
            .find(filter_query)
            .sort("created_at",-1)
            .skip(offset)
            .limit(limit)
        )
        results=[]
        for doc in cursor:
            results.append(
                logOut(
                    _id=str(doc.get("_id")),
                    action_type=doc.get("action_type"),
                    user_id=str(doc.get("user_id")),
                    description=doc.get("description"),
                    created_at=doc.get("created_at"),
                )
            )
        return results
    except Exception as e:
        logger.exception("Error fetching logs: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))

