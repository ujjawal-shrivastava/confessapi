import random
import string
import datetime


def random_string_generator(size=6, chars=string.digits):
    rand_number = int(''.join(random.choice(chars) for _ in range(size)))
    if(size==4):
        cmp_num=1000
    else:
        cmp_num=100000
    if rand_number<cmp_num:
        rand_number = random_string_generator(size=size)
    return str(rand_number)


def page_id_generator(instance):
    page_new_id= random_string_generator()

    Klass= instance.__class__
    qs_exists= Klass.objects.filter(pageId= page_new_id).exists()
    if qs_exists:
        return page_id_generator(instance)
    return page_new_id

def page_pin_generator(instance):
    page_new_id= random_string_generator(size=4)
    return page_new_id

def conf_id_generator(instance):
    x = datetime.datetime.now()
    x = x.strftime("%y%m%d")
    conf_new_id= x+str(random_string_generator(size=4))

    Klass= instance.__class__
    qs_exists= Klass.objects.filter(confId= conf_new_id).exists()
    if qs_exists:
        return conf_id_generator(instance)
    return conf_new_id


