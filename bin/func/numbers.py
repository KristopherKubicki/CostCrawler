
def ismoney(money):
    money = str(money)
    if money.isdigit(): return True
    else:
        try:
            new = "%.2f" % float(money)
            return new == money
        except: return False

def isnumey(money):
    money = str(money)
    if money.isdigit(): return True
    else:
        try:
            new = "%.1f" % float(money)
            return new == money
        except: return False

