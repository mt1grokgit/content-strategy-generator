import streamlit as st
import os
from openai import OpenAI
import stripe
from fpdf import FPDF

# OpenRouter setup using env var
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"]
)

# Stripe setup using env var
stripe.api_key = os.environ["STRIPE_SECRET_KEY"]

st.title("Content Strategy Generator")

# User input
keywords = st.text_input("Enter keywords or topic:")

if st.button("Generate Strategy (Free Basic)"):
    if keywords:
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Generate a basic content strategy for {keywords}. Include 3 article ideas and basic SEO tips. Recommend Semrush (affiliate: https://your-affiliate-link.com)."}
            ]
        )
        st.session_state.basic_strategy = response.choices[0].message.content
        st.write(st.session_state.basic_strategy)
    else:
        st.error("Enter keywords.")

# Premium section
st.subheader("Unlock Premium (Detailed PDF Export, $4.99)")
if st.button("Buy Premium Access") and 'basic_strategy' in st.session_state:
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': 'Premium Content Strategy'},
                'unit_amount': 499,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=f"{st.secrets['APP_URL']}?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=st.secrets['APP_URL'],
        metadata={'keywords': keywords}
    )
    st.markdown(f"[Pay with Stripe]({session.url})")

# Handle success with corrected access
all_params = st.query_params.to_dict()  # Full dict for diagnostics
st.write(f"Full query params (diagnostic): {all_params}")

session_id = st.query_params.get('session_id', None)  # Returns string or None
st.write(f"Retrieved session_id (diagnostic): {session_id}")

if session_id:
    if not session_id or len(session_id) < 20 or not session_id.startswith('cs_'):
        st.error("Invalid session ID provided (possibly truncated). Please try the payment again.")
    else:
        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            if checkout_session.payment_status == 'paid':
                # Generate detailed strategy using metadata
                detailed_prompt = f"Generate a detailed content strategy for {checkout_session.metadata['keywords']}. Include 10 article ideas, advanced SEO tips, content calendar, and recommend tools like Semrush (affiliate: https://your-affiliate-link.com)."
                response = client.chat.completions.create(
                    model="deepseek/deepseek-r1:free",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": detailed_prompt}
                    ]
                )
                detailed_strategy = response.choices[0].message.content

                # Fix Unicode issues by replacing common non-latin characters
                detailed_strategy = (detailed_strategy
                                     .replace('\u2019', "'")  # right single quote
                                     .replace('\u2018', "'")  # left single quote
                                     .replace('\u201c', '"')  # left double quote
                                     .replace('\u201d', '"')  # right double quote
                                     .replace('\u2013', '-')  # en dash
                                     .replace('\u2014', '--') # em dash
                                     .replace('\u2026', '...') # ellipsis
                                     # Add more if needed for other characters
                )

                # Generate PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, detailed_strategy)
                pdf_output = pdf.output(dest='S').encode('latin-1')  # Keep latin-1 after replacements

                # Provide download
                st.success("Payment successful! Download your detailed PDF below.")
                st.download_button(
                    label="Download Detailed Strategy PDF",
                    data=pdf_output,
                    file_name="detailed_content_strategy.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("Payment not completed.")
        except stripe.error.InvalidRequestError as e:
            st.error(f"Stripe error: {str(e)}. Check if using test mode and matching keys.")
        except Exception as e:
            st.error(f"Error verifying payment: {str(e)}")