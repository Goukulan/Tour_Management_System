import enum
class PaymentStatusEnum(str, enum.Enum):
    created = "created"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class BookingStatusEnum(str, enum.Enum):
    pending = "pending"        # seat held, awaiting payment
    confirmed = "confirmed"    # payment done, seat locked in
    ongoing = "ongoing"        # departure has started
    completed = "completed"    # departure finished
    cancelled = "cancelled"
    refunded = "refunded"