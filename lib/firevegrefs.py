import re

r = re.compile("[A-Z][a-z]+")
def extract_year(x):
    if x.__contains__("personal communication"):
        y = x[0:x.find(" personal")].replace(",","")
        year = "pers. comm."
    elif x.__contains__("unpublished"):
        y = x[0:x.find("unpublished")].replace(",","")
        year = "unpub."
    else:
        y = x[0:x.find(")")].replace(",","")
        year = ''.join(re.findall("\d+", y))
    return(year)

def extract_authors(x):
    authors = x[0:x.find("(")]
    return(authors)

def extract_rest(x):
    post_year = x[x.find(")")+1:]
    return(post_year)