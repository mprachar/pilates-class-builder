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
    # Beginner ab exercises
    Exercise("ab_hundred_prep", "Hundred Prep", "abdominals", ["mat", "reformer"], "beginner",
             spring_setting="1R or 1B", reps=5, duration_seconds=60),  # Modified hundred for beginners
    Exercise("ab_chest_lift", "Chest Lift", "abdominals", ["mat", "reformer"], "beginner",
             spring_setting="1R", reps=8, duration_seconds=45),
    Exercise("ab_supine_twist", "Supine Twist", "abdominals", ["mat"], "beginner",
             spring_setting="", reps=5, duration_seconds=45),
    Exercise("ab_dead_bug", "Dead Bug", "abdominals", ["mat"], "beginner",
             spring_setting="", reps=8, duration_seconds=60),
    # Intermediate ab exercises
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
    Exercise("pl_knee_stretch", "Knee Stretch", "plank", ["reformer"], "beginner",
             spring_setting="1R+1B", reps=8, duration_seconds=45),
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
    Exercise("ub_arm_circles", "Arm Circles", "upper_body", ["mat"], "beginner",
             spring_setting="", reps=10, duration_seconds=45),
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
    # Beginner full body exercises
    Exercise("fb_single_leg_stretch", "Single Leg Stretch", "full_body", ["mat"], "beginner",
             spring_setting="", reps=8, duration_seconds=60),
    Exercise("fb_rolling_like_ball", "Rolling Like a Ball", "full_body", ["mat"], "beginner",
             spring_setting="", reps=6, duration_seconds=45),
    Exercise("fb_full_body_stretch", "Full Body Stretch (Reformer)", "full_body", ["reformer"], "beginner",
             spring_setting="1R", reps=5, duration_seconds=60),
    # Intermediate and advanced
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

    def _allocate_equipment_blocks(
        self,
        ordered_sections: list[dict],
        allowed_equipment: list[str],
        level: str,
        max_transitions: int
    ) -> list[str]:
        """
        Pre-allocate equipment to each section to maximize primary equipment usage
        while maintaining LINEAR FLOW and providing controlled variety.

        Returns: List of equipment allocations, one per section.

        Strategy:
        1. Reserve "stretch" section for mat (natural ending)
        2. Allocate 1-2 sections to secondary equipment for variety
        3. Use primary equipment for everything else
        4. Ensure linear flow (no interleaving like R-M-R-M)
        """
        primary_equipment = allowed_equipment[0] if allowed_equipment else "mat"
        secondary_equipment = allowed_equipment[1] if len(allowed_equipment) > 1 else None
        tertiary_equipment = allowed_equipment[2] if len(allowed_equipment) > 2 else None

        # Count available exercises per section per equipment
        section_exercise_counts = {}
        for section in ordered_sections:
            section_id = section["id"]
            eq_counts = {}
            for ex in self.exercises:
                if ex.section != section_id:
                    continue
                if not self._level_matches(ex.level, level):
                    continue
                for eq in ex.equipment:
                    if eq in allowed_equipment:
                        eq_counts[eq] = eq_counts.get(eq, 0) + 1
            section_exercise_counts[section_id] = eq_counts

        # Initial allocation: mostly primary equipment
        allocations = []
        for section in ordered_sections:
            section_id = section["id"]
            eq_counts = section_exercise_counts.get(section_id, {})

            # Stretch section: prefer mat
            if section_id == "stretch" and eq_counts.get("mat", 0) > 0:
                allocations.append("mat")
            # Otherwise: prefer primary equipment
            elif eq_counts.get(primary_equipment, 0) > 0:
                allocations.append(primary_equipment)
            elif secondary_equipment and eq_counts.get(secondary_equipment, 0) > 0:
                allocations.append(secondary_equipment)
            elif eq_counts.get("mat", 0) > 0:
                allocations.append("mat")
            elif eq_counts:
                allocations.append(max(eq_counts, key=eq_counts.get))
            else:
                allocations.append(primary_equipment)

        # Introduce controlled variety: allocate CONTIGUOUS sections to secondary equipment
        # CRITICAL: Equipment must form LINEAR FLOW with no returns
        # Valid: reformer -> chair -> mat, reformer -> mat, reformer -> chair -> springboard -> mat
        # Invalid: reformer -> chair -> reformer (returns to reformer after leaving)

        # VARIETY STRATEGY: Randomly decide pattern and apply it linearly
        # Pattern options (with probabilities):
        # - 25%: Primary only -> mat (simple reformer class)
        # - 50%: Primary -> Secondary -> mat (standard variety)
        # - 25%: Primary -> Secondary (more sections) -> mat

        pattern_roll = random.random()
        n_sections = len(ordered_sections)

        if secondary_equipment and pattern_roll > 0.10:  # 90% chance to use secondary
            # Find which sections can use secondary equipment
            secondary_eligible = []
            for i, section in enumerate(ordered_sections):
                section_id = section["id"]
                if i == 0 or section_id == "stretch":
                    continue  # Keep first as primary, stretch as mat
                eq_counts = section_exercise_counts.get(section_id, {})
                if eq_counts.get(secondary_equipment, 0) >= 1:
                    secondary_eligible.append(i)

            if secondary_eligible:
                # CRITICAL: Sort eligible indices to ensure consecutive detection works
                secondary_eligible.sort()

                # Decide how many sections use secondary equipment
                # MORE AGGRESSIVE allocation since chair has fewer exercises than reformer
                if pattern_roll > 0.55:  # 45% chance for high variety (4-6 sections)
                    num_secondary = random.randint(4, min(6, len(secondary_eligible)))
                else:  # 45% chance for medium variety (3-5 sections)
                    num_secondary = random.randint(3, min(5, len(secondary_eligible)))

                # Choose starting position for secondary block
                # Lower threshold (30%) to allow more secondary equipment usage
                min_start = max(1, int(n_sections * 0.3))
                eligible_starts = [i for i in secondary_eligible if i >= min_start]

                if eligible_starts:
                    # Prefer EARLIER start positions to maximize secondary equipment usage
                    # Weight toward the first half of eligible starts
                    if len(eligible_starts) > 2:
                        # 70% chance to pick from first half, 30% from second half
                        if random.random() < 0.7:
                            start_idx = random.choice(eligible_starts[:len(eligible_starts)//2 + 1])
                        else:
                            start_idx = random.choice(eligible_starts)
                    else:
                        start_idx = eligible_starts[0]  # Always pick earliest if only 1-2 options

                    # Find consecutive eligible sections from start
                    consecutive = [start_idx]
                    for next_idx in secondary_eligible:
                        if next_idx > start_idx and next_idx == consecutive[-1] + 1:
                            consecutive.append(next_idx)
                        elif next_idx > consecutive[-1] + 1:
                            break  # Gap found, stop

                    # Allocate secondary to consecutive sections (up to num_secondary)
                    for i in range(min(num_secondary, len(consecutive))):
                        section_idx = consecutive[i]
                        if section_idx < len(allocations):
                            allocations[section_idx] = secondary_equipment

                    # Everything AFTER secondary block: prefer continuing secondary or mat
                    last_secondary = consecutive[min(num_secondary, len(consecutive)) - 1]
                    for i in range(last_secondary + 1, len(allocations)):
                        section_id = ordered_sections[i]["id"]
                        eq_counts = section_exercise_counts.get(section_id, {})

                        # Priority order for post-secondary sections:
                        # 1. Mat (if available and in allowed list) - natural ending
                        # 2. Secondary equipment (if available) - continue the block
                        # 3. Keep WHATEVER EQUIPMENT HAS EXERCISES (prevents empty sections)
                        if "mat" in allowed_equipment and eq_counts.get("mat", 0) > 0:
                            allocations[i] = "mat"
                        elif eq_counts.get(secondary_equipment, 0) > 0:
                            allocations[i] = secondary_equipment
                        elif eq_counts.get(primary_equipment, 0) > 0:
                            # Primary is ONLY option - keep it to avoid empty section
                            # This may cause "bouncing" at the end but that's better than empty
                            allocations[i] = primary_equipment
                        elif eq_counts:
                            # Use whatever equipment has exercises
                            allocations[i] = max(eq_counts, key=eq_counts.get)
                        # else: keep current allocation (will be empty, validation catches it)

        # FINAL PASS: Enforce linear flow (no equipment returns)
        # This catches edge cases where initial allocation created bouncing
        allocations = self._enforce_linear_flow(allocations, section_exercise_counts, ordered_sections, allowed_equipment)

        return allocations

    def _enforce_linear_flow(
        self,
        allocations: list[str],
        section_exercise_counts: dict,
        ordered_sections: list[dict],
        allowed_equipment: list[str]
    ) -> list[str]:
        """
        Post-process allocations to enforce linear flow WHERE POSSIBLE.
        Once we leave an equipment type, we can never return to it.

        CRITICAL: Do NOT create empty sections! If enforcing linear flow
        would result in a section with no exercises, allow the "bounce"
        instead. An imperfect flow is better than missing sections.
        """
        if len(allocations) <= 1:
            return allocations

        result = allocations.copy()
        abandoned = set()
        current_eq = None

        for i, eq in enumerate(result):
            if current_eq is not None and eq != current_eq:
                # Equipment changed - mark previous as abandoned
                abandoned.add(current_eq)

            if eq in abandoned:
                # VIOLATION: Trying to return to abandoned equipment
                section_id = ordered_sections[i]["id"]
                eq_counts = section_exercise_counts.get(section_id, {})

                # Try to fix, but ONLY if it won't create empty section
                # Priority: current_eq > mat > keep original (allow bounce)
                if current_eq and eq_counts.get(current_eq, 0) > 0:
                    result[i] = current_eq
                elif "mat" in allowed_equipment and eq_counts.get("mat", 0) > 0:
                    result[i] = "mat"
                else:
                    # Cannot fix without creating empty section
                    # ALLOW THE BOUNCE - it's better than empty sections
                    # Clear abandoned set since we're accepting this equipment return
                    abandoned.discard(eq)

            current_eq = result[i]

        return result

    def _count_equipment_transitions(self, allocations: list[str]) -> int:
        """Count equipment transitions (changes between sections)."""
        transitions = 0
        prev = None
        for eq in allocations:
            if prev and eq != prev:
                transitions += 1
            prev = eq
        return transitions

    def _optimize_section_order(
        self,
        allowed_equipment: list[str],
        exercises_by_section: dict,
        level: str = "intermediate"
    ) -> list[dict]:
        """
        Optimize middle section order for LINEAR EQUIPMENT FLOW.

        Strategy: Order sections so that secondary-equipment-capable sections
        are grouped at the END, enabling: primary → secondary → mat flow.

        This prevents the scenario where:
        - Middle sections use secondary equipment
        - Later sections can ONLY use primary (no secondary exercises)
        - Linear flow is violated (can't return to primary)

        CRITICAL: Must filter by level to accurately determine capability!
        """
        primary_equipment = allowed_equipment[0] if allowed_equipment else "mat"
        secondary_equipment = allowed_equipment[1] if len(allowed_equipment) > 1 else None

        # Categorize sections by equipment capability (FILTERED BY LEVEL)
        primary_only = []      # Can ONLY use primary equipment at this level
        secondary_capable = [] # Can use secondary equipment at this level

        for section in FLEXIBLE_SECTIONS:
            section_id = section["id"]
            if section_id not in exercises_by_section:
                primary_only.append(section)
                continue

            # Count equipment availability FOR THIS LEVEL
            eq_count = {}
            for ex in exercises_by_section[section_id]:
                # CRITICAL: Filter by level!
                if not self._level_matches(ex.level, level):
                    continue
                for eq in ex.equipment:
                    if eq in allowed_equipment:
                        eq_count[eq] = eq_count.get(eq, 0) + 1

            # Check if section can use secondary equipment AT THIS LEVEL
            if secondary_equipment and eq_count.get(secondary_equipment, 0) > 0:
                secondary_capable.append(section)
            else:
                primary_only.append(section)

        # Order: primary-only sections FIRST, then secondary-capable sections
        # This enables: primary (primary-only) → secondary (secondary-capable) → mat
        ordered_sections = primary_only + secondary_capable

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
        ANY empty section is a violation - we should never present empty sections.
        """
        violations = []

        # Check for empty sections - ANY empty section is a violation
        for section in class_plan["sections"]:
            if not section["exercises"]:
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
        max_retries: int = 50
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

        # Return best plan, but ALWAYS exclude empty sections
        result = best_plan if best_plan else class_plan
        result["sections"] = [s for s in result["sections"] if s["exercises"]]
        # Renumber sections after filtering
        for i, section in enumerate(result["sections"]):
            section["order"] = i + 1
        return result

    def _generate_class_attempt(
        self,
        duration_minutes: int,
        level: str,
        level_config: dict,
        allowed_equipment: list[str],
        max_transitions: int,
        max_equipment: int
    ) -> dict:
        """
        Single attempt to generate a class plan using EQUIPMENT BLOCK ALLOCATION.

        Strategy:
        1. Pre-allocate equipment to each section (maximize primary equipment)
        2. Fill each section with ONLY its allocated equipment
        3. Equipment flow is contiguous by design (no bouncing)
        """
        # Group exercises by section for analysis
        exercises_by_section = {}
        for ex in self.exercises:
            if ex.section not in exercises_by_section:
                exercises_by_section[ex.section] = []
            exercises_by_section[ex.section].append(ex)

        # Optimize middle section order (pass level for proper filtering)
        optimized_middle = self._optimize_section_order(allowed_equipment, exercises_by_section, level)

        # Build final section order
        ordered_sections = [FIXED_FIRST] + optimized_middle + [FIXED_LAST]

        # PRE-ALLOCATE equipment to each section
        equipment_allocations = self._allocate_equipment_blocks(
            ordered_sections, allowed_equipment, level, max_transitions
        )

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
        last_spring = None
        is_first_exercise = True

        for idx, section in enumerate(ordered_sections):
            section_minutes = section["typical_minutes"] * time_scale
            section_seconds = section_minutes * 60

            # Apply level modifier to exercise count
            section_seconds *= level_config["exercise_count_multiplier"]

            # Get the PRE-ALLOCATED equipment for this section
            allocated_equipment = equipment_allocations[idx]

            # Get exercises for this section that use the ALLOCATED equipment
            available = [
                ex for ex in self.exercises
                if ex.section == section["id"]
                and allocated_equipment in ex.equipment
                and self._level_matches(ex.level, level)
            ]

            # Shuffle to add variety
            random.shuffle(available)

            # Sort by spring setting preference (same spring first)
            def spring_priority(ex):
                ex_spring = ex.spring_setting if allocated_equipment != "mat" else ""
                same_spring = 0 if (ex_spring == last_spring or not last_spring) else 1
                return (same_spring, random.random())
            available.sort(key=spring_priority)

            # Select exercises to fill section time
            selected = []
            remaining_time = section_seconds
            section_has_exercise = False

            for ex in available:
                if remaining_time <= 0 and section_has_exercise:
                    break

                if ex.duration_seconds <= remaining_time or not section_has_exercise:
                    # Track equipment and spring transitions
                    has_equipment_transition = allocated_equipment != current_equipment
                    effective_spring = ex.spring_setting if allocated_equipment != "mat" else ""
                    has_spring_transition = effective_spring and effective_spring != last_spring

                    # ONLY count SPRING transitions against the limit
                    # Equipment transitions are PRE-PLANNED by block allocation and don't count
                    # CRITICAL: Always allow the FIRST exercise in each section (no skipping)
                    if not is_first_exercise and has_spring_transition and not has_equipment_transition:
                        # Skip if we've hit transition limit, BUT not if this is the first exercise in section
                        if class_plan["transitions"] >= max_transitions and section_has_exercise:
                            continue
                        # Only increment if we're under the limit
                        if class_plan["transitions"] < max_transitions:
                            class_plan["transitions"] += 1

                    # Track equipment flow
                    if has_equipment_transition:
                        current_equipment = allocated_equipment
                        class_plan["equipment_flow"].append(allocated_equipment)
                        # CRITICAL: Reset spring tracking on equipment change
                        # Spring settings are equipment-specific (e.g., "2R" vs "2@2")
                        # Different equipment = incomparable spring systems
                        last_spring = None

                    # Update spring tracking
                    exercise_spring_setting = ex.spring_setting if allocated_equipment != "mat" else ""
                    if exercise_spring_setting:
                        last_spring = exercise_spring_setting

                    is_first_exercise = False
                    section_has_exercise = True

                    selected.append({
                        "id": ex.id,
                        "name": ex.name,
                        "equipment": allocated_equipment,
                        "spring_setting": exercise_spring_setting,
                        "reps": ex.reps,
                        "duration_seconds": ex.duration_seconds,
                        "variations": ex.variations[:2] if ex.variations else [],
                        "props": ex.props,
                        "uses_box": ex.uses_box,
                    })
                    remaining_time -= ex.duration_seconds

            # Always include section in output
            class_plan["sections"].append({
                "id": section["id"],
                "name": section["name"],
                "order": idx + 1,
                "allocated_minutes": round(section_minutes, 1),
                "exercises": selected,
            })
            class_plan["total_exercises"] += len(selected)

        return class_plan
