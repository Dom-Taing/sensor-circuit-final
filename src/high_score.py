import json
import time

class HighScoreManager:
    def __init__(self, filename="high_scores.json"):
        self.filename = filename
        self.high_scores = self.load_scores()
        
    def load_scores(self):
        """Load high scores from file, create empty list if file doesn't exist"""
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except (OSError, ValueError):
            # File doesn't exist or is corrupted, start with empty list
            return []
    
    def save_scores(self):
        """Save high scores to file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.high_scores, f)
        except OSError:
            print("Failed to save high scores")
    
    def add_score(self, initials, score, misses):
        """Add a new score to the high score list"""
        new_score = {
            "initials": initials,
            "score": score,
            "misses": misses,
            "timestamp": time.time()
        }
        
        self.high_scores.append(new_score)
        # Sort by score (descending), then by misses (ascending)
        self.high_scores.sort(key=lambda x: (-x["score"], x["misses"]))
        
        # Keep only top 10 scores
        self.high_scores = self.high_scores[:10]
        self.save_scores()
        
        # Return the rank (1-based) of the new score, or None if not in top 10
        for i, score_entry in enumerate(self.high_scores):
            if score_entry == new_score:
                return i + 1
        return None
    
    def is_high_score(self, score, misses):
        """Check if a score qualifies for the high score list"""
        if len(self.high_scores) < 10:
            return True
        
        # Check if better than worst score
        worst_score = self.high_scores[-1]
        return (score > worst_score["score"] or 
                (score == worst_score["score"] and misses < worst_score["misses"]))
    
    def get_top_scores(self, count=10):
        """Get the top N scores"""
        return self.high_scores[:count]

