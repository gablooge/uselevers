from sqlalchemy.orm import Session

from . import models, schemas


def save_billspec(db: Session, bill_data: schemas.BillSpec) -> models.Bill:
    # Create a new instance of models.Bill directly
    bill = models.Bill(total=bill_data.total)
    # Process sub_bills
    for sub_bill_data in bill_data.sub_bills:
        sub_bill = models.SubBill(
            amount=sub_bill_data.amount, reference=sub_bill_data.reference
        )
        bill.sub_bills.append(sub_bill)

    db.add(bill)
    db.flush()
    return bill
