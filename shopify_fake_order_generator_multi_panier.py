
import streamlit as st
import random
import requests
import json
import names
from faker import Faker
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="Fake Order Generator", layout="centered")
st.title("🛒 Shopify Fake Order Generator")

st.markdown("""
Cette application permet de générer automatiquement des commandes factices dans Shopify via l'API Admin, pour simuler de l'activité ou tester une boutique.

**⚠️ Utilisation réservée à des fins de test.**

### 📋 Permissions API nécessaires :
- ✅ read_orders  
- ✅ write_orders  
- ✅ read_customers  
- ✅ write_customers
""")

with st.expander("🧩 Paramètres de la boutique Shopify"):
    shopify_domain = st.text_input("🌐 Nom de domaine Shopify (ex: nomdeboutique.myshopify.com)")
    access_token = st.text_input("🔐 Access Token privé (Admin API)", type="password")

with st.expander("⚙️ Paramètres de génération"):
    quantity = st.slider("🔁 Nombre de commandes à créer", min_value=1, max_value=100, value=5)
    interval_value = st.slider("⏱️ Délai entre chaque commande (valeur)", min_value=1, max_value=60, value=5)
    interval_unit = st.selectbox("📅 Unité de temps pour le délai", options=["secondes", "minutes", "heures", "jours"])
    product_name = st.text_input("🛍️ Nom du produit simulé", value="Produit Fantôme")
    product_price = st.number_input("💸 Prix du produit simulé (€)", min_value=0.0, value=29.99, step=0.01)

multiplier = {"secondes": 1, "minutes": 60, "heures": 3600, "jours": 86400}
interval_seconds = interval_value * multiplier[interval_unit]

fake = Faker('fr_FR')

if st.button("🚀 Lancer la génération"):
    if not all([shopify_domain, access_token]):
        st.error("Merci de remplir tous les champs obligatoires.")
    else:
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": access_token
        }
        created = 0
        for i in range(quantity):
            gender = random.choice(['male', 'female'])
            first_name = names.get_first_name(gender=gender)
            last_name = names.get_last_name()

            address = {
                "first_name": first_name,
                "last_name": last_name,
                "address1": fake.street_address(),
                "phone": fake.phone_number(),
                "city": fake.city(),
                "province": fake.region(),
                "country": "France",
                "zip": fake.postcode()
            }

            random_hour = random.randint(0, 23)
            random_minute = random.randint(0, 59)
            created_at = datetime.now().replace(hour=random_hour, minute=random_minute, second=0, microsecond=0).isoformat()

            order_data = {
                "order": {
                    "line_items": [{
                        "title": product_name,
                        "price": str(product_price),
                        "quantity": 1
                    }],
                    "customer": {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": f"{first_name.lower()}.{last_name.lower()}@example.com"
                    },
                    "billing_address": address,
                    "shipping_address": address,
                    "financial_status": "paid",
                    "created_at": created_at
                }
            }

            response = requests.post(
                f"https://{shopify_domain}/admin/api/2023-10/orders.json",
                headers=headers,
                data=json.dumps(order_data)
            )

            if response.status_code == 201:
                created += 1
                st.info(f"✅ Commande {i+1} créée : {first_name} {last_name}")
            else:
                st.error(f"Erreur à la commande {i+1} : {response.text}")

            time.sleep(interval_seconds)

        st.success(f"🎉 {created} commandes aléatoires ont été créées avec succès !")
