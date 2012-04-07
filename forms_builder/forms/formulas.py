
import parser

from UserDict import DictMixin


class FormulaCalculator(DictMixin):

    def __init__(self, fields, data):
        self.fields = fields
        self.data = data
        self.depth = 0

    def calculate_item(self, formula):
        self.depth += 1
        if self.depth >= 20:
            raise RuntimeError('maximum recursion depth in form exceeded')
        e = parser.expr(formula).compile()
        val = eval(e,{},self)
        self.depth -= 1
        return val

    def calculate_formulas(self):
        formulas = {}
        l = open('/tmp/tmp.log', 'a')
        for field in self.fields:
            field_key = "field_%s" % field.id 
            l.write('%s: %s\n' % (field.id, field.default))
            if not field.default or field.default[0] != '=': # no formula here
                continue 
            formula = field.default[1:]
            if not formula:
                continue
            formulas[field_key] = formula

        for field_key in formulas.keys():
            self.data[field_key] = self.calculate_item(formulas[field_key])

        l.close()

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        item = self.data[key]
        if item:
            return item
        return self.calculate_item(formulas[key])

    def __delitem__(self, key):
        del self.data[key]

    def keys(self):
        return self.data.keys()

