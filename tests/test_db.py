from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):
    user = User(username="test", password="test", email="test@mail.com")
    session.add(user)
    session.commit()
    query = select(User).where(User.email == "test@mail.com")
    result = session.scalar(query)
    # session.refresh(user)
    assert result.username == "test"
    # assert user.id == 1
