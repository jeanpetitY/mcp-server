# TP : Créer et Comprendre un Serveur MCP pour Orchestrer des Outils avec l'IA Générative

## Objectifs du TP

À la fin de ce TP, vous serez capable de :
- Comprendre l'architecture et le rôle d'un serveur MCP (Model Context Protocol)
- Mettre en place un serveur MCP fonctionnel avec FastMCP
- Créer et intégrer de nouveaux outils dans un serveur MCP
- Utiliser l'inspecteur MCP pour tester et déboguer votre serveur
- Comprendre les concepts clés : serveurs, UVM, inspector, assistants, transport protocols

---

## 1. Introduction Théorique (15 minutes)

### 1.1 Qu'est-ce que MCP ?

Le **Model Context Protocol (MCP)** est un standard ouvert qui permet aux assistants IA (comme ChatGPT, Claude, etc.) d'interagir avec des outils externes et des sources de données à travers un protocole unifié.

**Pourquoi MCP est essentiel :**
- Les LLMs ne peuvent pas accéder directement aux APIs ou bases de données
- MCP agit comme intermédiaire sécurisé qui orchestre et normalise les appels
- Fournit une abstraction unifiée pour différents types d'outils

### 1.2 Flux d'interaction

```
LLM/Assistant → MCP Server → Outils externes → MCP Server → LLM/Assistant
```

### 1.3 Concepts Clés

#### **Serveur MCP**
- Point d'entrée central qui expose des outils via le protocole MCP
- Gère l'orchestration, la sécurité et la normalisation des appels
- Peut fonctionner selon différents modes de transport

#### **Transports MCP**
- **stdio** : Communication directe via stdin/stdout (pour intégration locale)
- **http** : Serveur HTTP classique
- **sse** : Server-Sent Events pour communication unidirectionnelle
- **streamable-http** : HTTP avec streaming bidirectionnel (recommandé pour réseau)

#### **FastMCP**
- Framework Python pour créer rapidement des serveurs MCP
- Gère automatiquement la sérialisation/désérialisation JSON
- Fournit des décorateurs simples pour exposer des fonctions comme outils

#### **MCP Inspector**
- Outil de développement pour tester et déboguer les serveurs MCP
- Interface web pour explorer les outils disponibles
- Permet de tester les appels d'outils en temps réel

#### **Namespace et Sub-servers**
- Chaque groupe d'outils est organisé dans un "sub-server" avec son namespace
- Exemple : `sum_add` (namespace "sum", fonction "add")
- Permet une organisation claire des outils

---

## 2. Pré-requis Techniques

### 2.1 Connaissances requises
- Python 3.x (bases)
- Concepts HTTP/REST (bases)
- Utilisation de terminal/ligne de commande

### 2.2 Outils nécessaires
```bash
# Vérifier Python (version 3.14+ recommandée)
python --version

# Installer uv (gestionnaire de packages Python)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 3. Mise en Place du Projet (20 minutes)

### 3.1 Clonage et Installation

```bash
# Cloner le projet
git clone https://gitlab.com/TIBHannover/orkg/tib-aissistant/tib-mcp.git
cd tib-mcp/V3/mcp-server

# Créer l'environnement virtuel et installer les dépendances
uv sync

# Copier le fichier d'environnement
cp .env.example .env
```

### 3.2 Exploration de la Structure du Projet

Examinez l'architecture du projet :

```
mcp-server/
├── main.py                    # Point d'entrée principal
├── server/
│   ├── app.py                # Factory de l'application
│   ├── main.py               # Configuration et lancement
│   ├── core/
│   │   └── config.py         # Gestion de la configuration
│   ├── services/             # Logique métier des outils
│   │   ├── sum.py           # Service de calcul
│   │   └── ...
│   ├── tools/                # Définition des outils MCP
│   │   ├── sum.py           # Outil de calcul
│   │   └── ...
│   └── utils/
│       └── runtime.py       # Helpers d'exécution
├── tests/                    # Suite de tests
├── .env.example             # Configuration par défaut
└── pyproject.toml           # Dépendances et configuration
```

---

## 4. Lancement et Test du Serveur (25 minutes)

### 4.1 Démarrage du Serveur

```bash
# Mode streamable-http (par défaut)
uv run python main.py
```

Le serveur démarre sur `http://127.0.0.1:8000/mcp`

### 4.2 Test avec l'Inspecteur MCP

#### Option 1 : Serveur déjà démarré
```bash
# Dans un autre terminal
npx @modelcontextprotocol/inspector
```
Puis connectez-vous à `http://127.0.0.1:8000/mcp`

#### Option 2 : Lancement direct
```bash
npx @modelcontextprotocol/inspector uv run python main.py
```

### 4.3 Exploration des Outils Disponibles

