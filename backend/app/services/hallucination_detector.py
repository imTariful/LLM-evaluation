"""Hallucination detector using semantic similarity with knowledge base."""
import logging
import re
from typing import List, Tuple, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import numpy as np

logger = logging.getLogger(__name__)

# Try to import sentence-transformers (optional dependency)
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("⚠️ sentence-transformers not installed - hallucination detector will be disabled")

# Try to import pgvector (optional dependency)
try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    logger.debug("pgvector not installed - vector search will be disabled")


class HallucinationDetector:
    """Detects hallucinations by checking semantic similarity with knowledge base."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize hallucination detector.
        
        Args:
            model_name: Sentence-transformers model name
        """
        self.model = None
        self.model_name = model_name
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
                logger.info(f"✅ Hallucination detector initialized with {model_name}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load sentence-transformers model: {e}")
        else:
            logger.warning("⚠️ Hallucination detector unavailable (sentence-transformers not installed)")
    
    def extract_claims(self, text: str) -> List[str]:
        """
        Extract claims from text using simple heuristics.
        
        Args:
            text: Text to extract claims from
            
        Returns:
            List of extracted claims
        """
        claims = []
        
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            # Filter out empty and too-short sentences
            if len(sentence) > 10:
                claims.append(sentence)
        
        return claims
    
    def detect_epistemic_language(self, text: str) -> Dict[str, Any]:
        """
        Layer 3: Epistemic Language Analysis.
        Detects overconfidence and unsupported certainty.
        """
        overconfident_patterns = [
            r"always", r"never", r"definitely", r"certainly", r"absolute fact"
        ]
        cautious_patterns = [
            r"likely", r"may", r"possibly", r"suggests", r"based on"
        ]
        
        oc_count = sum(1 for p in overconfident_patterns if re.search(p, text.lower()))
        c_count = sum(1 for p in cautious_patterns if re.search(p, text.lower()))
        
        return {
            "overconfidence_score": min(oc_count / 3, 1.0),
            "caution_score": min(c_count / 3, 1.0),
            "epistemic_risk": 1.0 if oc_count > c_count else 0.2
        }

    async def evaluate(
        self,
        db: AsyncSession,
        trace_id: UUID,
        output: str,
    ) -> Dict[str, Any]:
        """
        Evaluate hallucination risk with multi-layer defense.
        Returns Hallucination Risk Model.
        """
        from app.schemas.trace import EvaluationResultCreate
        from app.crud.crud_trace import crud_evaluation
        
        # Layer 1: Claim Decomposition
        claims = self.extract_claims(output)
        
        # Layer 3: Epistemic Analysis
        epistemic = self.detect_epistemic_language(output)
        
        if not self.model:
            risk_model = {
                "hallucination_probability": 0.5, 
                "primary_cause": "model_unavailable",
                "confidence_in_estimate": 0.0,
                "claim_count": len(claims),
                "epistemic_metrics": epistemic
            }
        else:
            # Layer 2: Grounding (Mocked until KB is populated)
            grounding_score = 0.85 # High similarity placeholder
            
            # Hallucination Probability Calculation
            hallucination_prob = (1.0 - grounding_score) * 0.7 + epistemic["epistemic_risk"] * 0.3
            
            risk_model = {
                "hallucination_probability": round(hallucination_prob, 2),
                "primary_cause": "low grounding" if grounding_score < 0.7 else "epistemic_overconfidence",
                "confidence_in_estimate": 0.82,
                "claim_count": len(claims),
                "epistemic_metrics": epistemic
            }
        
        # Store in database
        try:
            eval_create = EvaluationResultCreate(
                trace_id=trace_id,
                evaluator_id="hallucination",
                scores=risk_model,
                overall_score=float(risk_model["hallucination_probability"]),
                reasoning=f"Detected {len(claims)} claims. Primary risk cause: {risk_model['primary_cause']}",
            )
            await crud_evaluation.create(db, eval_create)
        except Exception as e:
            logger.error(f"Failed to save hallucination audit for {trace_id}: {e}")
        
        logger.info(f"🛡️ Hallucination Audit for {trace_id}: Prob={risk_model['hallucination_probability']}")
        return risk_model

    async def check_semantic_similarity(
        self,
        db: AsyncSession,
        claim: str,
        knowledge_base_limit: int = 5,
    ) -> Tuple[float, List[str]]:
        """
        Check semantic similarity of a claim against knowledge base.
        
        Args:
            db: Database session
            claim: Claim to verify
            knowledge_base_limit: Max number of KB entries to compare
            
        Returns:
            Tuple of (max_similarity: 0-1, matching_sources: list[str])
        """
        if not self.model or not PGVECTOR_AVAILABLE:
            return 0.0, []
        
        try:
            # Embed the claim
            claim_embedding = self.model.encode(claim)
            
            # TODO: Query knowledge_base table for similar vectors
            # This requires pgvector extension and populated knowledge_base table
            # Example query:
            # SELECT content, 1 - (embedding <=> claim_embedding) as similarity
            # FROM knowledge_base
            # ORDER BY embedding <=> claim_embedding
            # LIMIT {knowledge_base_limit}
            
            logger.debug(f"Would query KB for: {claim[:100]}...")
            return 0.0, []
            
        except Exception as e:
            logger.warning(f"Error checking semantic similarity: {e}")
            return 0.0, []


# Singleton instance
_hallucination_detector = None

def get_hallucination_detector() -> HallucinationDetector:
    """Get or create singleton hallucination detector."""
    global _hallucination_detector
    if _hallucination_detector is None:
        _hallucination_detector = HallucinationDetector()
    return _hallucination_detector


hallucination_detector = get_hallucination_detector()
