import ast
import os


import astunparse


class TypeBuilder(ast.NodeTransformer):

    def __init__(self, options):
        self._schema = None
        self._options = options

    def generic_visit(self, node):
        if isinstance(node, ast.ClassDef):
            node.name = self._schema["name"].title()
        ast.NodeVisitor.generic_visit(self, node)

    def build(self, schema):
        result = dict(status=None, output_file=None, source_tree=None)
        if schema['state'] == 'attached':
            result.output_file = schema['file']
            with open(schema['file']) as f:
                result["source_tree"] = ast.parse(f.read())
            result["status"] = "updated"
        else:
            template_file = self._resolve_template_file(schema['baseType'])
            result["output_file"] = os.path.join(self._options['outputPath'], schema["name"] + ".py")
            with open(template_file) as f:
                result["source_tree"] = ast.parse(f.read())
            result["status"] = "created"
        self._schema = schema
        self.visit(result["source_tree"])
        return result

    def save(self, result):
        code = astunparse.unparse(result["source_tree"])
        with open(result["output_file"], 'w') as f:
            f.write(code)

    def _resolve_template_file(self, type_name):
        file_mapping = {
            "ComplexType": "complex_type.py",
            "EntityType": "entity_type.py"
        }
        path = os.path.join(self._options['templatePath'], file_mapping[type_name])
        return path
