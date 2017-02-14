
#nothing to import
#never import anything

def prepend_list_in_key_of_dict(dict_obj, dict_key_of_list, element):
    elements = dict_obj.get(dict_key_of_list, [])
    elements_set = set(elements)
    if element not in elements_set:
        elements.insert(0, element)
        dict_obj[dict_key_of_list] = elements
        return True
    return False

def append_list_in_key_of_dict(dict_obj, dict_key_of_list, element):
    elements = dict_obj.get(dict_key_of_list, [])
    elements_set = set(elements)
    if element not in elements_set:
        elements.append(element)
        dict_obj[dict_key_of_list] = elements
        return True
    return False

def remove_list_in_key_of_dict(dict_obj, dict_key_of_list, element):
    elements = dict_obj.get(dict_key_of_list, [])
    elements_set = set(elements)
    if element in elements_set:
        elements.remove(element)
        dict_obj[dict_key_of_list] = elements
        return True
    return False
