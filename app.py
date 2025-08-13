import streamlit as st
from openai import OpenAI
import stripe

# OpenRouter setup
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

# Stripe setup (unchanged)
stripe.api_key = "YOUR_STRIPE_SECRET_KEY"

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

# Premium section (unchanged)
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