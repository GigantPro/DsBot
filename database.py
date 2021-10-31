import json

def create(file_name = 'data_base.json'):
    try:
        data = json.load(open(file_name))
    except:
        data = []
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=True)

def json_write(base):
    with open('data_base.json', 'w', encoding='utf-8') as file:
        json.dump(base, file, indent=2, ensure_ascii=True)

def json_read_login(discord):
        temp_bool = False
        with open('data_base.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            for discords in data:
                if discords['discord'] == discord:
                    temp_bool = discords['login']
        return temp_bool

def json_read_pass(discord):
        with open('data_base.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            for discords in data:
                if discords['discord'] == discord:
                    return discords['passwd']

                    
def set_bad_word(bad_word, file_name = 'data_base_bad_words.json'):
    try:
        data = json.load(open(file_name))
    except:
        data = []
    data.append(bad_word)
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=True)

def json_read(file_name = 'data_base_bad_words.json'):
        temp_bool = False
        with open('data_base.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
        return temp_bool

def del_bad_word(bad_word, file_name = 'data_base_bad_words.json'):
    temp_data = []
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            temp = json.load(file)
            for bads in temp:
                if bads != bad_word:
                    temp_data.append(bads['bad'])
    except:
        return 'error'
    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(temp_data, file, indent=2, ensure_ascii=True)
    except:
        return 'error'

def json_write_passport(discord, names, warns, banned_server_names, banned_counter, time_limit_warn, road='pass_base.json'):
    temp = {'discord_num' : discord[-5:], 'names' : names, 'banned_server_names' : banned_server_names, 'banned_counter' : banned_counter, 'time_limit_warn' : time_limit_warn}
    try:
        data = json.load(open(road))
    except:
        data = []
    data.append(temp)

    with open(road, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=True)

def json_read_passport(road='pass_base.json'):
        with open('data_base.json', 'r', encoding='utf-8') as file:
            return(json.load(file))
