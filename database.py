import streamlit as st
from sqlalchemy import create_engine, text
from psycopg.types.json import Jsonb
from typing import Optional
import psycopg
from pydantic import BaseModel
from datetime import date

DATABASE_URL = st.secrets["DATABASE_URL"]

engine = create_engine(DATABASE_URL)


class TransactionData(BaseModel):
    store:str
    customer_id:str
    product:str
    total_price:float
    quantity:int
    transaction_date:Optional[date]=None


def save_document(info:TransactionData):
    with engine.begin() as connection:
        result = connection.execute(
            text("""
                INSERT INTO transaction_doc (
                store,
                customer_id,
                product,
                total_price,
                quantity,
                transaction_date)

                VALUES(
                :store,
                :customer_id,
                :product,
                :total_price,
                :quantity,
                :transaction_date)

                RETURNING id
            """),
            {
                "store":info.store,
                "customer_id":info.customer_id,
                "product":info.product,
                "total_price":info.total_price,
                "quantity":info.quantity,
                "transaction_date":info.transaction_date
            }
        )

        document_id = result.scalar()

    return document_id

    