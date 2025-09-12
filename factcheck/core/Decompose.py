from factcheck.utils.logger import CustomLogger
import nltk

logger = CustomLogger(__name__).getlog()


class Decompose:
    def __init__(self, llm_client, prompt):
        """Initialize the Decompose class

        Args:
            llm_client (BaseClient): The LLM client used for decomposing documents into claims.
            prompt (BasePrompt): The prompt used for fact checking.
        """
        self.llm_client = llm_client
        self.prompt = prompt
        self.doc2sent = self._nltk_doc2sent

    def _nltk_doc2sent(self, text: str):
        """Split the document into sentences using nltk

        Args:
            text (str): the document to be split into sentences

        Returns:
            list: a list of sentences
        """

        sentences = nltk.sent_tokenize(text)
        sentence_list = [s.strip() for s in sentences if len(s.strip()) >= 3]
        return sentence_list

    def getclaims(self, doc: str, num_retries: int = 3, prompt: str = None) -> list[str]:
        """Use GPT to decompose a document into claims

        Args:
            doc (str): the document to be decomposed into claims
            num_retries (int, optional): maximum attempts for GPT to decompose the document into claims. Defaults to 3.

        Returns:
            list: a list of claims
        """
        if prompt is None:
            user_input = self.prompt.decompose_prompt.format(doc=doc).strip()
        else:
            user_input = prompt.format(doc=doc).strip()

        claims = None
        messages = self.llm_client.construct_message_list([user_input])
        for i in range(num_retries):
            response = self.llm_client.call(
                messages=messages,
                num_retries=1,
                seed=42 + i,
            )
            try:
                # Clean the response to handle malformed JSON from Gemini
                cleaned_response = response.strip()
                
                # Try to fix common JSON formatting issues
                if cleaned_response.startswith('{') and not cleaned_response.endswith('}'):
                    # Missing closing brace
                    cleaned_response += '}'
                elif cleaned_response.startswith('{{') and not cleaned_response.endswith('}}'):
                    # Double braces from Gemini, fix it
                    cleaned_response = cleaned_response[1:-1] if cleaned_response.endswith('}') else cleaned_response[1:] + '}'
                
                # Remove any markdown code blocks
                import re
                cleaned_response = re.sub(r'```(?:json)?\s*([\s\S]*?)\s*```', r'\1', cleaned_response)
                cleaned_response = cleaned_response.strip()
                
                # Try json.loads first, fallback to eval
                try:
                    import json
                    parsed_response = json.loads(cleaned_response)
                except json.JSONDecodeError:
                    # Fallback to eval for cases where JSON parser fails
                    parsed_response = eval(cleaned_response)
                
                claims = parsed_response["claims"]
                if isinstance(claims, list) and len(claims) > 0:
                    break
            except Exception as e:
                logger.error(f"Parse LLM response error {e}, response is: {response}")
                logger.error(f"Parse LLM response error, prompt is: {messages}")
        if isinstance(claims, list):
            return claims
        else:
            logger.info("It does not output a list of sentences correctly, return self.doc2sent_tool split results.")
            claims = self.doc2sent(doc)
        return claims

    def restore_claims(self, doc: str, claims: list, num_retries: int = 3, prompt: str = None) -> dict[str, dict]:
        """Use GPT to map claims back to the document

        Args:
            doc (str): the document to be decomposed into claims
            claims (list[str]): a list of claims to be mapped back to the document
            num_retries (int, optional): maximum attempts for GPT to decompose the document into claims. Defaults to 3.

        Returns:
            dict: a dictionary of claims and their corresponding text spans and start/end indices.
        """

        def restore(claim2doc):
            claim2doc_detail = {}
            flag = True
            for claim, sent in claim2doc.items():
                # Handle empty or None text spans
                if not sent or sent.strip() == "":
                    # Try to find a reasonable text span for the claim
                    # Look for key words from the claim in the document
                    claim_words = claim.lower().split()
                    best_match = ""
                    best_score = 0
                    
                    # Simple keyword matching to find relevant text
                    for i in range(len(doc) - 10):
                        text_chunk = doc[i:i+50].lower()
                        score = sum(1 for word in claim_words if word in text_chunk)
                        if score > best_score:
                            best_score = score
                            # Find sentence boundaries
                            start = max(0, doc.rfind('\n', 0, i))
                            end = doc.find('\n', i+50)
                            if end == -1:
                                end = min(len(doc), i+100)
                            best_match = doc[start:end].strip()
                    
                    if best_match:
                        sent = best_match
                        logger.warning(f"Empty text span for claim '{claim}', using fallback: '{sent[:50]}...'")
                    else:
                        # Last resort: use the claim itself as text
                        sent = claim
                        logger.warning(f"No text span found for claim '{claim}', using claim as text")
                        flag = False
                
                st = doc.find(sent)
                if st != -1:
                    claim2doc_detail[claim] = {"text": sent, "start": st, "end": st + len(sent)}
                else:
                    # If exact match fails, try to find the best position
                    # Use the claim text and position it appropriately
                    claim2doc_detail[claim] = {"text": sent, "start": 0, "end": len(sent)}
                    flag = False
                    logger.warning(f"Text span '{sent[:30]}...' not found in document for claim '{claim[:30]}...'")

            cur_pos = -1
            texts = []
            for k, v in claim2doc_detail.items():
                if v["start"] < cur_pos + 1 and v["end"] > cur_pos:
                    v["start"] = cur_pos + 1
                    flag = False
                elif v["start"] < cur_pos + 1 and v["end"] <= cur_pos:
                    v["start"] = v["end"]  # temporarily ignore this span
                    flag = False
                elif v["start"] > cur_pos + 1:
                    v["start"] = cur_pos + 1
                    flag = False
                v["text"] = doc[v["start"] : v["end"]]
                texts.append(v["text"])
                claim2doc_detail[k] = v
                cur_pos = v["end"]

            return claim2doc_detail, flag

        if prompt is None:
            user_input = self.prompt.restore_prompt.format(doc=doc, claims=claims).strip()
        else:
            user_input = prompt.format(doc=doc, claims=claims).strip()

        messages = self.llm_client.construct_message_list([user_input])

        tmp_restore = {}
        for i in range(num_retries):
            response = self.llm_client.call(
                messages=messages,
                num_retries=1,
                seed=42 + i,
            )
            try:
                # Clean the response to handle malformed JSON from Gemini
                cleaned_response = response.strip()
                
                # Try to fix common JSON formatting issues
                if cleaned_response.startswith('{') and not cleaned_response.endswith('}'):
                    # Missing closing brace
                    cleaned_response += '}'
                elif cleaned_response.startswith('{{') and not cleaned_response.endswith('}}'):
                    # Double braces from Gemini, fix it
                    cleaned_response = cleaned_response[1:-1] if cleaned_response.endswith('}') else cleaned_response[1:] + '}'
                
                # Remove any markdown code blocks
                import re
                cleaned_response = re.sub(r'```(?:json)?\s*([\s\S]*?)\s*```', r'\1', cleaned_response)
                cleaned_response = cleaned_response.strip()
                
                # Try json.loads first, fallback to eval
                try:
                    import json
                    claim2doc = json.loads(cleaned_response)
                except json.JSONDecodeError:
                    # Fallback to eval for cases where JSON parser fails
                    claim2doc = eval(cleaned_response)
                
                assert len(claim2doc) == len(claims)
                claim2doc_detail, flag = restore(claim2doc)
                if flag:
                    return claim2doc_detail
                else:
                    tmp_restore = claim2doc_detail
                    # Instead of raising exception, log warning and continue with partial results
                    logger.warning(f"Restore claims partially satisfied. Using available mappings. Retry {i+1}/{num_retries}")
                    if i == num_retries - 1:  # Last retry
                        logger.info("Using partial claim restoration results due to text span mapping issues")
                        return tmp_restore
                    # Continue to next retry
                    continue
            except Exception as e:
                logger.error(f"Parse LLM response error {e}, response is: {response}")
                logger.error(f"Parse LLM response error, prompt is: {messages}")

        return tmp_restore
