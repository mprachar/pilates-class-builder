"""
Class Builder Logic

Generates balanced Pilates classes based on section flow and rules.

FLOW RULES:
1. Footwork is ALWAYS first, Stretch is ALWAYS last
2. Middle 8 sections (Bridges through Full Body) can be reordered for better flow
3. Equipment transitions must be contiguous - no returning to equipment after leaving
   (e.g., Reformer→Chair→Springboard OK, but Reformer→Chair→Reformer NOT OK)
4. Minimize spring changes within same equipment
5. Advanced classes: fewer reps but more exercises; Beginner: more reps, fewer exercises
"""

import random
from dataclasses import dataclass, field
from typing import Optional
from itertools import permutations

# Class sections - Footwork first, Stretch last, middle 8 flexible
FIXED_FIRST = {"id": "footwork", "name": "Footwork", "order": 1, "typical_minutes": 5}
FIXED_LAST = {"id": "stretch", "name": "Stretch", "order": 10, "typical_minutes": 5}

# Middle sections can be reordered for optimal flow
FLEXIBLE_SECTIONS = [
    {"id": "bridges", "name": "Bridges", "typical_minutes": 5},
    {"id": "abdominals", "name": "Abdominals", "typical_minutes": 7},
    {"id": "plank", "name": "Plank", "typical_minutes": 5},
    {"id": "upper_body", "name": "Upper Body", "typical_minutes": 7},
    {"id": "lower_body", "name": "Lower Body", "typical_minutes": 7},
    {"id": "lateral_line", "name": "Lateral Line", "typical_minutes": 5},
    {"id": "prone_extension", "name": "Prone/Extension", "typical_minutes": 5},
    {"id": "full_body", "name": "Full Body Integration", "typical_minutes": 5},
]

# Default section order (can be optimized)
CLASS_SECTIONS = [FIXED_FIRST] + FLEXIBLE_SECTIONS + [FIXED_LAST]

EQUIPMENT_TYPES = [
    {"id": "reformer", "name": "Reformer"},
    {"id": "chair", "name": "Chair"},
    {"id": "springboard", "name": "Springboard"},
    {"id": "mat", "name": "Mat"},
    {"id": "trx", "name": "TRX"},
    {"id": "bosu", "name": "BOSU"},
    {"id": "barrel", "name": "Barrel"},
]

EXPERIENCE_LEVELS = [
    # max_transitions based on sample classes (~6 for all levels)
    {"id": "beginner", "name": "Beginner (Level 1)", "level_num": 1.0, "rep_multiplier": 1.2, "exercise_count_multiplier": 0.8, "max_transitions": 6},
    {"id": "intermediate", "name": "Intermediate (Level 1.5)", "level_num": 1.5, "rep_multiplier": 1.0, "exercise_count_multiplier": 1.0, "max_transitions": 6},
    {"id": "advanced", "name": "Advanced (Level 2)", "level_num": 2.0, "rep_multiplier": 0.85, "exercise_count_multiplier": 1.15, "max_transitions": 6},
    {"id": "advanced_plus", "name": "Advanced+ (Level 2.5)", "level_num": 2.5, "rep_multiplier": 0.75, "exercise_count_multiplier": 1.25, "max_transitions": 8},
]


@dataclass
class Exercise:
    """Represents a single exercise."""
    id: str
    name: str
    section: str
    equipment: list[str]
    level: str  # beginner, intermediate, advanced, advanced_plus
    spring_setting: str = ""  # e.g., "1R + 1B", "2R", helps with flow optimization
    reps: int = 8  # Default reps from manual guidelines
    duration_seconds: int = 60  # Calculated from reps × sec_per_rep
    variations: list[str] = field(default_factory=list)
    props: list[str] = field(default_factory=list)
    notes: str = ""
    uses_box: bool = False  # True if exercise uses the long or short box


