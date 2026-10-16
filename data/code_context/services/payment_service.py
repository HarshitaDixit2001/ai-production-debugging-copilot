class PaymentService:

    def create_payment(self, payment_request):
        payment = {
            "order_id": payment_request["order_id"],
            "amount": payment_request["amount"],
            "currency": payment_request["currency"],
        }

        # Payment record is created before transaction ID generation.
        self.repository.insert_payment(payment)

        transaction_id = self.generate_transaction_id()

        return {
            "payment": payment,
            "transaction_id": transaction_id,
        }

    def generate_transaction_id(self):
        return "TXN-GENERATED"