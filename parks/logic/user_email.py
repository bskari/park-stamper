from parks.models import DBSession
from parks.models import UserEmail


def get_emails_by_user_id(user_id):
    emails = DBSession.query(
        UserEmail,
    ).filter(
        UserEmail.user_id == user_id
    ).all()

    return emails
