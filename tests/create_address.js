var api =  require('@cityofzion/neon-js');

wallet = api.wallet;

let numberOfWallets = 100; //replace 100 with the number of wallets you want to create

console.log("Generating " + numberOfWallets + " addresses");

for (let i = 0; i < numberOfWallets; i++) {
    const privateKey = wallet.generatePrivateKey();
    const publicKey = wallet.getPublicKeyFromPrivateKey(privateKey);
    const scriptHash = wallet.getScriptHashFromPublicKey(publicKey);
    const address = wallet.getAddressFromScriptHash(scriptHash);
    console.log(address);
}; 
