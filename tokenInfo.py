import httpx


class TokenInfo:
    def __init__(self):
        pass

    @staticmethod
    async def get_token_info(token_mint_address):
        """Get Token Info"""
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }
        url = f"https://gmgn.ai/defi/quotation/v1/tokens/sol/{token_mint_address}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()["data"]["token"]
            else:
                return {}
            
    @staticmethod
    def convert_price_to_string(price):
        # Price is a float number, convert it to a string
        price_str = "{:.10f}".format(price).rstrip('0')
        
        # Find the position of the dot
        dot_position = price_str.find('.')
        zero_count = 0
        for char in price_str[dot_position+1:]:
            if char == '0':
                zero_count += 1
            else:
                break
        
        # If there are more than 2 continuous zeros, convert them to a placeholder
        if zero_count > 2:
            # Convert the price to a string with a placeholder
            converted_price = price_str[:dot_position+2] + "{" + str(zero_count-1) + "}" + price_str[dot_position+1+zero_count:]
        else:
            # Convert the price to a string without a placeholder
            converted_price = price_str
        
        return converted_price
    
    @staticmethod
    def convert_volume_to_string(volume):
        # Covert volume to a string
        if volume > 1000000000:
            volume_str = "{:.2f}".format(volume/1000000000) + "B"
        elif volume > 1000000:
            volume_str = "{:.2f}".format(volume/1000000) + "M"
        else:
            volume_str = "{:.2f}".format(volume/1000) + "K"
        
        return volume_str
    