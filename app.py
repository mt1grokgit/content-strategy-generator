import streamlit as st
import os
from openai import OpenAI
import stripe

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
            model="deepseek/deepseek-r1:free",  # Valid free chat model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Generate a detailed content strategy for {keywords}. Include 5 article ideas, SEO tips, and recommend tools like Semrush (affiliate link: https://your-affiliate-link.com)."}
            ]
        )
        st.write(response.choices[0].message.content)
    else:
        st.error("Enter keywords.")

# Premium section
st.subheader("Unlock Premium (Detailed PDF Export, $4.99)")
if st.button("Buy Premium Access"):
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
        success_url='https://your-domain.com/success',
        cancel_url='https://your-domain.com/cancel',
    )
    st.markdown(f"[Pay with Stripe]({session.url})")