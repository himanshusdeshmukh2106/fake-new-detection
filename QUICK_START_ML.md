# Quick Start: Adding ML to Fake News Detection

## 🚀 Easiest ML Enhancements (Start Here!)

### 1. Semantic Similarity with Sentence-BERT (10 minutes)

**Already have the package!** Just need to use it.

Create `factcheck/ml_models/semantic_matcher.py`:

```python
from sentence_transformers import SentenceTransformer, util
import numpy as np

class SemanticMatcher:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    
    def rank_evidence(self, claim: str, evidences: list) -> list:
        """Rank evidences by semantic similarity to claim"""
        claim_emb = self.model.encode(claim, convert_to_tensor=True)
        evidence_texts = [e['text'] if isinstance(e, dict) else e for e in evidences]
        evidence_embs = self.model.encode(evidence_texts, convert_to_tensor=True)
        
        scores = util.cos_sim(claim_emb, evidence_embs)[0]
        ranked_indices = scores.argsort(descending=True)
        
        return [(evidences[i], float(scores[i])) for i in ranked_indices]
```

**Integration:** Add to `ClaimVerify.py` to prioritize relevant evidence.

---

### 2. Source Credibility Scorer (30 minutes)

Create `factcheck/ml_models/source_credibility.py`:

```python
import re
from urllib.parse import urlparse

class SourceCredibilityScorer:
    def __init__(self):
        # Trusted domains (expand this list)
        self.trusted_domains = {
            'reuters.com': 0.95,
            'apnews.com': 0.95,
            'bbc.com': 0.90,
            'nytimes.com': 0.85,
            'washingtonpost.com': 0.85,
            'theguardian.com': 0.85,
            'wikipedia.org': 0.80,
        }
        
        # Suspicious patterns
        self.suspicious_patterns = [
            r'\.blogspot\.',
            r'\.wordpress\.',
            r'fake',
            r'hoax',
            r'satire',
        ]
    
    def score_url(self, url: str) -> dict:
        """Score a URL's credibility (0-1)"""
        domain = urlparse(url).netloc.lower()
        domain = domain.replace('www.', '')
        
        # Check trusted list
        if domain in self.trusted_domains:
            return {
                'score': self.trusted_domains[domain],
                'reason': 'Trusted source',
                'category': 'high'
            }
        
        # Check suspicious patterns
        for pattern in self.suspicious_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return {
                    'score': 0.3,
                    'reason': f'Suspicious pattern: {pattern}',
                    'category': 'low'
                }
        
        # Check HTTPS
        score = 0.5
        if url.startswith('https://'):
            score += 0.1
        
        # Check domain length (shorter usually better)
        if len(domain) < 20:
            score += 0.1
        
        return {
            'score': min(score, 1.0),
            'reason': 'Unknown source',
            'category': 'medium'
        }
```

---

### 3. Claim Type Classifier (1 hour)

Uses spaCy (already installed) for basic classification.

Create `factcheck/ml_models/claim_classifier.py`:
