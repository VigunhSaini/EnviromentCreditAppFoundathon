"""
utils/decorators.py
Shared Flask decorators for input validation and unified error handling.
"""
import functools
from flask import request, jsonify


def require_json(*required_fields):
    """
    Decorator that:
      1. Ensures the request Content-Type is application/json.
      2. Parses the JSON body.
      3. Validates that all *required_fields* keys are present and non-empty.

    Usage:
        @require_json("name", "type", "ngo_id")
        def create_project():
            data = request.get_json()
            ...
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({"success": False, "error": "Content-Type must be application/json"}), 415

            data = request.get_json(silent=True)
            if data is None:
                return jsonify({"success": False, "error": "Invalid or empty JSON body"}), 400

            missing = [f for f in required_fields if f not in data or data[f] in (None, "")]
            if missing:
                return jsonify(
                    {
                        "success": False,
                        "error": f"Missing required fields: {', '.join(missing)}",
                    }
                ), 400

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def handle_errors(fn):
    """
    Decorator that catches unhandled exceptions inside a route and returns a
    structured JSON error response instead of a 500 HTML page.

    Usage:
        @handle_errors
        def my_route():
            ...
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValueError as exc:
            return jsonify({"success": False, "error": str(exc)}), 400
        except PermissionError as exc:
            return jsonify({"success": False, "error": str(exc)}), 403
        except FileNotFoundError as exc:
            return jsonify({"success": False, "error": str(exc)}), 404
        except Exception as exc:  # pylint: disable=broad-except
            # Log to server console for debugging; don't expose raw tracebacks
            import traceback
            traceback.print_exc()
            return (
                jsonify({"success": False, "error": "An internal server error occurred."}),
                500,
            )
    return wrapper
