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
        """Identify whether candidate claims are worth fact checking using ML (with LLM fallback).

        Args:
            texts (list[str]): a list of texts to identify whether they are worth fact checking
            num_retries (int, optional): maximum attempts for LLM to identify checkworthy claims. Defaults to 3.
            prompt (str, optional): custom prompt for LLM. Defaults to None.
            use_ml (bool, optional): whether to use ML classifier first. Defaults to True.
            ml_confidence_threshold (float, optional): minimum confidence for ML predictions. Defaults to 0.7.

        Returns:
            tuple: (checkworthy_claims, claim2checkworthy) - list of checkworthy claims and mapping dict
        """
        # Try ML classifier first if available and enabled
        if self.use_ml and use_ml and self.ml_classifier is not None:
            try:
                logger.info(f"🤖 Using ML classifier for {len(texts)} claims...")
                
                # Classify all claims
                results = self.ml_classifier.classify_batch(texts)
                
                # Separate high-confidence and low-confidence predictions
                high_conf_checkworthy = []
                high_conf_not_checkworthy = []
                low_conf_claims = []
                
                claim2checkworthy = {}
                
                for result in results:
                    claim = result['claim']
                    label = result['label']
                    confidence = result['confidence']
                    
                    if confidence >= ml_confidence_threshold:
                        # High confidence prediction
                        if label == 'checkworthy':
                            high_conf_checkworthy.append(claim)
                            claim2checkworthy[claim] = f"Yes - ML Classifier (confidence: {confidence:.1%})"
                        else:
                            high_conf_not_checkworthy.append(claim)
                            claim2checkworthy[claim] = f"No - ML Classifier: {label} (confidence: {confidence:.1%})"
                    else:
                        # Low confidence - will verify with LLM
                        low_conf_claims.append(claim)
                
                # Log ML performance
                total_filtered = len(high_conf_not_checkworthy)
                total_approved = len(high_conf_checkworthy)
                total_uncertain = len(low_conf_claims)
                
                logger.info(f"✅ ML Results: {total_approved} checkworthy, {total_filtered} filtered, {total_uncertain} uncertain")
                logger.info(f"💰 API calls saved: {total_filtered} ({total_filtered/len(texts)*100:.1f}%)")
                
                # If there are low-confidence claims, verify with LLM
                if low_conf_claims:
                    logger.info(f"🔄 Verifying {len(low_conf_claims)} low-confidence claims with LLM...")
                    try:
                        llm_checkworthy, llm_claim2checkworthy = self._llm_checkworthy(
                            low_conf_claims, num_retries, prompt
                        )
                        
                        # Merge results
                        checkworthy_claims = high_conf_checkworthy + llm_checkworthy
                        claim2checkworthy.update(llm_claim2checkworthy)
                        
                        logger.info(f"✅ LLM verified: {len(llm_checkworthy)}/{len(low_conf_claims)} as checkworthy")
                    except Exception as llm_error:
                        logger.warning(f"⚠️  LLM verification failed: {llm_error}")
                        logger.info(f"📊 Using ML predictions for low-confidence claims")
                        
                        # Use ML predictions even for low-confidence claims
                        for result in results:
                            if result['claim'] in low_conf_claims:
                                claim = result['claim']
                                if result['label'] == 'checkworthy':
                                    high_conf_checkworthy.append(claim)
                                    claim2checkworthy[claim] = f"Yes - ML Classifier (low confidence: {result['confidence']:.1%}, LLM unavailable)"
                                else:
                                    claim2checkworthy[claim] = f"No - ML Classifier: {result['label']} (low confidence: {result['confidence']:.1%}, LLM unavailable)"
                        
                        checkworthy_claims = high_conf_checkworthy
                        logger.info(f"✅ Accepted ML predictions for all claims")
                else:
                    checkworthy_claims = high_conf_checkworthy
                
                logger.info(f"🎯 Final: {len(checkworthy_claims)}/{len(texts)} claims are checkworthy")
                
                return checkworthy_claims, claim2checkworthy
                
            except Exception as e:
                logger.error(f"❌ ML classifier failed: {e}")
                logger.info("🔄 Falling back to LLM-only mode...")
        
        # Fallback to LLM-only mode
        logger.info(f"📡 Using LLM for {len(texts)} claims...")
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
