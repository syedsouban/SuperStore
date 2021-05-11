from app import app

@app.route("/checkout", methods=["POST"])
def checkout():
    payload = request.get_json()
    payment_details = payload.get("payment_details")
    pass
    # user_cart = 