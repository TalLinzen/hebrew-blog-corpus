from .db import User

def select_distinct(field, user):
    query = "select distinct %s from web_page where user='%s'" % (field, user)
    results = User._connection.queryAll(query)
    return [res[0] for res in results]

def fill_user_table():
    User.dropTable()
    User.createTable()
    users = User._connection.queryAll('select distinct user from web_page')
    users = [x[0] for x in users]
    query = "select distinct %s from web_page where user='%s'"
    for i, user in enumerate(users):
        print i, user
        birthyears = select_distinct('birthyear', user)
        candidates = [int(by) for by in birthyears 
                if by is not None]
        birthyear = min(candidates) if len(candidates) != 0 else None

        ages = select_distinct('age', user)
        age = ages[0] if len(ages) != 0 else None

        sexes = select_distinct('sex', user)
        sex = sexes[0] if len(sexes) != 0 else None

        chars = User._connection.queryAll(
                "select sum(length(clean_text)) "
                "from web_page where user='%s'" % user)
        chars = int(chars[0][0])
        User(number=user, age=age, sex=sex, chars=chars, birthyear=birthyear)

