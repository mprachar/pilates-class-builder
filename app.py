"""
Pilates Class Builder - Flask Web Application

Helps instructors build balanced Pilates classes with good flow.
"""

from flask import Flask, render_template, request, jsonify
from class_builder import ClassBuilder, CLASS_SECTIONS, EQUIPMENT_TYPES, EXPERIENCE_LEVELS
import database as db

app = Flask(__name__)
builder = ClassBuilder()


@app.route('/')
def index():
    """Main page with class builder form."""
    saved_classes = db.list_classes()
    return render_template(
        'index.html',
        sections=CLASS_SECTIONS,
        equipment=EQUIPMENT_TYPES,
        levels=EXPERIENCE_LEVELS,
        saved_classes=saved_classes
    )


@app.route('/generate', methods=['POST'])
def generate_class():
    """Generate a class based on user selections."""
    data = request.json

    class_length = int(data.get('class_length', 50))
    level = data.get('level', 'intermediate')
    equipment = data.get('equipment', ['reformer'])
    max_transitions = data.get('max_transitions')
    if max_transitions is not None:
        max_transitions = int(max_transitions)

    generated_class = builder.generate_class(
        duration_minutes=class_length,
        level=level,
        allowed_equipment=equipment,
        max_transitions=max_transitions
    )

    return jsonify(generated_class)


@app.route('/exercises')
def list_exercises():
    """List all exercises, optionally filtered."""
    section = request.args.get('section')
    equipment = request.args.get('equipment')
    level = request.args.get('level')

    exercises = builder.get_exercises(section=section, equipment=equipment, level=level)
    return jsonify(exercises)


@app.route('/exercises/by-section')
def exercises_by_section():
    """Get all exercises grouped by section (for exercise selection dropdowns)."""
    equipment_filter = request.args.getlist('equipment')
    level = request.args.get('level')

    result = {}
    for section in CLASS_SECTIONS:
        section_id = section["id"]
        exercises = builder.get_exercises(section=section_id, level=level)

        # Filter by equipment if specified
        if equipment_filter:
            exercises = [
                ex for ex in exercises
                if any(eq in equipment_filter for eq in ex["equipment"])
            ]

        result[section_id] = exercises

    return jsonify(result)


# ============ Saved Classes API ============

@app.route('/classes', methods=['GET'])
def list_saved_classes():
    """List all saved classes."""
    classes = db.list_classes()
    return jsonify(classes)


@app.route('/classes', methods=['POST'])
def save_new_class():
    """Save a new class."""
    data = request.json

    name = data.get('name', 'Untitled Class')
    description = data.get('description', '')
    class_data = data.get('class_data')

    if not class_data:
        return jsonify({"error": "class_data is required"}), 400

    class_id = db.save_class(class_data, name, description)
    return jsonify({"id": class_id, "message": "Class saved successfully"})


@app.route('/classes/<int:class_id>', methods=['GET'])
def get_saved_class(class_id):
    """Get a saved class by ID."""
    class_data = db.get_class(class_id)

    if not class_data:
        return jsonify({"error": "Class not found"}), 404

    # Add level_name from EXPERIENCE_LEVELS
    for level in EXPERIENCE_LEVELS:
        if level["id"] == class_data["level"]:
            class_data["level_name"] = level["name"]
            break

    # Reconstruct equipment_flow from sections
    equipment_flow = []
    seen = set()
    for section in class_data["sections"]:
        for ex in section["exercises"]:
            eq = ex.get("equipment")
            if eq and eq not in seen:
                equipment_flow.append(eq)
                seen.add(eq)
    class_data["equipment_flow"] = equipment_flow

    return jsonify(class_data)


@app.route('/classes/<int:class_id>', methods=['PUT'])
def update_saved_class(class_id):
    """Update a saved class."""
    data = request.json

    name = data.get('name')
    description = data.get('description')
    class_data = data.get('class_data')

    if not class_data:
        return jsonify({"error": "class_data is required"}), 400

    success = db.update_class(class_id, class_data, name, description)

    if not success:
        return jsonify({"error": "Class not found"}), 404

    return jsonify({"message": "Class updated successfully"})


@app.route('/classes/<int:class_id>', methods=['DELETE'])
def delete_saved_class(class_id):
    """Delete a saved class."""
    success = db.delete_class(class_id)

    if not success:
        return jsonify({"error": "Class not found"}), 404

    return jsonify({"message": "Class deleted successfully"})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
