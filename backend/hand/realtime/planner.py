import time
from typing import Optional
from math import radians
from .models import GestureEvent, PlannedGesture, JointEuler
from hand.models.gestures import GESTURES


class GesturePlanner:
    def __init__(self, min_conf: float = 0.6, cooldown_s: float = 0.15, respect_play: bool = True):
        self.min_conf = min_conf
        self.cooldown_s = cooldown_s
        self.respect_play = respect_play

        self.current_gesture: str | None = None
        self.busy_until_ts: float = 0.0
        self.last_ts: float = 0.0
        self.last_gesture_ts: dict[str, float] = {}

        # priority (higher = more priority)
        self.priority = {
            'ZERO': 100,
            'REST': 90,
            'OPEN': 50,
            'CLOSE': 50,
            'PINCH': 60,
        }

        # per-gesture cooldowns
        self.cooldowns = {
            'ZERO': 0.5,
            'REST': 0.2,
            'PINCH': 0.3,
        }

        # simple safe transitions map (if not present, allow direct)
        self.force_rest_between = set(['CLOSE', 'PINCH'])

    def accept(self, event: GestureEvent) -> Optional[PlannedGesture]:
        now = time.time()
        self.last_ts = event.ts or now

        if event.conf < self.min_conf:
            return None

        # global cooldown (small), and gesture-specific cooldown
        if (now - self.last_ts) < self.cooldown_s:
            return None
        g_cd = self.cooldowns.get(event.gesture.upper(), 0.0)
        lastg = self.last_gesture_ts.get(event.gesture.upper(), 0.0)
        if (now - lastg) < g_cd:
            return None

        # respect ongoing play
        if self.respect_play and now < self.busy_until_ts:
            return None

        newg = event.gesture.upper()

        # if same as current, may choose to loop/hold
        if newg == self.current_gesture:
            pg = PlannedGesture(gesture=newg, play_mode='hold')
            # extend busy
            self.busy_until_ts = now + 1.0
            self.last_gesture_ts[newg] = now
            return pg

        # if transition involves dangerous gestures, insert REST
        intermediate = None
        if self.current_gesture in self.force_rest_between or newg in self.force_rest_between:
            intermediate = ['REST']

        # accept and set busy
        # build joint targets if available from hand model definitions
        joints_map: dict[str, JointEuler] = {}
        try:
            gesture_defs = GESTURES.get(newg)
            if gesture_defs:
                # pick a profile available
                profile = next(iter(gesture_defs.keys()))
                defn = gesture_defs.get(profile, {})
                for finger, joints in defn.items():
                    for jname, deg in joints.items():
                        bone = f"{finger}_{jname}".lower().replace(' ', '_')
                        rad = radians(float(deg))
                        joints_map[bone] = JointEuler(x=rad, y=0.0, z=0.0)
        except Exception:
            joints_map = {}

        pg = PlannedGesture(gesture=newg, play_mode='once', intermediate=intermediate, joints=joints_map or None)
        self.current_gesture = newg
        self.busy_until_ts = now + 1.0
        self.last_gesture_ts[newg] = now
        return pg