# Seed exercise database with spring settings and rep counts from CPTT manuals
# Rep counts are based on manual guidelines; duration = reps × seconds_per_rep
EXERCISES = [
    # Footwork (typically heavier springs) - Manual: 8-10 reps per position
    Exercise("fw_heels_bilateral", "Heels - Bilateral", "footwork", ["reformer", "chair"], "beginner",
             spring_setting="3R or 2R+1B", reps=10, duration_seconds=45,
             variations=["Parallel", "V Position", "Wide", "Narrow"]),
    Exercise("fw_toes_bilateral", "Toes - Bilateral", "footwork", ["reformer", "chair"], "beginner",
             spring_setting="3R or 2R+1B", reps=10, duration_seconds=45,
             variations=["Parallel", "V Position", "Wide", "Narrow"]),
    Exercise("fw_arches", "Arches", "footwork", ["reformer", "chair"], "beginner",
             spring_setting="3R or 2R+1B", reps=10, duration_seconds=45),
    Exercise("fw_single_leg", "Single Leg Footwork", "footwork", ["reformer", "chair"], "intermediate",
             spring_setting="2R or 1R+1B", reps=8, duration_seconds=60,
             variations=["Toe Tap", "Ball & Socket", "Leg & Leg", "Develope", "Circles"]),
    Exercise("fw_standing", "Standing Footwork", "footwork", ["springboard"], "beginner",
             spring_setting="", reps=10, duration_seconds=60),
    Exercise("fw_side_lying", "Side Lying Footwork", "footwork", ["reformer"], "intermediate",
             spring_setting="1R+1B", reps=8, duration_seconds=60,
             variations=["Parallel", "External Rotation", "Internal Rotation", "High Half Toe"]),

    # Bridges (medium springs) - Manual: 5 reps, 3 reps for shoulder bridge
    Exercise("br_articulating", "Articulating Bridge", "bridges", ["mat"], "beginner",
             spring_setting="", reps=5, duration_seconds=60),
    Exercise("br_pelvic_lift", "Pelvic Lift/Hinge Bridge", "bridges", ["mat"], "beginner",
             spring_setting="", reps=5, duration_seconds=45),
    Exercise("br_single_leg", "Single Leg Bridge", "bridges", ["mat"], "advanced",  # CPTT: A
             spring_setting="", reps=5, duration_seconds=60),
    Exercise("br_shoulder_bridge", "Shoulder Bridge", "bridges", ["mat", "reformer"], "intermediate",
             spring_setting="1R+1B", reps=3, duration_seconds=60),
    Exercise("br_reformer_bilateral", "Bridge - Bilateral", "bridges", ["reformer"], "beginner",
             spring_setting="1R+1B", reps=5, duration_seconds=60,
             variations=["Heels", "Toes", "Arches"], props=["Magic Circle", "Ball", "Dumbbell", "Band"]),
    Exercise("br_reformer_unilateral", "Bridge - Unilateral", "bridges", ["reformer"], "intermediate",
             spring_setting="1R+1B", reps=5, duration_seconds=60,
             variations=["Marches", "Hip Drops", "Leg Circle"]),
    Exercise("br_hamstring_curl", "Heels on Hamstring Curl", "bridges", ["chair"], "intermediate",
             spring_setting="2@2", reps=5, duration_seconds=60),
    Exercise("br_pedal_bridge", "Bridge with Feet on Pedal", "bridges", ["chair"], "intermediate",
             spring_setting="2@2", reps=5, duration_seconds=60),
    Exercise("br_frog_back", "Frog Back", "bridges", ["chair"], "intermediate",
             spring_setting="2@2", reps=5, duration_seconds=60),
    Exercise("br_trx_hip_lift", "TRX Hip Lift", "bridges", ["trx"], "intermediate",
             spring_setting="", reps=5, duration_seconds=60),

    # Abdominals (light-medium springs) - Manual: Hundred=10 cycles, Coordination=5 reps
    Exercise("ab_hundred", "Hundred", "abdominals", ["mat", "reformer"], "intermediate",  # CPTT: I/A mat, I reformer
             spring_setting="1R or 1B", reps=10, duration_seconds=90),  # 10 breathing cycles
    Exercise("ab_roll_up", "Roll Up", "abdominals", ["mat", "reformer"], "intermediate",
             spring_setting="1R", reps=5, duration_seconds=60),
    Exercise("ab_series_five", "Series of Five", "abdominals", ["mat"], "intermediate",
             spring_setting="", reps=10, duration_seconds=120),  # 10 reps each of 5 exercises
    Exercise("ab_coordination", "Coordination", "abdominals", ["reformer"], "intermediate",
             spring_setting="1R+1B", reps=5, duration_seconds=60),
    Exercise("ab_teaser", "Teaser", "abdominals", ["mat", "reformer"], "intermediate",  # CPTT: I/A mat
             spring_setting="1R", reps=3, duration_seconds=60),
    Exercise("ab_criss_cross", "Criss Cross", "abdominals", ["mat"], "intermediate",
             spring_setting="", reps=8, duration_seconds=60),
    Exercise("ab_short_box_round", "Short Box - Round Back", "abdominals", ["reformer"], "intermediate",
             spring_setting="1R", reps=5, duration_seconds=60, uses_box=True),
    Exercise("ab_short_box_flat", "Short Box - Flat Back", "abdominals", ["reformer"], "intermediate",
             spring_setting="1R", reps=5, duration_seconds=60, uses_box=True),
    Exercise("ab_short_box_twist", "Short Box - Twist", "abdominals", ["reformer"], "intermediate",
             spring_setting="1R", reps=5, duration_seconds=60, uses_box=True),
    Exercise("ab_short_box_side", "Short Box - Side to Side", "abdominals", ["reformer"], "intermediate",
             spring_setting="1R", reps=5, duration_seconds=60, uses_box=True),

    # Plank (various springs) - Manual: 3-5 reps
    Exercise("pl_front_plank", "Front Plank", "plank", ["mat"], "beginner",
             spring_setting="", reps=3, duration_seconds=30),  # Hold position
    Exercise("pl_long_stretch", "Long Stretch", "plank", ["reformer"], "intermediate",
             spring_setting="1R+1B", reps=5, duration_seconds=45),
    Exercise("pl_up_stretch", "Up Stretch", "plank", ["reformer"], "advanced",  # CPTT: A
             spring_setting="1R+1B", reps=5, duration_seconds=45),
    Exercise("pl_elephant", "Elephant", "plank", ["reformer"], "intermediate",
             spring_setting="1R+1B", reps=5, duration_seconds=45),
    Exercise("pl_pike", "Pike", "plank", ["chair", "mat"], "intermediate",
             spring_setting="1@2", reps=5, duration_seconds=45),
    Exercise("pl_mountain_climber", "Mountain Climber", "plank", ["chair"], "intermediate",
             spring_setting="1@2", reps=8, duration_seconds=45),

    # Upper Body (light-medium springs) - Manual: Arm Circles=10, Rowing series
    Exercise("ub_arm_work", "Arm Work Series", "upper_body", ["reformer"], "beginner",
             spring_setting="1R or 1B", reps=10, duration_seconds=90,
             variations=["Biceps", "Triceps", "Chest", "Back"]),
    Exercise("ub_chest_expansion", "Chest Expansion", "upper_body", ["reformer", "springboard"], "beginner",
             spring_setting="1R", reps=5, duration_seconds=45),
    Exercise("ub_rowing", "Rowing Series", "upper_body", ["reformer"], "intermediate",
             spring_setting="1R", reps=5, duration_seconds=90, uses_box=True),
    Exercise("ub_hug_a_tree", "Hug a Tree", "upper_body", ["reformer", "springboard"], "beginner",
             spring_setting="1R", reps=8, duration_seconds=45),
    Exercise("ub_push_ups", "Push Ups", "upper_body", ["mat", "chair"], "intermediate",
             spring_setting="", reps=3, duration_seconds=45),  # Manual: 3 times
    Exercise("ub_trx_rows", "TRX Rows", "upper_body", ["trx"], "intermediate",
             spring_setting="", reps=8, duration_seconds=45),

    # Lower Body (medium-heavy springs) - Manual: Leg Circles=5 each direction
    Exercise("lb_leg_circles", "Leg Circles", "lower_body", ["mat", "reformer"], "beginner",
             spring_setting="2R", reps=5, duration_seconds=60),  # 5 each direction
    Exercise("lb_leg_press", "Leg Press", "lower_body", ["springboard"], "beginner",
             spring_setting="", reps=10, duration_seconds=60),
    Exercise("lb_standing_leg", "Standing Leg Series", "lower_body", ["reformer", "chair"], "intermediate",
             spring_setting="1R+1B", reps=8, duration_seconds=90),
    Exercise("lb_side_splits", "Side Splits", "lower_body", ["reformer"], "intermediate",  # CPTT: I
             spring_setting="1R", reps=5, duration_seconds=60),
    Exercise("lb_lunges", "Lunges", "lower_body", ["reformer", "chair"], "intermediate",
             spring_setting="1R+1B", reps=5, duration_seconds=60),
    Exercise("lb_scooter", "Scooter", "lower_body", ["reformer"], "beginner",  # CPTT: B
             spring_setting="1R+1B", reps=8, duration_seconds=45),

    # Lateral Line (light-medium springs) - Manual: Mermaid=5 each side
    Exercise("ll_side_lying", "Side Lying Series", "lateral_line", ["mat", "reformer"], "beginner",
             spring_setting="1R", reps=8, duration_seconds=90),
    Exercise("ll_mermaid", "Mermaid", "lateral_line", ["reformer", "mat", "chair"], "beginner",  # CPTT: B
             spring_setting="1R", reps=5, duration_seconds=60),  # 5 each side
    Exercise("ll_side_bend", "Side Bend", "lateral_line", ["mat"], "intermediate",
             spring_setting="", reps=5, duration_seconds=45),
    Exercise("ll_kneeling_side", "Kneeling Side Kicks", "lateral_line", ["reformer"], "intermediate",
             spring_setting="1R", reps=8, duration_seconds=60),

    # Prone/Extension (light springs) - Manual: Swan=5, Swimming=5 sets
    Exercise("pe_swan", "Swan", "prone_extension", ["mat", "reformer"], "intermediate",  # CPTT: I/A mat, I reformer
             spring_setting="1B", reps=5, duration_seconds=45),
    Exercise("pe_swimming", "Swimming", "prone_extension", ["mat"], "beginner",  # CPTT: B mat
             spring_setting="", reps=5, duration_seconds=45),  # 5 sets
    Exercise("pe_pulling_straps", "Pulling Straps", "prone_extension", ["reformer"], "beginner",  # CPTT: B/I
             spring_setting="1R", reps=5, duration_seconds=60, uses_box=True),
    Exercise("pe_back_extension", "Back Extension", "prone_extension", ["chair", "barrel"], "intermediate",
             spring_setting="1@2", reps=5, duration_seconds=60),
    Exercise("pe_rocking", "Rocking", "prone_extension", ["mat"], "intermediate",  # CPTT: I/A
             spring_setting="", reps=5, duration_seconds=45),

    # Full Body Integration (various) - Manual: 3-5 reps for advanced exercises
    Exercise("fb_control_balance", "Control Balance", "full_body", ["mat"], "advanced",
             spring_setting="", reps=3, duration_seconds=60),
    Exercise("fb_star", "Star", "full_body", ["reformer"], "advanced",
             spring_setting="1R", reps=3, duration_seconds=45),
    Exercise("fb_snake_twist", "Snake/Twist", "full_body", ["reformer"], "advanced",
             spring_setting="1R+1B", reps=3, duration_seconds=60),
    Exercise("fb_balance_control", "Balance Control", "full_body", ["reformer", "chair"], "advanced",
             spring_setting="1R", reps=3, duration_seconds=60),
    Exercise("fb_burpees", "Pilates Burpees", "full_body", ["mat"], "intermediate",
             spring_setting="", reps=5, duration_seconds=60),

    # Stretch (light or no springs) - Held positions, 30-60 seconds each
    Exercise("st_hip_flexor", "Hip Flexor Stretch", "stretch", ["mat", "reformer"], "beginner",
             spring_setting="1B or none", reps=3, duration_seconds=60),  # Hold each side
    Exercise("st_hamstring", "Hamstring Stretch", "stretch", ["mat", "reformer", "springboard"], "beginner",
             spring_setting="1B or none", reps=3, duration_seconds=60),
    Exercise("st_mermaid_stretch", "Mermaid Stretch", "stretch", ["mat", "reformer"], "beginner",
             spring_setting="1R", reps=5, duration_seconds=45),
    Exercise("st_spine_stretch", "Spine Stretch Forward", "stretch", ["mat"], "beginner",
             spring_setting="", reps=5, duration_seconds=45),
    Exercise("st_cat_cow", "Cat/Cow", "stretch", ["mat"], "beginner",
             spring_setting="", reps=5, duration_seconds=45),
    Exercise("st_childs_pose", "Child's Pose", "stretch", ["mat"], "beginner",
             spring_setting="", reps=1, duration_seconds=30),  # Hold position
]


