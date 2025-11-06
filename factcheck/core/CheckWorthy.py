from factcheck.utils.logger import CustomLogger
import os

logger = CustomLogger(__name__).getlog()


class Checkworthy:
    def __init__(self, llm_client, prompt):
        """Initialize the Checkworthy class

        Args:
            llm_client (BaseClient): The LLM client used for identifying checkworthiness of claims.
            prompt (BasePrompt): The prompt used for identifying checkworthiness of claims.
        """
        self.llm_client = llm_client
        self.prompt = prompt
        
        # Initialize ML classifier if available
        self.ml_classifier = None
        self.use_ml = False
        try:
            from factcheck.ml_models import ClaimClassifier
            model_path = os.path.join(os.path.dirname(__file__), '..', 'ml_models', 'trained_model')
            if os.path.exists(model_path):
                self.ml_classifier = ClaimClassifier(model_path)
                self.use_ml = True
                logger.info("✅ ML Claim Classifier loaded successfully")
                logger.info("🚀 ML-enhanced checkworthy detection enabled (API fallback available)")
            else:
                logger.warning("⚠️  ML model not found, using LLM-only mode")
        except Exception as e:
            logger.warning(f"⚠️  Could not load ML classifier: {e}")
            logger.info("📡 Using LLM-only mode for checkworthy detection")

    def identify_checkworthiness(self, texts: list[str], num_retries: int = 3, prompt: str = None, 
                                 use_ml: bool = True, ml_confidence_threshold: float = 0.7) -> tuple:
        """Identify whether candidate claims are worth fact checking using LLM (with ML fallback).

        Args:
            texts (list[str]): a list of texts to identify whether they are worth fact checking
            num_retries (int, optional): maximum attempts for LLM to identify checkworthy claims. Defaults to 3.
            prompt (str, optional): custom prompt for LLM. Defaults to None.
            use_ml (bool, optional): whether to use ML classifier as fallback. Defaults to True.
            ml_confidence_threshold (float, optional): minimum confidence for ML predictions. Defaults to 0.7.

        Returns:
            tuple: (checkworthy_claims, claim2checkworthy) - list of checkworthy claims and mapping dict
        """
        # Try LLM first (primary method)
        logger.info(f"📡 Using LLM for {len(texts)} claims (primary method)...")
        
        try:
            checkworthy_claims, claim2checkworthy = self._llm_checkworthy(texts, num_retries, prompt)
            logger.info(f"✅ LLM identified: {len(checkworthy_claims)}/{len(texts)} claims as checkworthy")
            return checkworthy_claims, claim2checkworthy
            
        except Exception as llm_error:
            logger.warning(f"⚠️  LLM checkworthy detection failed: {llm_error}")
            
            # Fallback to ML classifier if available
            if self.use_ml and use_ml and self.ml_classifier is not None:
                logger.info(f"🤖 Using ML classifier as fallback for {len(texts)} claims...")
                
                try:
                    # Classify all claims with ML
                    results = self.ml_classifier.classify_batch(texts)
                    
                    checkworthy_claims = []
                    claim2checkworthy = {}
                    
                    for result in results:
                        claim = result['claim']
                        label = result['label']
                        confidence = result['confidence']
                        
                        if label == 'checkworthy' and confidence >= ml_confidence_threshold:
                            checkworthy_claims.append(claim)
                            claim2checkworthy[claim] = f"Yes - ML Fallback (confidence: {confidence:.1%}, LLM failed)"
                        else:
                            claim2checkworthy[claim] = f"No - ML Fallback: {label} (confidence: {confidence:.1%}, LLM failed)"
                    
                    logger.info(f"✅ ML Fallback: {len(checkworthy_claims)}/{len(texts)} claims identified as checkworthy")
                    return checkworthy_claims, claim2checkworthy
                    
                except Exception as ml_error:
                    logger.error(f"❌ ML fallback also failed: {ml_error}")
                    logger.warning("⚠️  Both LLM and ML failed - treating all claims as checkworthy")
                    
                    # Last resort: treat all as checkworthy
                    claim2checkworthy = {claim: "Yes - Default (both LLM and ML failed)" for claim in texts}
                    return texts, claim2checkworthy
            else:
                logger.warning("⚠️  ML classifier not available - treating all claims as checkworthy")
                claim2checkworthy = {claim: "Yes - Default (LLM failed, no ML available)" for claim in texts}
                return texts, claim2checkworthy
        return self._llm_checkworthy(texts, num_retries, prompt)
    
    def _llm_checkworthy(self, texts: list[str], num_retries: int = 3, prompt: str = None) -> tuple:
        """Original LLM-based checkworthy detection (used as fallback).

        Args:
            texts (list[str]): a list of texts to identify whether they are worth fact checking
            num_retries (int, optional): maximum attempts for LLM. Defaults to 3.
            prompt (str, optional): custom prompt. Defaults to None.

        Returns:
            tuple: (checkworthy_claims, claim2checkworthy)
        """
        checkworthy_claims = texts
        joint_texts = "\n".join([str(i + 1) + ". " + j for i, j in enumerate(texts)])

        if prompt is None:
            user_input = self.prompt.checkworthy_prompt.format(texts=joint_texts)
        else:
            user_input = prompt.format(texts=joint_texts)

        messages = self.llm_client.construct_message_list([user_input])
        for i in range(num_retries):
            response = self.llm_client.call(messages, num_retries=1, seed=42 + i)
            try:
                claim2checkworthy = eval(response)
                valid_answer = list(
                    filter(
                        lambda x: x[1].startswith("Yes") or x[1].startswith("No"),
                        claim2checkworthy.items(),
                    )
                )
                checkworthy_claims = list(filter(lambda x: x[1].startswith("Yes"), claim2checkworthy.items()))
                checkworthy_claims = list(map(lambda x: x[0], checkworthy_claims))
                assert len(valid_answer) == len(claim2checkworthy)
                break
            except Exception as e:
                logger.error(f"====== Error: {e}, the LLM response is: {response}")
                logger.error(f"====== Our input is: {messages}")
        return checkworthy_claims, claim2checkworthy
