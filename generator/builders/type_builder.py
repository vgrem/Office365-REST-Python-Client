import ast
import os
from os.path import abspath
from pydoc import locate

import astunparse


class TypeBuilder(ast.NodeTransformer):

    def __init__(self, type_schema, options):
        """
        :type type_schema: office365.runtime.odata.type.ODataType
        :type options: dict
        """
        self._schema = type_schema
        self._options = options
        self._type_info = None
        self._source_tree = None
        self._status = None

    def generic_visit(self, node):
        if isinstance(node, ast.ClassDef):
            node.name = self._schema.name.title()
        ast.NodeVisitor.generic_visit(self, node)

    def build(self):
        if self.state == 'attached':
            with open(self.file) as f:
                self._source_tree = ast.parse(f.read())
            self._status = "updated"
        else:
            template_file = self._resolve_template_file(self._schema.baseType)
            with open(template_file) as f:
                self._source_tree = ast.parse(f.read())
            self._status = "created"
        self.visit(self._source_tree)
        return self

    def save(self):
        code = astunparse.unparse(self._source_tree)
        with open(self.file, 'w') as f:
            f.write(code)

    def _resolve_template_file(self, type_name):
        file_mapping = {
            "ComplexType": "complex_type.py",
            "EntityType": "entity_type.py"
        }
        path = abspath(os.path.join(self._options['templatePath'], file_mapping[type_name]))
        return path

    def _resolve_type(self, type_name):
        """
        :type type_name: str
        """
        type_info = {}
        namespaces = ['directory', 'onedrive', 'mail', 'teams']
        types = [locate("office365.{0}.{1}".format(ns, type_name)) for ns in namespaces]
        found_modules = [t for t in types if t is not None]
        if any(found_modules):
            type_info['state'] = 'attached'
            type_info['file'] = found_modules[0].__file__
        else:
            type_info['state'] = 'detached'
            type_info['file'] = abspath(os.path.join(self._options['outputPath'], type_name + ".py"))
        return type_info

    def _ensure_type_info(self):
        if self._type_info is None:
            self._type_info = self._resolve_type(self._schema.name)
        return self._type_info

    @property
    def state(self):
        self._ensure_type_info()
        return self._type_info['state']

    @property
    def file(self):
        self._ensure_type_info()
        return self._type_info['file']

    @property
    def status(self):
        return self._status
