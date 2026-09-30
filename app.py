# Libraries

import streamlit as st
import io, os
from groq import Groq
from dotenv import load_dotenv
from PIL import Image
import json
import base64
from datetime import date

from database import save_document, TransactionData 


# Setting the configuration

load_dotenv()

st.set_page_config(
    page_title="PHOTON AI RECEIPT SCANNER",
    layout="wide",
)


API_Key = st.secrets["GROQ_API_KEY"]
DATABASE_url = st.secrets["DATABASE_URL"]

# Setting-up the client

client = None

if API_Key:
    client = Groq(api_key=API_Key)
else:
    st.error(
        "Groq API key is not configured. "
        "Please add GROQ_API_KEY to Streamlit secrets."
    )

# Setting upu our receipt schema

RECEIPT_SCHEMA = {
    "type": "object",
    "properties": {
        "store": {
            "type": ["string", "null"]
        },
        "customer_id": {
            "type": ["string", "null"]
        },
        "transaction_date": {
            "type": ["string", "null"]
        },
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "product": {
                        "type": "string"
                    },
                    "total_price": {
                        "type": "number"
                    },
                    "quantity": {
                        "type": "integer"
                    }
                },
                "required": [
                    "product",
                    "total_price",
                    "quantity"
                ],
                "additionalProperties": False
            }
        }
    },
    "required": [
        "store",
        "customer_id",
        "transaction_date",
        "items"
    ],
    "additionalProperties": False
}


AI_PROMPT = """
Analyze this image as a receipt and extract only:

- store: store name
- customer_id: customer ID, if visible
- transaction_date: transaction date
- items: every purchased product separately, with:
  - product: product name
  - quantity: number purchased
  - total_price: total amount charged for that product line

Instructions:
- Capture every item separately; never combine different products.
- Use the line-item total printed on the receipt as total_price.
- Do not return unit price.
- Do not calculate total_price from unit price.
- You may use quantity × unit price to verify the line total, but do not return the calculated value if a line total is shown.
- Do not use the receipt subtotal, tax, discount, grand total, payment amount, or change as an item's total_price.
- If quantity is not shown but one item is clearly purchased, use 1.
- Do not invent unreadable or missing information; use null where appropriate.
- If handwriting is present, do your best to read it.
- Preserve product names as they appear.
- Return the transaction date as YYYY-MM-DD when possible.
"""

# Setting up image (Image to text)

def image_text(image:Image.Image) -> str:
    """
    Convert the uploaded image to a base64 data url
    """
    image = image.convert("RGB")

    buffer=io.BytesIO()
    image.save(buffer, format="JPEG")

    encoded_image=base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:image/jpeg;base64,{encoded_image}"

# USER INTERFACE DESIGN
st.title("PHOTON AI RECEIPT SCANNER")

st.write(
    "Upload a receipt and extract the shopping details."
)

uploaded_file = st.file_uploader(
    "upload Receipt",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)

    st.image(
        image, caption="Uploaded receipt", width="stretch"
    )

    analyse_button = st.button(
        "Analyse Receipt", type="primary"
    )

    if analyse_button:
        with st.spinner("Reading receipt..."):
            try:
                image_url=image_text(image)

                response=client.chat.completions.create(
                    model="qwen/qwen3.8-27b",
                    messages=[{
                        "role":"user", "content":[{
                            "type":"text",
                            "text":AI_PROMPT
                        },
                        {"type":"image_url",
                        "image_url":{
                            "url":image_url
                        }
                        }
                        ]
                    }],
                response_format={
                    "type":"json_schema", 
                    "json_schema":{
                        "name":"receipt_extraction",
                        "strict":True,
                        "schema":RECEIPT_SCHEMA
                    }
                },

                reasoning_effort="none",

                temperature=0.2,
                max_completion_tokens=800
                )

                # RESULT- AI OUTPUT

                result_text=(response.choices[0].message.content)

                receipt_data=json.loads(result_text)

                # Extraction into receipt format

                store=receipt_data.get("store")
                customer_id = receipt_data.get("customer_id")
                transaction_date=receipt_data.get("transaction_date")

                items=receipt_data.get("items",[])

                # Simple validation series

                if not items:
                    st.warning("No purchased items could be detected from this receipt")

                    st.stop()

                if not store:
                    store="Unknown"

                if not customer_id:
                    customer_id="N/A"

                if transaction_date:
                    try:
                        transaction_date=date.fromisoformat(transaction_date)

                    except ValueError:
                        st.warning("The transaction date could not be interpreted correctly")

                        transaction_date=None
                else:
                    transaction_date=None


                # Data display

                table_data=[]

                for item in items:
                    table_data.append({"Product":item["product"],
                                       "TotalPrice":item["total_price"],
                                       "Quantity":item["quantity"]
                                       })

                # Receipt info

                st.header("Receipt information")

                col1, col2, col3=st.columns(3)

                with col1:
                    st.write("STORE")
                    st.write(store)

                with col2:
                    st.write("CUSTOMER ID")
                    st.write(customer_id)

                with col3:
                    st.write("TRANSACTION DATE")

                    if transaction_date:
                        st.write(
                            transaction_date.strftime("%Y-%m-%d")
                        )
                    else:
                        st.write("Not available")

                # Product

                st.subheader("Purchased Items")
                st.dataframe(table_data, use_container_width=True,
                             hide_index=True)


                #Save into Database

                saved_count=0

                for item in items:
                    transaction = TransactionData(
                        store=store,
                        customer_id=customer_id,
                        product=item["product"],
                        total_price=item["total_price"],
                        quantity=item["quantity"],
                        transaction_date=transaction_date
                        )

                    save_document(transaction)
                    saved_count+=1

                st.success(f"Receipt successfully analysed."
                        f"{saved_count} items saved to the database")

            except json.JSONDecodeError:
                st.error(
                    "The AI returned data that could not be processed."
                    "Please try again"
                )

            except Exception as e:
                st.error(f"Unable to process the receipt: {e}")