Dans l'inspecteur, vous devriez voir les outils :
- `sum_add` : Additionne deux nombres
- `core_*` : Outils de base
- `crossref_*` : Recherche CrossRef
- `orcid_*` : Recherche ORCID
- `semantic_scholar_*` : Recherche Semantic Scholar

### 4.4 Test d'un Outil

Testez l'outil `sum_add` :
```json
{
  "name": "sum_add",
  "arguments": {
    "a": 5.5,
    "b": 3.2
  }
}
```

Résultat attendu :
```json
{
  "content": [
    {
      "type": "text",
      "text": "8.7"
    }
  ]
}
```

---

## 5. Analyse du Code Existant (20 minutes)

### 5.1 Structure d'un Outil MCP

Examinez `server/tools/sum.py` :

```python
from fastmcp import FastMCP
from server.services import SumService

# Création du sub-server avec son namespace
server = FastMCP("sum")
sum_service = SumService()

# Décoration d'une fonction comme outil MCP
@server.tool()
def add(a: float, b: float) -> float:
    """Add two numbers and return the result.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The sum of a and b.
    """
    return sum_service.add(a, b)
```

### 5.2 Pattern Service-Séparation

Examinez `server/services/sum.py` :

```python
class SumService:
    """Starter for Sum Service."""

    def add(self, a: float, b: float) -> float:
        return a + b
```

**Avantages de cette séparation :**
- Logique métier réutilisable en dehors de MCP
- Tests unitaires plus simples
- Architecture claire et maintenable

### 5.3 Configuration et Transport

Examinez `server/core/config.py` pour comprendre :
- La gestion des variables d'environnement
- La normalisation des transports
- Les valeurs par défaut

---

## 6. Création d'un Nouvel Outil (30 minutes)

### 6.1 Objectif

Créer un outil `calculator` avec les fonctions :
- `multiply` : Multiplier deux nombres
- `divide` : Diviser deux nombres
- `power` : Calculer la puissance

### 6.2 Étape 1 : Créer le Service

Créez `server/services/calculator.py` :

```python
class CalculatorService:
    """Calculator service for basic arithmetic operations."""

    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        return a * b

    def divide(self, a: float, b: float) -> float:
        """Divide two numbers."""
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        return a / b

    def power(self, base: float, exponent: float) -> float:
        """Calculate base to the power of exponent."""
        return base ** exponent
```

### 6.3 Étape 2 : Exporter le Service

Modifiez `server/services/__init__.py` :

```python
from server.services.calculator import CalculatorService
from server.services.sum import SumService

__all__ = ["CalculatorService", "SumService"]
```

### 6.4 Étape 4 : Créer l'Outil MCP

Créez `server/tools/calculator.py` :

```python
from fastmcp import FastMCP
from server.services import CalculatorService

server = FastMCP("calculator")
calculator_service = CalculatorService()

@server.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers and return the result.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The product of a and b.
    """
    return calculator_service.multiply(a, b)

@server.tool()
def divide(a: float, b: float) -> float:
    """Divide two numbers and return the result.

    Args:
        a: The dividend.
        b: The divisor.

    Returns:
        The result of a divided by b.

    Raises:
        ValueError: If b is zero.
    """
    return calculator_service.divide(a, b)

@server.tool()
def power(base: float, exponent: float) -> float:
    """Calculate base to the power of exponent.

    Args:
        base: The base number.
        exponent: The exponent.

    Returns:
        Base raised to the power of exponent.
    """
    return calculator_service.power(base, exponent)
```

### 6.5 Étape 5 : Monter l'Outil

Modifiez `server/tools/__init__.py` :

```python
from fastmcp import FastMCP
from server.tools.calculator import server as calculator_server
from server.tools.sum import server as sum_server
# ... autres imports

def register_tools(app: FastMCP) -> None:
    app.mount(sum_server, namespace="sum")
    app.mount(calculator_server, namespace="calculator")
    # ... autres montages
```

### 6.6 Étape 6 : Tester

Redémarrez le serveur et testez avec l'inspecteur :

```bash
uv run python main.py
```

Testez les nouveaux outils :
- `calculator_multiply`
- `calculator_divide`
- `calculator_power`

---

## 7. Tests Unitaires (15 minutes)

### 7.1 Créer les Tests

Créez `tests/tools/test_calculator.py` :

```python
import pytest
from server.services import CalculatorService

class TestCalculatorService:
    def test_multiply(self):
        service = CalculatorService()
        assert service.multiply(3, 4) == 12
        assert service.multiply(-2, 5) == -10

    def test_divide(self):
        service = CalculatorService()
        assert service.divide(10, 2) == 5
        assert service.divide(-6, 3) == -2

    def test_divide_by_zero(self):
        service = CalculatorService()
        with pytest.raises(ValueError, match="Division by zero"):
            service.divide(5, 0)

    def test_power(self):
        service = CalculatorService()
        assert service.power(2, 3) == 8
        assert service.power(9, 0.5) == 3
```

