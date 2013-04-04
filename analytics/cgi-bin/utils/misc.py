
def is_live():
    
    try:
        x = open("/is_live","r")
        return True

    except:
        return False
    
