# A2A_ETH: Blockchain-Verified Multi-Agent System

Un'architettura sperimentale che combina **Google ADK (Agent Development Kit)** e **Ethereum Blockchain** per creare un ecosistema di agenti AI "fidati".

Il sistema è composto da un **Root Agent** (Orchestratore) che delega compiti a **Sub-Agents remoti** solo dopo aver verificato la loro identità e il loro stato di approvazione ("TRUSTED") su uno Smart Contract Ethereum (Sepolia Testnet).

## ✨ Caratteristiche Principali

* **AI Orchestration:** Utilizza Google Gemini (modelli Flash/Lite) per la gestione del linguaggio naturale e il routing delle richieste.
* **Blockchain Security:** Registro on-chain (Smart Contract Solidity) per gestire la whitelist degli agenti autorizzati.
* **Agent-to-Agent (A2A):** Comunicazione remota tra agenti via protocollo HTTP/ADK.
* **Trust Verification:** Tool personalizzato che interroga la blockchain in tempo reale prima di ogni delega.

---

## 📂 Struttura del Progetto

```text
A2A_ETH/
├── contracts/
│   ├── AgentRegistry.sol       # Smart Contract (Il Registro)
│   └── contract_info.json      # Generato automaticamente dopo il deploy (ABI + Address)
├── remote_a2a/
│   └── check_prime_agent/      # Agente Remoto (Specialista Numeri Primi)
│       ├── agent.py
│       └── agent.json
├── scripts/
│   ├── deploy_registry.py      # Script per deployare il contratto su Sepolia
│   └── register_agent.py       # Script per registrare un agente come "Trusted"
├── tools/
│   └── blockchain_verifier.py  # Logica di verifica on-chain usata dal Root Agent
├── agent.py                    # Root Agent (Orchestratore e interfaccia utente)
└── .env                        # Variabili d'ambiente e chiavi segrete
```

---

## 🛠️ Prerequisiti

* **Python 3.10+**
* **Google Gemini API Key** (per l'intelligenza degli agenti)
* **Infura API Key** (per connettersi a Ethereum Sepolia)
* **MetaMask / Private Key** (per firmare le transazioni di deploy/registrazione)
* **ETH su Sepolia** (per pagare il gas delle transazioni - sono gratuiti tramite faucet)

---

## 🚀 Installazione

1.  **Clona il repository e entra nella cartella:**
    ```bash
    cd A2A_ETH
    ```

2.  **Crea e attiva un virtual environment:**
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Mac/Linux:
    source .venv/bin/activate
    ```

3.  **Installa le dipendenze:**
    ```bash
    pip install google-adk web3 python-dotenv py-solc-x
    pip install google-adk[a2a]
    ```

4.  **Configura il file `.env`:**
    Crea un file `.env` nella root e inserisci le tue chiavi seguendo questo template:

    ```env
    # --- Google AI ---
	GOOGLE_GENAI_USE_VERTEXAI=FALSE
    GOOGLE_API_KEY="la_tua_chiave_gemini"

    # --- Blockchain (Infura & Wallet) ---
    INFURA_URL="[https://sepolia.infura.io/v3/la_tua_infura_key](https://sepolia.infura.io/v3/la_tua_infura_key)"
    DEPLOYER_PRIVATE_KEY="la_tua_chiave_privata_metamask"
    CHAIN_ID="11155111"  # Sepolia ID

    # --- Agenti ---
    # Genera un nuovo address per il tuo agente remoto o usane uno esistente
    AGENT_PRIME_ETH_ADDRESS="0xIndirizzo_Del_Tuo_Prime_Agent"
	AGENT_REGISTRY_ADDRESS="0xIndirizzo_Del_Contratto"
    ```

---

## ⚙️ Utilizzo

Il sistema richiede una sequenza precisa di avvio per garantire che la catena di fiducia sia stabilita.

### Passo 1: Deploy dello Smart Contract
Pubblica il registro sulla blockchain. Eseguire solo una volta.
```bash
python scripts/deploy_registry.py
```
> **Output atteso:** Crea `contracts/contract_info.json` con l'indirizzo del contratto.

### Passo 2: Avvio dell'Agente Remoto (Prime Agent)
Avvia lo specialista matematico sulla porta 8001.
```bash
adk api_server --a2a --port 8001 remote_a2a
```
⚠️ *Lasciare questo terminale aperto.*

### Passo 3: Registrazione On-Chain
Registra l'indirizzo del Prime Agent nel contratto come "TRUSTED".
```bash
python scripts/register_agent.py
```
> **Output atteso:** "SUCCESSO! Agent 0x... è ora TRUSTED on-chain."

### Passo 4: Avvio del Root Agent (Orchestratore)
In un nuovo terminale, avvia l'agente principale che dialoga con l'utente.
```bash
adk run .
```

---

## 🧪 Test del Flusso

Una volta avviato il Root Agent (Passo 4), prova i seguenti prompt:

**1. Task Locale:**
> "Roll a 6-sided die."
* Risposta immediata dal `roll_agent` locale.

**2. Task Remoto + Verifica Blockchain:**
> "Is 5 a prime number?"
* Il Root Agent consulterà lo Smart Contract tramite Infura.
* Se l'agente remoto è "TRUSTED", la richiesta verrà inoltrata.
* L'agente remoto calcolerà e restituirà la risposta.

**3. Task Combinato:**
> "Roll a 100-sided die and check if the result is prime."
* Esegue sequenzialmente il lancio locale, la verifica blockchain e il controllo remoto.

---

## 📝 Note Tecniche

* **Modelli:** Si consiglia di utilizzare `gemini-1.5-flash` o `gemini-flash-latest` in `agent.py` per evitare limiti di rate (errore 429).
* **Routing A2A:** L'URL dell'agente remoto deve includere il percorso completo generato dall'ADK.
  * Esempio: `http://localhost:8001/a2a/check_prime_agent/.well-known/agent-card.json`
