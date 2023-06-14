
import re 
from func import model, numbers


def service_filter(line):
   '''Return true if we care about this string of text'''
   lline = line.lower()
  
   wordlist = [' ct',' ct', 'mri','magnetic','image','radio','ray ',' ray']
   for w in wordlist:
       if w in lline:
           return True

   return False



def line_to_charge(line):

    (bill_id, description, charge) = (None, None, None)
    (bill_id_pos, description_pos, charge_pos) = (None, None, None)

    split_line = []
    tokens = ['\t',',','    ']
    ltoken = None

    # TODO: deal with fix width files
    line = re.sub("([\d]{1,3}),([\d]{3})",r"\1\2", line.strip())
    for token in tokens:
        split_line = line.strip().split(token)
        if 1 < len(split_line) < 8:
            break
        split_line = []


    ops = list(range(len(split_line)))
    for i in ops:
        lsplit = split_line[i].strip()
        if len(lsplit) > 3:
            if lsplit[0] == '"' and lsplit[-1] == '"':
                lsplit = lsplit[1:-1]
            if lsplit[0] == "'" and lsplit[-1] == "'":
                lsplit = lsplit[1:-1]

        if charge_pos is None and '$' in lsplit:
            charge_pos = i
        elif charge_pos is None and len(lsplit) > 3 and lsplit[-3] == '.' and numbers.ismoney(lsplit.replace(',','')):
            charge_pos = i
        elif charge_pos is None and len(lsplit) > 3 and lsplit[-2] == '.' and numbers.isnumey(lsplit.replace(',','')):
            charge_pos = i
        elif charge_pos is None and len(lsplit) >= 5  and lsplit[-3] == ',' and numbers.ismoney(lsplit.replace(',','')):
            charge_pos = i
        elif charge_pos is None and numbers.ismoney(lsplit) and 0 < float(lsplit) < 10000:
            charge_pos = i
        elif lsplit.count(' ') > 0:
            description_pos = i
        elif bill_id_pos is None and len(lsplit) in [5,6]:
            bill_id_pos = i
        elif bill_id_pos is None and lsplit.count(' ') == 0 and 3 < len(lsplit) < 16:
            bill_id_pos = i
        print("lsplit:", '"%s"' % lsplit, charge_pos, numbers.ismoney(lsplit.replace(',','')), numbers.isnumey(lsplit.replace(',','')))

    lops = ops.copy()
    if bill_id_pos:
        lops.remove(bill_id_pos)
    if description_pos:
        lops.remove(description_pos)
    if charge_pos:
        lops.remove(charge_pos)


    if description_pos and charge_pos and len(lops) == 1:
        bill_id_pos = lops[0]
        lops.remove(bill_id_pos)
    if description_pos and bill_id_pos and len(lops) == 1 and numbers.ismoney(lsplit[lops[0]]):
        charge_pos = lops[0]
        lops.remove(charge_pos)

    if bill_id_pos is not None and len(split_line[bill_id_pos]) < 32:
        bill_id = split_line[bill_id_pos]
    if description_pos is not None:
        description = split_line[description_pos]
    if charge_pos is not None:
        try:
            lcharge = split_line[charge_pos]
            lcharge = re.sub("['\"$\,]","", lcharge)
            charge = float(lcharge)
        except Exception as e:
            print("can't convert to charge:", split_line[charge_pos], e)

    return (bill_id, description, charge)


def smoother(left, word, replace):

    left = left.replace(word, replace)
    return left

def kw_booster(left,right, key_words):

    lwithout = False
    for wow in key_words:
        if wow in left:
            lwithout = True

    rwithout = False
    for wow in key_words:
        if wow in right:
            rwithout = True

    if lwithout and rwithout:
        #print("boosted without", left, right)
        return 10
    if not lwithout and not rwithout:
        #print("boosted with", left, right)
        return 10
    return 0

