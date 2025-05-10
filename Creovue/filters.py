# Creovue/filters.py
def format_number(value):
    try:
        return "{:,}".format(int(value))
    except:
        return value
