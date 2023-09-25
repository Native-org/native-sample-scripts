const ethers = require("ethers");
const nativePoolAbi = require("../ABIs/nativePool.json");

const rpcMap = {
  ethereum: "https://ethereum.publicnode.com",
  bsc: "https://bsc-dataseed.binance.org",
  bsc_test: "https://data-seed-prebsc-1-s2.binance.org:8545",
};
const chain = "ethereum";
const rpc = rpcMap[chain];
//token address must be updated for every chain
const tokenMap = {
  BANANA: "0x38E68A37E401F7271568CecaAc63c6B1e19130B4",
  WETH: "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
};

const poolAddress = "0x816ecda969E24583E79b71645f1202daBD7fe90e";
// const treasuryAddress = "0x2008b6c3D07B061A84F790C035c2f6dC11A0be70";
const treasuryPrivateKey = "";

const newPairs = [
  {
    tokenA: tokenMap["WETH"],
    tokenB: tokenMap["BANANA"],
    fee: 0,
    pricingModel: 100,
  },
];

async function updatePairs() {
  const provider = new ethers.JsonRpcProvider(rpc);
  const wallet = new ethers.Wallet(treasuryPrivateKey, provider);

  const poolContract = new ethers.Contract(poolAddress, nativePoolAbi).connect(
    wallet
  );

  const fees = newPairs.map((item) => item.fee);
  const tokenAs = newPairs.map((item) => ethers.getAddress(item.tokenA));
  const tokenBs = newPairs.map((item) => ethers.getAddress(item.tokenB));
  const pricingModels = newPairs.map((item) => item.pricingModel);

  const tx = await poolContract.updatePairs(
    fees,
    tokenAs,
    tokenBs,
    pricingModels
  );

  const receipt = await tx.wait();
  console.log("success update pairs: ", receipt);
}

updatePairs();
