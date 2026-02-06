import json
from openai import OpenAI, NotFoundError
from .schema import TradeOrder, ParserResponse
from pydantic import ValidationError



class TradeParser:
    def __init__(self, api_key: str, model: str = "deepseek-chat", base_url: str = "https://api.deepseek.com"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def parse_text(self, text: str) -> ParserResponse:
        system_prompt = (
            """
            You are a trading signal parser.
            
            Your task is to convert a user's raw trade message into one or more
            VALID JSON trade orders.

            CRITICAL RULES:
            - Output JSON ONLY. No explanations. No markdown.
            - Ignore emotional language, emojis, and commentary.
            - Extract only actionable trading information.
            - NEVER guess missing numeric values.
            - If a required value is missing, return an error object instead.
            - Normalize symbols (e.g., gold → XAUUSD).
            - Normalize actions (buy/long → BUY, sell/short → SELL).
            - Interpret "now" as a MARKET order.
            - Interpret ranges (e.g., 4327-4330) as LIMIT orders using the midpoint.
            - If multiple take-profit (TP) values exist:
              - Create a MAXIMUM of 2 orders
              - Use the first two TP levels ONLY
            - Each order must be independent and complete.

            You are not allowed to output anything except valid JSON.
            """
        )

        developer_prompt = (
            """
            OUTPUT FORMAT:

            If the signal is valid, output a JSON ARRAY of trade orders.
            If invalid, output a single JSON object with an "error" field.

            Each trade order MUST follow this schema:

            {
                "action": "BUY | SELL",
                "symbol": "string",
                "order_type": "MARKET | LIMIT",
                "volume": number | null,
                "price": number | null,
                "stop_loss": number,
                "take_profit": number,
                "time_in_force": "GTC",
                "comment": null
            }

            INTERPRETATION RULES:

            1. ORDER TYPE
            - "now" → MARKET order (price = null)
            - "limit" or price range → LIMIT order
            - price range A-B → price = (A + B) / 2

            2. SYMBOL NORMALIZATION
            - gold → XAUUSD
            - indices must be preserved as-is (e.g., USTEC_X1000m)

            3. TAKE PROFIT RULES
            - Multiple TP lines → create multiple orders
            - Maximum of 2 orders only
            - Use TP values in the order they appear
            - Ignore "tp every X pip" if explicit TP values exist
            - If only "tp every X pip" exists and no numeric TP is given → error

            4. STOP LOSS
            - stop loss is REQUIRED
            - If missing → error

            5. VOLUME
            - If not specified → set to 0.05

            6. INVALID CASE
            Return:
            {
                "error": "clear description of what is missing or ambiguous"
            }
            """
        )

        user_prompt = (f"""{text}""")

        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "assistant" if self.model=="deepseek-chat" else "developer", "content": developer_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=TradeOrder,
            )
            
            order = response.choices[0].message.parsed
            return ParserResponse(success=True, order=order, raw_text=text)
        
        except ValidationError as exc:
            print(repr(exc.errors()[0]['type']))
        except NotFoundError as ntf:
            print(f"OpenAI client not found: {ntf}")
        except Exception as e:
            return ParserResponse(success=False, error_message=e, raw_text=text)

# Quick Test helper
if __name__ == "__main__":
    # Ensure you have OPENAI_API_KEY in your .env
    parser = TradeParser("AIzaSyDvYIM7vqKM86dfWzFmMKbsDmfqZsd6iBw", model="gemini-2.5-flash", base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
    result = parser.parse_text("""Buy 0.5 lots of EURUSD at market SL 1.0500 TP 1.1000""")
    print(result.model_dump_json(indent=2))