from cStringIO import StringIO

def renderForm(annotation, elements):

    result = StringIO()

    w = result.write

    w('<table border="0" cellspacing="0" cellpadding="2">')
    w('<tr>')
    
    for e in elements:
        pass
