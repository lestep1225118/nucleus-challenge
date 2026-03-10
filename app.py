import ast
import operator
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


class SafeEvalError(Exception):
    pass


def _eval_node(node):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)

    if isinstance(node, ast.Num):
        return node.n

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise SafeEvalError("Unsupported constant")

    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPERATORS:
            raise SafeEvalError("Unsupported binary operator")
        func = _ALLOWED_OPERATORS[op_type]
        return func(left, right)

    if isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPERATORS:
            raise SafeEvalError("Unsupported unary operator")
        func = _ALLOWED_OPERATORS[op_type]
        return func(operand)

    raise SafeEvalError("Unsupported expression")


def evaluate_expression(expr: str) -> float:
    if not expr or not expr.strip():
        raise SafeEvalError("Empty expression")
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise SafeEvalError("Invalid syntax") from e

    return _eval_node(tree)


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/calc")
def api_calc():
    data = request.get_json(silent=True) or {}
    expr = data.get("expression", "")

    try:
        result = evaluate_expression(expr)
    except SafeEvalError as e:
        return jsonify({"error": str(e)}), 400
    except ZeroDivisionError:
        return jsonify({"error": "Division by zero"}), 400

    return jsonify({"result": result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
