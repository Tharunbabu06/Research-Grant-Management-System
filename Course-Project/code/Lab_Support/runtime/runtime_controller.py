# ============================================================
# LAB 6 - CONTROLLED RUNTIME
# Research Grant Management System
#
# Runtime responsibilities:
#   - Budget control
#   - Approval gates
#   - Audit logging
#   - Checkpointing
#   - Resume
# ============================================================

import json
from datetime import datetime
from pathlib import Path


# ============================================================
# FILE LOCATIONS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "outputs"

AUDIT_FILE = OUTPUT_DIR / "audit_log.json"
CHECKPOINT_FILE = OUTPUT_DIR / "checkpoint.json"


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR.mkdir(
    exist_ok=True
)


# ============================================================
# RUNTIME CLASS
# ============================================================

class Runtime:

    def __init__(
        self,
        budget=10,
        gates=None
    ):
        """
        Create a controlled runtime.

        budget:
            Maximum number of runtime actions allowed.

        gates:
            Actions that require approval.
        """

        self.budget = budget

        self.actions_used = 0

        self.gates = gates or []

        self.state = {}

        self.audit_log = []

        self.current_step = 0

        self.load_existing_audit()

    # ========================================================
    # AUDIT
    # ========================================================

    def load_existing_audit(self):

        if AUDIT_FILE.exists():

            try:

                with open(
                    AUDIT_FILE,
                    "r",
                    encoding="utf-8"
                ) as file:

                    self.audit_log = json.load(file)

            except (
                json.JSONDecodeError,
                OSError
            ):

                self.audit_log = []

    # ========================================================
    # AUDIT LOGGING
    # ========================================================

    def log(
        self,
        intent,
        action,
        input_data,
        result
    ):
        """
        Log one runtime action.

        The document requires inputs and outputs
        to be logged, not just messages.
        """

        record = {
            "timestamp":
                datetime.now().isoformat(),

            "step":
                self.current_step,

            "intent":
                intent,

            "action":
                action,

            "input":
                input_data,

            "output":
                result
        }

        self.audit_log.append(record)

        with open(
            AUDIT_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.audit_log,
                file,
                indent=4
            )

    # ========================================================
    # BUDGET CHECK
    # ========================================================

    def check_budget(self):

        if self.actions_used >= self.budget:

            raise RuntimeError(
                "Runtime action budget exceeded."
            )

        self.actions_used += 1

    # ========================================================
    # RUN ONE STEP
    # ========================================================

    def run_step(
        self,
        intent,
        action_name,
        action,
        input_data=None,
        risky=False
    ):
        """
        Execute one controlled runtime step.
        """

        self.check_budget()

        self.current_step += 1

        # ----------------------------------------------------
        # APPROVAL GATE
        # ----------------------------------------------------

        if risky or action_name in self.gates:

            approval = input(
                f"\nAPPROVAL REQUIRED for "
                f"'{action_name}'. "
                f"Continue? (yes/no): "
            ).strip().lower()

            approval_result = {
                "approved":
                    approval in ["yes", "y"]
            }

            self.log(
                intent=intent,
                action=f"{action_name}_approval",
                input_data=input_data,
                result=approval_result
            )

            if approval not in ["yes", "y"]:

                raise PermissionError(
                    f"Action '{action_name}' "
                    f"was not approved."
                )

        # ----------------------------------------------------
        # EXECUTE ACTION
        # ----------------------------------------------------

        result = action()

        # ----------------------------------------------------
        # AUDIT
        # ----------------------------------------------------

        self.log(
            intent=intent,
            action=action_name,
            input_data=input_data,
            result=result
        )

        # ----------------------------------------------------
        # CHECKPOINT
        # ----------------------------------------------------

        self.save_checkpoint()

        return result

    # ========================================================
    # CHECKPOINT
    # ========================================================

    def set_state(self, key, value):

        self.state[key] = value

    def save_checkpoint(self):

        checkpoint = {
            "current_step":
                self.current_step,

            "actions_used":
                self.actions_used,

            "state":
                self.state
        }

        with open(
            CHECKPOINT_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                checkpoint,
                file,
                indent=4,
                default=str
            )

    # ========================================================
    # RESUME
    # ========================================================

    def resume(self):

        if not CHECKPOINT_FILE.exists():

            print(
                "\nNo checkpoint found."
            )

            return False

        with open(
            CHECKPOINT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            checkpoint = json.load(file)

        self.current_step = checkpoint.get(
            "current_step",
            0
        )

        self.actions_used = checkpoint.get(
            "actions_used",
            0
        )

        self.state = checkpoint.get(
            "state",
            {}
        )

        print("\n" + "=" * 70)
        print("RUNTIME RESUMED")
        print("=" * 70)

        print(
            f"\nResumed from step: "
            f"{self.current_step}"
        )

        print(
            f"Actions already used: "
            f"{self.actions_used}"
        )

        print("\nRecovered state:")

        print(
            json.dumps(
                self.state,
                indent=4
            )
        )

        return True

    # ========================================================
    # DISPLAY AUDIT
    # ========================================================

    def show_audit(self):

        print("\n" + "=" * 70)
        print("AUDIT LOG")
        print("=" * 70)

        for record in self.audit_log:

            print(
                f"\nStep: {record['step']}"
            )

            print(
                f"Intent: {record['intent']}"
            )

            print(
                f"Action: {record['action']}"
            )

            print(
                f"Input: {record['input']}"
            )

            print(
                f"Output: {record['output']}"
            )

    # ========================================================
    # DISPLAY CHECKPOINT
    # ========================================================

    def show_checkpoint(self):

        print("\n" + "=" * 70)
        print("CHECKPOINT")
        print("=" * 70)

        if not CHECKPOINT_FILE.exists():

            print("\nNo checkpoint available.")
            return

        with open(
            CHECKPOINT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            checkpoint = json.load(file)

        print(
            json.dumps(
                checkpoint,
                indent=4
            )
        )