class ClassBuilder:
    """Builds balanced Pilates classes with flow optimization."""

    def __init__(self):
        self.exercises = EXERCISES

    def get_exercises(
        self,
        section: Optional[str] = None,
        equipment: Optional[str] = None,
        level: Optional[str] = None
    ) -> list[dict]:
        """Get exercises filtered by section, equipment, or level."""
        results = []

        for ex in self.exercises:
            if section and ex.section != section:
                continue
            if equipment and equipment not in ex.equipment:
                continue
            if level and not self._level_matches(ex.level, level):
                continue

            results.append({
                "id": ex.id,
                "name": ex.name,
                "section": ex.section,
                "equipment": ex.equipment,
                "level": ex.level,
                "spring_setting": ex.spring_setting,
                "reps": ex.reps,
                "duration_seconds": ex.duration_seconds,
                "variations": ex.variations,
                "props": ex.props,
                "uses_box": ex.uses_box,
            })

        return results

    def _level_matches(self, exercise_level: str, target_level: str) -> bool:
        """Check if exercise is appropriate for target level."""
        level_order = {"beginner": 1.0, "intermediate": 1.5, "advanced": 2.0, "advanced_plus": 2.5}
        return level_order.get(exercise_level, 1.5) <= level_order.get(target_level, 1.5)

    def _get_level_config(self, level: str) -> dict:
        """Get configuration for experience level."""
        for lvl in EXPERIENCE_LEVELS:
            if lvl["id"] == level:
                return lvl
        return EXPERIENCE_LEVELS[1]  # Default to intermediate

    def _optimize_section_order(
        self,
        allowed_equipment: list[str],
        exercises_by_section: dict
    ) -> list[dict]:
        """
        Optimize middle section order to minimize equipment transitions.

        Rule: Cannot return to equipment after leaving it.
        Goal: Group sections by equipment for smooth flow.
        """
        # Determine which equipment each section primarily uses
        section_equipment = {}
        for section in FLEXIBLE_SECTIONS:
            section_id = section["id"]
            if section_id not in exercises_by_section:
                continue

            # Count equipment usage in this section
            eq_count = {}
            for ex in exercises_by_section[section_id]:
                for eq in ex.equipment:
                    if eq in allowed_equipment:
                        eq_count[eq] = eq_count.get(eq, 0) + 1

            if eq_count:
                # Primary equipment is most common
                section_equipment[section_id] = max(eq_count, key=eq_count.get)

        # Group sections by primary equipment
        equipment_groups = {}
        for section_id, eq in section_equipment.items():
            if eq not in equipment_groups:
                equipment_groups[eq] = []
            equipment_groups[eq].append(section_id)

        # Order equipment groups (start with most sections)
        ordered_sections = []
        for eq in sorted(equipment_groups.keys(), key=lambda e: -len(equipment_groups[e])):
            for section_id in equipment_groups[eq]:
                for section in FLEXIBLE_SECTIONS:
                    if section["id"] == section_id:
                        ordered_sections.append(section)
                        break

        # Add any sections not yet included
        for section in FLEXIBLE_SECTIONS:
            if section not in ordered_sections:
                ordered_sections.append(section)

        return ordered_sections

    def _validate_equipment_flow(self, class_exercises: list[dict]) -> tuple[bool, list[str]]:
        """
        Validate that equipment flow is contiguous.
        Returns (is_valid, list of equipment used in order).
        """
        equipment_sequence = []
        equipment_seen = set()

        for ex in class_exercises:
            eq = ex["equipment"]
            if eq not in equipment_seen:
                equipment_sequence.append(eq)
                equipment_seen.add(eq)
            elif equipment_sequence[-1] != eq:
                # Returning to equipment after leaving - invalid!
                return False, equipment_sequence

        return True, equipment_sequence

    def _validate_class(self, class_plan: dict, max_equipment: int = 3, allowed_equipment: list[str] = None, level: str = "intermediate") -> tuple[bool, list[str]]:
        """
        Validate a generated class plan for rule violations.
        Returns (is_valid, list of violation messages).
        Only counts empty sections as violations if exercises were available for that section.
        """
        violations = []

        # Check for empty sections - but only if exercises were available
        for section in class_plan["sections"]:
            if not section["exercises"]:
                # Check if any exercises exist for this section with selected equipment+level
                available = [
                    ex for ex in self.exercises
                    if ex.section == section["id"]
                    and any(eq in (allowed_equipment or ["reformer"]) for eq in ex.equipment)
                    and self._level_matches(ex.level, level)
                ]
                # Only count as violation if exercises were available but not selected
                if available:
                    violations.append(f"Empty section: {section['name']}")

        # Check transition count
        if class_plan["transitions"] > class_plan["max_transitions"]:
            violations.append(f"Too many transitions ({class_plan['transitions']}) - max is {class_plan['max_transitions']}")

        # Check equipment count
        used_equipment = set()
        for section in class_plan["sections"]:
            for ex in section["exercises"]:
                if ex.get("equipment"):
                    used_equipment.add(ex["equipment"])

        if len(used_equipment) > max_equipment:
            violations.append(f"Too many equipment types ({len(used_equipment)}) - max is {max_equipment}")

        return len(violations) == 0, violations

    def generate_class(
        self,
        duration_minutes: int = 50,
        level: str = "intermediate",
        allowed_equipment: list[str] = None,
        max_transitions: int = None,
        max_retries: int = 10
    ) -> dict:
        """
        Generate a balanced class plan with optimized flow.
        Retries generation until a valid plan is produced.

        Rules applied:
        - Footwork always first, Stretch always last
        - Middle sections reordered for equipment flow
        - No returning to equipment after leaving it
        - Minimize transitions (spring changes OR equipment changes)
        """
        if allowed_equipment is None:
            allowed_equipment = ["reformer"]

        level_config = self._get_level_config(level)

        # Use provided max_transitions or default from level config (default 6 based on sample classes)
        if max_transitions is None:
            max_transitions = level_config.get("max_transitions", 6)

        # Equipment limit: sample classes show 2-3 equipment for all levels
        max_equipment = 3

        # Retry generation until we get a valid plan
        best_plan = None
        best_violation_count = float('inf')

        for attempt in range(max_retries):
            class_plan = self._generate_class_attempt(
                duration_minutes, level, level_config, allowed_equipment, max_transitions, max_equipment
            )

            # Validate the generated plan
            is_valid, violations = self._validate_class(class_plan, max_equipment, allowed_equipment, level)

            if is_valid:
                return class_plan

            # Track best plan (fewest violations) as fallback
            if len(violations) < best_violation_count:
                best_violation_count = len(violations)
                best_plan = class_plan

        # If no valid plan after all retries, return best attempt
        # (This shouldn't happen often with good exercise coverage)
        return best_plan if best_plan else class_plan

    def _generate_class_attempt(
        self,
        duration_minutes: int,
        level: str,
        level_config: dict,
        allowed_equipment: list[str],
        max_transitions: int,
        max_equipment: int
    ) -> dict:
        """Single attempt to generate a class plan."""
        # Group exercises by section for analysis
        exercises_by_section = {}
        for ex in self.exercises:
            if ex.section not in exercises_by_section:
                exercises_by_section[ex.section] = []
            exercises_by_section[ex.section].append(ex)

        # Optimize middle section order
        optimized_middle = self._optimize_section_order(allowed_equipment, exercises_by_section)

        # Build final section order
        ordered_sections = [FIXED_FIRST] + optimized_middle + [FIXED_LAST]

        # Calculate time per section
        total_typical = sum(s["typical_minutes"] for s in ordered_sections)
        time_scale = duration_minutes / total_typical

        class_plan = {
            "duration_minutes": duration_minutes,
            "level": level,
            "level_name": level_config["name"],
            "equipment": allowed_equipment,
            "sections": [],
            "total_exercises": 0,
            "equipment_flow": [],
            "transitions": 0,
            "max_transitions": max_transitions,
        }

        current_equipment = None
        equipment_used = set()
        last_spring = None
        last_box = False  # Track if previous exercise used box
        is_first_exercise = True  # Track first exercise to not count initial setup as transition

        for idx, section in enumerate(ordered_sections):
            section_minutes = section["typical_minutes"] * time_scale
            section_seconds = section_minutes * 60

            # Apply level modifier to exercise count
            section_seconds *= level_config["exercise_count_multiplier"]

            # Get exercises for this section
            available = [
                ex for ex in self.exercises
                if ex.section == section["id"]
                and any(eq in allowed_equipment for eq in ex.equipment)
                and self._level_matches(ex.level, level)
            ]

            # Fallback: if no exercises match level, get ANY exercise for this section
            if not available:
                available = [
                    ex for ex in self.exercises
                    if ex.section == section["id"]
                    and any(eq in allowed_equipment for eq in ex.equipment)
                ]

            # Select exercises to fill section time
            selected = []
            remaining_time = section_seconds
            section_has_exercise = False  # Ensure each section gets at least one exercise

            # Shuffle for initial variety
            random.shuffle(available)

            while available and (remaining_time > 0 or not section_has_exercise):
                # Sort available exercises to prefer current spring setting to minimize transitions
                # Priority: 1) same spring, 2) different spring
                def transition_cost(ex):
                    spring_match = (ex.spring_setting == last_spring) if last_spring else True
                    return 0 if spring_match else 1

                available.sort(key=transition_cost)

                # Try to find a valid exercise
                found_exercise = False
                selected_idx = None

                for i, ex in enumerate(available):
                    # Recalculate valid equipment for EACH exercise
                    valid_equipment = set(allowed_equipment) - (equipment_used - ({current_equipment} if current_equipment else set()))

                    # Skip if exercise doesn't work with valid equipment
                    if not any(eq in valid_equipment for eq in ex.equipment):
                        continue

                    # Enforce equipment count limit
                    current_eq_count = len(equipment_used) + (1 if current_equipment and current_equipment not in equipment_used else 0)
                    exercise_would_add_new = not any(eq in equipment_used or eq == current_equipment for eq in ex.equipment)
                    if exercise_would_add_new and current_eq_count >= max_equipment:
                        continue

                    if remaining_time <= 0 and section_has_exercise:
                        break

                    if ex.duration_seconds <= remaining_time or not section_has_exercise:
                        # Pick equipment - prefer current to avoid transition
                        valid_eq = [e for e in ex.equipment if e in valid_equipment]
                        if not valid_eq:
                            continue

                        if current_equipment in valid_eq:
                            equipment_choice = current_equipment
                        else:
                            equipment_choice = valid_eq[0]

                        # Track transitions (equipment change OR spring change)
                        # NOTE: Box changes are NOT transitions - box is a prop on reformer, not separate equipment
                        has_equipment_transition = equipment_choice != current_equipment
                        has_spring_transition = ex.spring_setting and ex.spring_setting != last_spring

                        # Count transition if equipment OR spring changed (not first exercise)
                        if not is_first_exercise and (has_equipment_transition or has_spring_transition):
                            # STRICTLY enforce max transitions - skip exercise if at limit
                            if class_plan["transitions"] >= max_transitions:
                                continue
                            class_plan["transitions"] += 1

                        # Track equipment flow
                        if has_equipment_transition:
                            if current_equipment is not None:
                                equipment_used.add(current_equipment)
                            current_equipment = equipment_choice
                            class_plan["equipment_flow"].append(equipment_choice)

                        # Update spring and box tracking
                        if ex.spring_setting:
                            last_spring = ex.spring_setting
                        last_box = ex.uses_box

                        is_first_exercise = False
                        section_has_exercise = True

                        selected.append({
                            "id": ex.id,
                            "name": ex.name,
                            "equipment": equipment_choice,
                            "spring_setting": ex.spring_setting,
                            "reps": ex.reps,
                            "duration_seconds": ex.duration_seconds,
                            "variations": ex.variations[:2] if ex.variations else [],
                            "props": ex.props,
                            "uses_box": ex.uses_box,
                        })
                        remaining_time -= ex.duration_seconds
                        selected_idx = i
                        found_exercise = True
                        break

                # Remove selected exercise from available list
                if selected_idx is not None:
                    available.pop(selected_idx)
                else:
                    # No valid exercise found, exit loop
                    break

            # Always include section in output (even if empty - shows what needs exercises)
            if selected or True:  # Always include section
                class_plan["sections"].append({
                    "id": section["id"],
                    "name": section["name"],
                    "order": idx + 1,
                    "allocated_minutes": round(section_minutes, 1),
                    "exercises": selected,
                })
                class_plan["total_exercises"] += len(selected)

        return class_plan
