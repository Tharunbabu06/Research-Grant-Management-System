# ============================================================
# LAB 4 - SESSION STATE
# Short-term memory for the current agent run
# ============================================================


class SessionState:
    """
    Stores information that belongs only to the
    current execution/run.

    This is NOT long-term memory.
    """

    def __init__(self):
        self.current_request = None
        self.current_plan = None
        self.draft = None

    def set_request(self, request):
        self.current_request = request

    def set_plan(self, plan):
        self.current_plan = plan

    def set_draft(self, draft):
        self.draft = draft

    def show_state(self):
        print("\n" + "=" * 70)
        print("SHORT-TERM SESSION STATE")
        print("=" * 70)

        print("\nCurrent Request:")
        print(self.current_request)

        print("\nCurrent Plan:")
        print(self.current_plan)

        print("\nCurrent Draft:")
        print(self.draft)