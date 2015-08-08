#encoding=utf8
from .models import User 
from django.db.models import Q
import xlrd, random
from django.contrib import messages

def random_str(length):
    string = ''
    for _ in xrange(length):
        string += random.choice('0123456789')

    return string

def import_users_from_excel(request):
    try:
        workbook = xlrd.open_workbook(file_contents = request.FILES['users'].read())
        data_sheet = workbook.sheet_by_name('DATA')

        nicknames = []
        usernames = []

        for i in xrange(data_sheet.nrows):
            data = data_sheet.row_values(i)
            nicknames.append(data[1])
            usernames.append(data[0])

        duplicated = User.objects.filter(Q(username__in = usernames) | Q(nickname__in = nicknames)).only('nickname', 'username')
        duplicated_nicknames = map(lambda u: u.nickname, duplicated)
        duplicated_usernames = map(lambda u: u.username, duplicated)

        if len(duplicated):
            messages.info(request, u'昵称为 {0} 的用户已经存在。'.format(
                    u'，'.join(duplicated_nicknames)
                )
            )

        results = []
        users = []
        for i in xrange(len(nicknames)):
            print nicknames[i], duplicated_nicknames
            if nicknames[i] in duplicated_nicknames or usernames[i] in duplicated_usernames:
                continue

            result_dict = (usernames[i], nicknames[i], random_str(6))
            results.append(result_dict)
            user = User(username = result_dict[0], nickname = result_dict[1])
            user.set_password(result_dict[2])
            user.password_raw = result_dict[2]
            print result_dict, user, users
            users.append(user)

        User.objects.bulk_create(users)
        print users
        return users
    except:
        messages.warning(request, '出错了！请检查数据格式')
        return []