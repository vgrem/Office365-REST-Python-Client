import ast

import astunparse


class TypeBuilder:

    def __init__(self, schema):
        self._schema = schema
        self._node = None

    def build(self, options):
        if self._schema['state'] == 'attached':
            with open(self._schema['file']) as f:
                self._node = ast.parse(f.read())
            return True
        else:
            with open(options['complexTypeFile']) as f:
                self._node = ast.parse(f.read())
            return False

    def save(self):
        code = astunparse.unparse(self._node)
        with open(self._schema['file']) as f:
            f.write(code)
