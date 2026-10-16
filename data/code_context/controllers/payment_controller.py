class PaymentController:

    def create_payment(self, request):
        try:
            payment = self.payment_service.create_payment(request)

            return {
                "status": "completed",
                "payment": payment,
            }

        except Exception as exc:
            raise RuntimeError(
                "Payment creation failed"
            ) from exc