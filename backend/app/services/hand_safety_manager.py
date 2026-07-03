class SafetyManager:
    def __init__(self, dxl):
        self.dxl = dxl

    def emergency_stop(self, motor_ids):
        for mid in motor_ids:
            self.dxl.disable_torque(mid)
