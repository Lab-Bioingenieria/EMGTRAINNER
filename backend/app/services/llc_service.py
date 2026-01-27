import os
import csv
import math
from typing import Dict, List, Any, Optional

class LLCService:
    def __init__(self, storage_dir: str = "storage/sessions"):
        self.storage_dir = storage_dir

    def _get_patient_dir(self, patient_name: str) -> str:
        safe_name = "".join(c for c in patient_name if c.isalnum() or c in (' ', '_', '-')).strip()
        if not safe_name:
            safe_name = "Guest"
        return os.path.join(self.storage_dir, safe_name)

    def load_patient_data(self, patient_name: str) -> Dict[str, List[List[float]]]:
        """
        Load all EMG data for a patient, grouped by label.
        Returns: { "Fist": [[emg1, emg2, emg3], ...], "Rest": [...] }
        """
        patient_dir = self._get_patient_dir(patient_name)
        data_by_label: Dict[str, List[List[float]]] = {}

        if not os.path.exists(patient_dir):
            return {}

        for filename in os.listdir(patient_dir):
            if not filename.endswith(".csv"):
                continue
            
            filepath = os.path.join(patient_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            label = row.get('label', 'Unknown')
                            # Parse EMGs. Assuming they are float capable strings
                            # If emg1 is "200.0", float() works.
                            val = [
                                float(row.get('emg1', 0)),
                                float(row.get('emg2', 0)),
                                float(row.get('emg3', 0))
                            ]
                            
                            if label not in data_by_label:
                                data_by_label[label] = []
                            data_by_label[label].append(val)
                        except (ValueError, KeyError):
                            continue
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                continue
                
        return data_by_label

    def _euclidean_dist(self, p1: List[float], p2: List[float]) -> float:
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))

    def _mean_point(self, points: List[List[float]]) -> List[float]:
        if not points:
            return [0.0, 0.0, 0.0]
        n = len(points)
        sums = [sum(col) for col in zip(*points)]
        return [s / n for s in sums]

    def _calculate_variance(self, points: List[List[float]], centroid: List[float]) -> float:
        """Intra-class dispersion (mean squared distance to centroid)"""
        if not points:
            return 0.0
        
        sq_dists = [sum((a - b) ** 2 for a, b in zip(p, centroid)) for p in points]
        return sum(sq_dists) / len(points)

    def calculate_separability_index(self, patient_name: str) -> Dict[str, Any]:
        """
        Calculate J for each gesture.
        J = Min_InterClass_Dist / IntraClass_Variance
        """
        data = self.load_patient_data(patient_name)
        if len(data) < 2:
            return {} # Need at least 2 classes to compare

        # 1. Calculate Centroids and Variances
        stats = {}
        for label, points in data.items():
            centroid = self._mean_point(points)
            variance = self._calculate_variance(points, centroid)
            stats[label] = {
                "centroid": centroid,
                "variance": variance,
                "count": len(points),
                "j_score": 0.0
            }

        # 2. Calculate J
        # J_i = min(dist(centroid_i, centroid_j)) / variance_i
        for label_i, stat_i in stats.items():
            min_inter_dist = float('inf')
            
            # Find closest neighbor
            for label_j, stat_j in stats.items():
                if label_i == label_j:
                    continue
                d = self._euclidean_dist(stat_i["centroid"], stat_j["centroid"])
                if d < min_inter_dist:
                    min_inter_dist = d
            
            # Avoid division by zero
            variance = stat_i["variance"] if stat_i["variance"] > 1e-6 else 1e-6
            
            j_score = min_inter_dist / variance
            stat_i["j_score"] = j_score
            stat_i["min_inter_dist"] = min_inter_dist

        return stats

    def suggest_next_gesture(self, patient_name: str) -> Dict[str, Any]:
        stats = self.calculate_separability_index(patient_name)
        
        if not stats:
            # Fallback if no data
            return {"next_gesture": None, "reason": "No data available"}

        # Calculate Final Selection Score
        # Score = J * (1 + penalty * count_factor)
        # We want the LOWEST score, so typically we look for LOW J (bad separability).
        # But if we practice it a lot, we want to skip it, so we need to INCREASE the score if practiced a lot?
        # User said: "Dividas el resultado por la cantidad de veces".
        # User Prompt: "Ponderación... dividas el resultado por la cantidad de veces... evita que la máquina pida el mismo gesto infinitas veces"
        
        # Wait, if I divide by count: Low J (bad) / High Count = Very Low Score -> Selected AGAIN.
        # This is opposite of what we want.
        # If I have a hard gesture (Low J), I want to practice it.
        # If I practice it 100 times, I want to STOP practicing it.
        # So I want the selection metric to become "Better" (Higher) so it's NOT selected (since we select Min).
        # So I should MULTIPLY by count.
        
        # Score = J * log(Count + 1)  (Using log to dampen effect)
        # Low J (0.1) * 1 = 0.1 -> Selected
        # Low J (0.1) * 100 = 10 -> Not Selected (if others are 2.0)
        
        scores = {}
        penalty_factor = 0.5 # Adjustable
        
        for label, stat in stats.items():
            # Count here is number of *samples* (rows). We ideally want number of *sessions* or *blocks*, but rows is proxy for time spent.
            # Raw rows might be huge (thousands). Use log10.
            count = stat["count"]
            weight = math.log10(count + 1) if count > 0 else 1.0
            
            # J is what we want to improve. Low J = Bad.
            # We select Min(Score).
            # Score = J * weight.
            # If J is small (bad), Score is small -> Selected.
            # If weight is huge (practiced a lot), Score becomes big -> Not Selected.
            
            final_score = stat["j_score"] * weight
            scores[label] = {
                "j": stat["j_score"],
                "count": count,
                "score": final_score
            }

        # Select min score
        best_candidate = min(scores.items(), key=lambda x: x[1]["score"])
        
        return {
            "next_gesture": best_candidate[0],
            "debug_scores": scores
        }

llc_service = LLCService()