### 7.2 Lancer les Tests

```bash
# Tests de l'outil calculator
uv run pytest tests/tools/test_calculator.py -v

# Tous les tests
uv run pytest -v
```

---

## 8. Configuration Avancée (10 minutes)

### 8.1 Modes de Transport

Testez différents modes de transport :

```bash
# Mode stdio (pour intégration avec Claude Desktop)
MCP_TRANSPORT=stdio uv run python main.py

# Mode HTTP classique
MCP_TRANSPORT=http uv run python main.py

# Mode SSE
MCP_TRANSPORT=sse uv run python main.py
```

### 8.2 Configuration Personnalisée

Modifiez `.env` pour personnaliser :

```bash
# Personnaliser le nom du serveur
MCP_SERVER_NAME="Mon Serveur MCP"

# Changer le port
MCP_PORT=8080

# Activer le debug
MCP_LOG_LEVEL=DEBUG
```

---

## 9. Intégration avec des Assistants IA (10 minutes)

### 9.1 Configuration Claude Desktop

Configurez votre serveur dans Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`) :

```json
{
  "mcpServers": {
    "tib-mcp": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "/chemin/vers/tib-mcp/V3/mcp-server"
    }
  }
}
```

### 9.2 Configuration VS Code avec Copilot

Dans les settings VS Code :

```json
{
  "github.copilot.chat.experimental.mcpServers": {
    "tib-mcp": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "/chemin/vers/tib-mcp/V3/mcp-server"
    }
  }
}
```

---

## 10. Déploiement et Production (15 minutes)

### 10.1 Dockerisation

Le projet inclut déjà un `Dockerfile` :

```bash
# Construire l'image
docker build -t tib-mcp .

# Lancer le conteneur
docker run -p 8000:8000 tib-mcp
```

### 10.2 Configuration Production

Pour la production, utilisez :

```bash
# Variables d'environnement de production
export MCP_HOST=0.0.0.0
export MCP_LOG_LEVEL=WARNING
export MCP_SERVER_NAME="TIB MCP Production"

# Lancement
uv run python main.py
```

---

## 11. Exercices Supplémentaires (optionnel)

### 11.1 Outil de Traitement de Texte

Créez un outil `text` avec les fonctions :
- `count_words` : Compter les mots dans un texte
- `reverse_text` : Inverser un texte
- `to_uppercase` : Mettre en majuscules

### 11.2 Outil de Conversion

Créez un outil `convert` avec les fonctions :
- `celsius_to_fahrenheit` : Conversion de température
- `km_to_miles` : Conversion de distance
- `kg_to_lbs` : Conversion de poids

### 11.3 Intégration API Externe

Créez un outil qui appelle une API externe (ex: API météo, API de citation).

---

## 12. Conclusion et Discussion (10 minutes)

### 12.1 Points Clés Retenus

- **MCP** standardise la communication entre IA et outils externes
- **FastMCP** simplifie la création de serveurs MCP en Python
- L'architecture **service-séparation** assure une meilleure maintenabilité
- Les **transports** flexibles permettent différents cas d'usage
- L'**inspecteur MCP** est essentiel pour le développement et le débogage

### 12.2 Applications Réelles

- Assistants de recherche académique
- Outils d'analyse de données
- Automatisation de workflows
- Intégration avec des systèmes existants

### 12.3 Défis et Perspectives

- **Sécurité** : Gestion des authentifications et autorisations
- **Performance** : Optimisation des appels et mise en cache
- **Scalabilité** : Gestion de multiples utilisateurs et requêtes
- **Observabilité** : Logging, métriques et monitoring

---

## Ressources Complémentaires

- [Documentation officielle MCP](https://modelcontextprotocol.io/)
- [FastMCP](https://gofastmcp.com/)
- [Projet sur GitLab](https://gitlab.com/TIBHannover/orkg/tib-aissistant/tib-mcp)
- [MCP Inspector](https://www.npmjs.com/package/@modelcontextprotocol/inspector)

---

## Checklist de Validation

- [ ] Serveur MCP démarré avec succès
- [ ] Outils existants testés avec l'inspecteur
- [ ] Nouvel outil `calculator` créé et fonctionnel
- [ ] Tests unitaires écrits et passants
- [ ] Configuration personnalisée testée
- [ ] Documentation comprise et expliquée

---

**Durée estimée totale : 3 heures**

**Niveau de difficulté : Intermédiaire**

**Prérequis : Python 3.x, concepts HTTP/REST**
