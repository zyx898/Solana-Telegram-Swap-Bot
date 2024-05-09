import httpx
from datetime import datetime
from jupiter_python_sdk.jupiter import Jupiter
from wallet import Wallet 
from spl.token.instructions import get_associated_token_address
from solders.pubkey import Pubkey # type: ignore

class Swap(Wallet):
    
    def __init__(self, rpc_url: str, private_key: str) -> None:
        super().__init__(rpc_url=rpc_url, private_key=private_key)
        self.swapClient = Jupiter(async_client=self.client, keypair=self.wallet)


    async def get_token_mint_account(self, token_mint: str) -> Pubkey:
        print("get_token_mint_account")
        token_mint_account = get_associated_token_address(owner=self.wallet.pubkey(), mint=Pubkey.from_string(token_mint))
        return token_mint_account

    async def get_wallet_token_balance(self,token_mint_address:str):
        """ Get the wallet token balance"""
        print("get_wallet_token_balance")
        if token_mint_address == "So11111111111111111111111111111111111111112":
            sell_token_account_info = await self.get_token_balance(token_mint_account=self.wallet.pubkey().__str__())
        else:
            sell_token_account_info = await self.get_token_balance(token_mint_account=token_mint_address)
        return sell_token_account_info
    
    async def swap_token(self, input_mint:str, output_mint:str, amount, slippage_bps):
        """Swap Token"""
        sell_token_account_info = await self.get_wallet_token_balance(input_mint)
        print(sell_token_account_info)
        swap_data = await self.swapClient.swap(
            input_mint=input_mint,
            output_mint=output_mint,
            amount=int(amount*10**sell_token_account_info["decimals"]),
            slippage_bps=int(slippage_bps*100),
        )
        return (True,await self.sign_send_transaction(swap_data))

        
    async def swap_status(self, transaction_hash):
        """Get The Swap Status"""
        try:
            return await self.get_status_transaction(transaction_hash=transaction_hash) # TBD
        except Exception as e:
            print(e)
            return False


    async def fetch_token_list(self):
        tokens_list = await self.jupiter.get_tokens_list(list_type="all")
        return tokens_list
