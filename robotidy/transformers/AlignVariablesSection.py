from collections import defaultdict

from robot.api.parsing import (
    ModelTransformer,
    Token
)
from robot.parsing.model import Statement

from robotidy.utils import (
    node_outside_selection,
    round_to_four,
    tokens_by_lines,
    left_align
)


class AlignVariablesSection(ModelTransformer):
    """
    Align variables in *** Variables *** section to columns.

    Following code::

        *** Variables ***
        ${VAR}  1
        ${LONGER_NAME}  2
        &{MULTILINE}  a=b
        ...  b=c

    will be transformed to::

        *** Variables ***
        ${VAR}          1
        ${LONGER_NAME}  2
        &{MULTILINE}    a=b
        ...             b=c

    Supports global formatting params: ``--startline`` and ``--endline``.
    """

    def visit_VariableSection(self, node):  # noqa
        if node_outside_selection(node, self.formatting_config):
            return node
        statements = []
        for child in node.body:
            if node_outside_selection(child, self.formatting_config):
                statements.append(child)
            elif child.type in (Token.EOL, Token.COMMENT):
                statements.append(left_align(child))
            else:
                statements.append(list(tokens_by_lines(child)))
        nodes_to_be_aligned = [st for st in statements if isinstance(st, list)]
        if not nodes_to_be_aligned:
            return node
        look_up = self.create_look_up(nodes_to_be_aligned)  # for every col find longest value
        node.body = self.align_rows(statements, look_up)
        return node

    def align_rows(self, statements, look_up):
        aligned_statements = []
        for st in statements:
            if not isinstance(st, list):
                aligned_statements.append(st)
                continue
            aligned_statement = []
            for line in st:
                for index, token in enumerate(line[:-2]):
                    aligned_statement.append(token)
                    aligned_statement.append(Token(Token.SEPARATOR, (look_up[index] - len(token.value) + 4) * ' '))
                last_token = line[-2]
                # remove leading whitespace before token
                last_token.value = last_token.value.strip() if last_token.value else last_token.value
                aligned_statement.append(last_token)
                aligned_statement.append(line[-1])  # eol
            aligned_statements.append(Statement.from_tokens(aligned_statement))
        return aligned_statements

    @staticmethod
    def create_look_up(statements):
        look_up = defaultdict(int)
        for st in statements:
            for line in st:
                for index, token in enumerate(line):
                    look_up[index] = max(look_up[index], len(token.value))
        return {index: round_to_four(length) for index, length in look_up.items()}
