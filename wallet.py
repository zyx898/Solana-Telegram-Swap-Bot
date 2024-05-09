import json
import base58
import base64
from solders import message
from solders.keypair import Keypair # type: ignore
from solders.transaction import VersionedTransaction # type: ignore
from solders.signature import Signature # type: ignore
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed, Finalized
from solana.rpc.types import TxOpts
from solders.pubkey import Pubkey # type: ignore
from spl.token.instructions import get_associated_token_address
from solders.pubkey import Pubkey # type: ignore




class Wallet():
    
    def __init__(self, rpc_url: str, private_key: str):
        self.wallet = Keypair.from_bytes(base58.b58decode(private_key))
        self.client = AsyncClient(endpoint=rpc_url,commitment=Finalized)


    async def get_token_balance(self, token_mint_account: str) -> dict:
        """Get the wallet token balance"""
        if token_mint_account == self.wallet.pubkey().__str__(): #If it is SoL
            get_token_balance = await self.client.get_balance(pubkey=self.wallet.pubkey())
            token_balance = {
                'decimals': 9,
                'balance': {
                    'int': get_token_balance.value,
                    'float': float(get_token_balance.value / 10 ** 9)
                }
            }
        else: #If it is a token
            token_mint_account = get_associated_token_address(owner=self.wallet.pubkey(), mint=Pubkey.from_string(token_mint_account))
            get_token_balance = await self.client.get_token_account_balance(pubkey=token_mint_account)
            try:
                token_balance = {
                    'decimals': int(get_token_balance.value.decimals),
                    'balance': {
                        'int': get_token_balance.value.amount,
                        'float': float(get_token_balance.value.amount) / 10 ** int(get_token_balance.value.decimals)
                    }
                }
            except AttributeError: #If the token account does not exist
                token_balance = {
                    'decimals': 0,
                    'balance': {
                        'int': 0,
                        'float':0
                    }
                }
        
        return token_balance
    
    
    async def sign_send_transaction(self, transaction_data: str, signatures_list: list=None, print_link: bool=True):
        try:
            """Sign and send transaction, return transaction hash"""
            signatures = []
            raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data))
            signature = self.wallet.sign_message(message.to_bytes_versioned(raw_transaction.message))
            signatures.append(signature)
            if signatures_list:
                for signature in signatures_list:
                    signatures.append(signature)
            signed_txn = VersionedTransaction.populate(raw_transaction.message, signatures)
            opts = TxOpts(skip_preflight=True, preflight_commitment=Processed)
            result = await self.client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)
            transaction_hash = json.loads(result.to_json())['result']
            if print_link is True:
                print(f"Transaction sent: https://explorer.solana.com/tx/{transaction_hash}")
            return transaction_hash
        except Exception as e:
            print(e)
            return False

    async def get_status_transaction(self, transaction_hash: str):
        """Get the transaction status"""
        try:
            get_transaction_details = await self.client.confirm_transaction(
                tx_sig=Signature.from_string(transaction_hash),
                sleep_seconds=3,
                last_valid_block_height=json.loads((await self.client.get_latest_blockhash()).to_json())["result"]["value"]["lastValidBlockHeight"],
                commitment=Processed
            )
            transaction_status = get_transaction_details.value[0].err
            
            if transaction_status is None:
                print("Transaction Status SUCCESS!")
                return (True,transaction_status)
            else:
                print(f"!!! Check Transaction Status FAILED!")
                return (False,transaction_status)
        except Exception as e:
            print(e)
            print("Check Transaction Status FAILED!")
            return (False,str(e))