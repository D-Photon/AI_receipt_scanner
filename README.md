# AI Receipt Scanner

An AI-powered receipt processing application that uses a vision-language model to extract structured transaction information from receipt images 
and store the extracted records in a PostgreSQL database.

The application is built with Streamlit, uses Groq's hosted Qwen vision model for image understanding, and stores transaction records in Neon PostgreSQL. 
The entire application is containerized with Docker.

## Project Overview

Manually entering information from receipts can be time-consuming and error-prone. 
This project automates the process by allowing a user to upload a receipt image and automatically extract relevant transaction information.

The system extracts:

- Store name
- Customer ID
- Transaction date
- Product name
- Quantity
- Total price for each product line

The extracted information is displayed in a clean table and can then be stored in a PostgreSQL database.

## Schema Design

There are three schemas designed in this project
- The RECEIPT SCHEMA; 
Defines the structured output expected from the Qwen vision model. It specifies the fields to extract from the receipt, including store, customer ID, transaction date, and individual line items. It also defines how missing values should be represented, helping maintain a consistent AI response.

- The APPLICATION SCHEMA; 
Defines how the extracted receipt data is represented and handled within the application before being displayed or saved. It acts as the bridge between the AI response, the Streamlit interface, and the database layer.

- The DATABASE SCHEMA; 
Defines how the extracted transaction records are stored in PostgreSQL. The application uses Pydantic validation and data formatting before inserting the extracted information into the corresponding PostgreSQL fields, ensuring that the data conforms to the expected database types.

## System Architecture

```text
Receipt Image
      │
 Streamlit App
      │
 Groq API
      │
 Qwen Vision Model
      │
 Structured Receipt Data
      │
 Streamlit Data Table
      │
 SQLAlchemy + Psycopg
      │
 Neon PostgreSQL
