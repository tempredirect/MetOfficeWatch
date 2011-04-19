from webapp import app
from decimal import Decimal

@app.template_filter('money')
def money(i):
    d = Decimal(str(i) + '.00')
    d /= 100

    return u'\u00A3' + str(d)


if __name__ == '__main__':
    print "money(120) : %s" % money(120)