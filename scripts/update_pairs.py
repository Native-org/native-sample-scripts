import os
import asyncio
import json
from decimal import Decimal
from web3 import AsyncHTTPProvider, Web3
from web3.eth import AsyncEth
from web3.net import AsyncNet
from web3.middleware import async_geth_poa_middleware
from async_web3_helper import constructAsyncSignAndSendRawMiddleware

# Async calls to give allowance to pool address
# Enter treasuryAddress and private key
# Change ABI path if neccessary

ownerAddress = "OWNER_ADDRESS_HERE"
privateKey = "OWNER_PRIVATE_KEY_HERE"
poolAddress = "POOL_ADDRESS_HERE"

provider = "https://ethereum.publicnode.com"

tokens = {
    "SNX": "0xc011a73ee8576fb46f5e1c5751ca3b9fe0af2a6f",
    "BIGTIME": "0x64Bc2cA1Be492bE7185FAA2c8835d9b824c8a194",
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
}

# for PMM, put fee as 0 and pricingModel as 100
pairs = [
    {
        "tokenA": tokens["SNX"],
        "tokenB": tokens["USDT"],
        "fee": 0,
        "pricingModel": 100,
    },
    {
        "tokenA": tokens["SNX"],
        "tokenB": tokens["USDC"],
        "fee": 0,
        "pricingModel": 100,
    },
    {
        "tokenA": tokens["SNX"],
        "tokenB": tokens["WETH"],
        "fee": 0,
        "pricingModel": 100,
    },
    {
        "tokenA": tokens["BIGTIME"],
        "tokenB": tokens["USDT"],
        "fee": 0,
        "pricingModel": 100,
    },
    {
        "tokenA": tokens["BIGTIME"],
        "tokenB": tokens["USDC"],
        "fee": 0,
        "pricingModel": 100,
    },
    {
        "tokenA": tokens["BIGTIME"],
        "tokenB": tokens["WETH"],
        "fee": 0,
        "pricingModel": 100,
    },
]


def loadAbi(name: str):
    root_path = os.path.abspath(__file__ + "../../../")
    path = os.path.join(root_path, "app/common/abi/", name + ".json")
    with open(path) as json_file:
        json_data = json.load(json_file)
        return json_data


async def loadContract(web3: Web3, contractAddress: str, abiName: str):
    address = web3.to_checksum_address(contractAddress)
    abi = loadAbi(abiName)
    return web3.eth.contract(address=address, abi=abi)


async def getPoolContract(web3: Web3, tokenAddress: str):
    return await loadContract(web3, tokenAddress, "Pool")


async def updatePairs():
    web3 = Web3(
        AsyncHTTPProvider(provider),
        modules={"eth": AsyncEth, "net": AsyncNet},
        middlewares=[],
    )
    web3.middleware_onion.inject(async_geth_poa_middleware, layer=0)
    web3.middleware_onion.add(constructAsyncSignAndSendRawMiddleware(privateKey))

    poolContract = await getPoolContract(web3, web3.to_checksum_address(poolAddress))

    tx = {
        "chainId": await web3.eth.chain_id,
        "from": web3.to_checksum_address(ownerAddress),
        "nonce": await web3.eth.get_transaction_count(ownerAddress),
        "gasPrice": await web3.eth.gas_price,
        "gas": 800000,
    }

    fees = [pair["fee"] for pair in pairs]
    tokenAs = [web3.to_checksum_address(pair["tokenA"]) for pair in pairs]
    tokenBs = [web3.to_checksum_address(pair["tokenB"]) for pair in pairs]
    pricingModels = [pair["pricingModel"] for pair in pairs]

    # return

    sendTx = await poolContract.functions.updatePairs(
        fees, tokenAs, tokenBs, pricingModels
    ).transact(tx)
    txReceipt = await web3.eth.wait_for_transaction_receipt(sendTx)
    return txReceipt


def main():
    loop = asyncio.get_event_loop()

    tasks = [updatePairs()]

    caroutines = asyncio.gather(*tasks)
    result = loop.run_until_complete(caroutines)

    loop.close()

    print("RESULT:", result)


main()
