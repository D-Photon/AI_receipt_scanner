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
